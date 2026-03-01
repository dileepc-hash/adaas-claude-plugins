#!/usr/bin/env python3
"""
Script to generate a health report for an ADaaS connector repo.
Checks SDK version, npm audit, and Snyk CLI for vulnerabilities.
"""

import argparse
import json
import os
import subprocess
import sys
import urllib.request
import urllib.error
from datetime import datetime
from typing import Optional, Tuple


def run_command(args: list[str], cwd: str) -> tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr."""
    try:
        result = subprocess.run(
            args,
            cwd=cwd,
            capture_output=True,
            text=True
        )
        return result.returncode, result.stdout, result.stderr
    except FileNotFoundError:
        return -1, "", f"Command not found: {args[0]}"


def get_current_branch(repo_path: str) -> Optional[str]:
    """Get the current git branch name. Returns None if not a git repo or on error."""
    if not os.path.exists(os.path.join(repo_path, ".git")):
        return None
    exit_code, stdout, stderr = run_command(["git", "branch", "--show-current"], repo_path)
    if exit_code != 0:
        return None
    branch = (stdout or "").strip()
    return branch if branch else None


def sync_main_branch(repo_path: str) -> bool:
    """
    Sync the main branch: if not on main, stash changes, checkout main, pull;
    if on main, just pull. Returns True on success, False on failure.
    """
    current = get_current_branch(repo_path)
    if current is None:
        print("  Not a git repository or could not determine branch; skipping sync.")
        return True  # Continue with scan

    # Resolve main branch name (main or master)
    exit_code, _, _ = run_command(["git", "rev-parse", "--verify", "main"], repo_path)
    main_branch = "main" if exit_code == 0 else "master"
    exit_code_master, _, _ = run_command(["git", "rev-parse", "--verify", "master"], repo_path)
    if main_branch == "master" and exit_code_master != 0:
        print("  No 'main' or 'master' branch found; skipping sync.")
        return True

    if current != main_branch:
        print(f"  Current branch: {current}. Syncing to {main_branch}...")
        # Check for uncommitted changes
        exit_code, status_out, _ = run_command(["git", "status", "--porcelain"], repo_path)
        if exit_code == 0 and status_out.strip():
            print("  Stashing uncommitted changes...")
            exit_code, _, stderr = run_command(
                ["git", "stash", "push", "-m", "Auto-stash before health check"],
                repo_path,
            )
            if exit_code != 0:
                print(f"  Warning: stash failed: {stderr.strip()}; continuing without stash.")
        exit_code, _, stderr = run_command(["git", "checkout", main_branch], repo_path)
        if exit_code != 0:
            print(f"  Error: checkout to {main_branch} failed: {stderr.strip()}")
            return False
        print(f"  Checked out {main_branch}.")
    else:
        print(f"  Already on {main_branch}. Pulling latest...")

    exit_code, stdout, stderr = run_command(["git", "pull", "origin", main_branch], repo_path)
    if exit_code != 0:
        print(f"  Warning: pull failed: {stderr.strip() or stdout.strip()}; continuing with current state.")
        return True  # Continue with scan
    print("  Main branch synced.")
    return True


def fetch_latest_sdk_version(package_name: str = "@devrev/ts-adaas") -> Tuple[Optional[str], Optional[str]]:
    """Fetch the latest version of the SDK from npm registry.
    
    Returns:
        Tuple of (latest_version, error_message). If successful, error is None.
    """
    # URL encode the package name (@ -> %40, / -> %2F)
    encoded_name = package_name.replace("@", "%40").replace("/", "%2F")
    url = f"https://registry.npmjs.org/{encoded_name}/latest"
    
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            return data.get("version"), None
    except urllib.error.HTTPError as e:
        return None, f"HTTP error fetching SDK version: {e.code}"
    except urllib.error.URLError as e:
        return None, f"Network error fetching SDK version: {e.reason}"
    except json.JSONDecodeError:
        return None, "Failed to parse npm registry response"
    except Exception as e:
        return None, f"Error fetching SDK version: {str(e)}"


def get_current_sdk_version(repo_path: str, package_name: str = "@devrev/ts-adaas") -> Tuple[Optional[str], Optional[str]]:
    """Get the current SDK version from package.json.
    
    Returns:
        Tuple of (current_version, error_message). If successful, error is None.
    """
    package_json_path = os.path.join(repo_path, "package.json")
    
    if not os.path.exists(package_json_path):
        return None, "package.json not found"
    
    try:
        with open(package_json_path, "r") as f:
            data = json.load(f)
        
        # Check both dependencies and devDependencies
        dependencies = data.get("dependencies", {})
        dev_dependencies = data.get("devDependencies", {})
        
        version = dependencies.get(package_name) or dev_dependencies.get(package_name)
        
        if not version:
            return None, f"{package_name} not found in dependencies"
        
        # Strip any version prefixes like ^, ~, >=, etc.
        clean_version = version.lstrip("^~>=<")
        return clean_version, None
        
    except json.JSONDecodeError:
        return None, "Failed to parse package.json"
    except Exception as e:
        return None, f"Error reading package.json: {str(e)}"


def compare_versions(current: str, latest: str) -> bool:
    """Compare version strings. Returns True if current is older than latest."""
    def parse_version(v: str) -> list:
        """Parse version string into comparable list of integers."""
        # Handle versions like "0.0.25" or "1.2.3-beta.1"
        base_version = v.split("-")[0]  # Remove prerelease suffix
        try:
            return [int(x) for x in base_version.split(".")]
        except ValueError:
            return [0, 0, 0]
    
    current_parts = parse_version(current)
    latest_parts = parse_version(latest)
    
    # Pad shorter version with zeros
    max_len = max(len(current_parts), len(latest_parts))
    current_parts.extend([0] * (max_len - len(current_parts)))
    latest_parts.extend([0] * (max_len - len(latest_parts)))
    
    return current_parts < latest_parts


def check_sdk_version(repo_path: str) -> dict:
    """Check if the SDK version is up to date.
    
    Returns dict with:
        - current_version: installed version (or None)
        - latest_version: latest available version (or None)
        - update_required: bool indicating if update is needed
        - error: error message if any
    """
    print("  Checking @devrev/ts-adaas SDK version...")
    
    result = {
        "current_version": None,
        "latest_version": None,
        "update_required": False,
        "error": None
    }
    
    # Get current version
    current_version, current_error = get_current_sdk_version(repo_path)
    if current_error:
        result["error"] = current_error
        return result
    result["current_version"] = current_version
    
    # Get latest version
    latest_version, latest_error = fetch_latest_sdk_version()
    if latest_error:
        result["error"] = latest_error
        return result
    result["latest_version"] = latest_version
    
    # Compare versions
    if current_version and latest_version:
        result["update_required"] = compare_versions(current_version, latest_version)
    
    return result


def run_npm_audit(repo_path: str) -> dict:
    """Run npm audit and return parsed results."""
    print("  Running npm audit...")
    
    # First ensure node_modules exists
    if not os.path.exists(os.path.join(repo_path, "node_modules")):
        print("  Installing dependencies first (npm install)...")
        run_command(["npm", "install"], repo_path)
    
    exit_code, stdout, stderr = run_command(["npm", "audit", "--json"], repo_path)
    
    if exit_code == -1:
        return {"error": stderr, "vulnerabilities": {}}
    
    try:
        data = json.loads(stdout) if stdout else {}
        return data
    except json.JSONDecodeError:
        return {"error": "Failed to parse npm audit output", "vulnerabilities": {}}


def run_snyk_test(repo_path: str) -> dict:
    """Run snyk test and return parsed results."""
    print("  Running snyk test (dependencies)...")
    
    exit_code, stdout, stderr = run_command(["snyk", "test", "--json"], repo_path)
    
    if exit_code == -1:
        return {"error": stderr, "vulnerabilities": []}
    
    try:
        data = json.loads(stdout) if stdout else {}
        return data
    except json.JSONDecodeError:
        return {"error": "Failed to parse snyk output", "vulnerabilities": []}


def run_snyk_code_test(repo_path: str) -> dict:
    """Run snyk code test for source code vulnerabilities (SAST)."""
    print("  Running snyk code test (source code)...")
    
    exit_code, stdout, stderr = run_command(["snyk", "code", "test", "--json"], repo_path)
    
    if exit_code == -1:
        return {"error": stderr, "runs": []}
    
    try:
        data = json.loads(stdout) if stdout else {}
        return data
    except json.JSONDecodeError:
        return {"error": "Failed to parse snyk code output", "runs": []}


def parse_npm_audit(data: dict) -> dict:
    """Parse npm audit data into a summary."""
    if "error" in data and data["error"]:
        return {"error": data["error"], "summary": {}, "details": []}
    
    # npm audit format varies by version
    vulnerabilities = data.get("vulnerabilities", {})
    metadata = data.get("metadata", {})
    
    summary = {
        "critical": 0,
        "high": 0,
        "moderate": 0,
        "low": 0,
        "info": 0,
        "total": 0
    }
    
    # Try to get summary from metadata first
    if metadata and "vulnerabilities" in metadata:
        vuln_meta = metadata["vulnerabilities"]
        summary["critical"] = vuln_meta.get("critical", 0)
        summary["high"] = vuln_meta.get("high", 0)
        summary["moderate"] = vuln_meta.get("moderate", 0)
        summary["low"] = vuln_meta.get("low", 0)
        summary["info"] = vuln_meta.get("info", 0)
        summary["total"] = vuln_meta.get("total", 0)
    else:
        # Count from vulnerabilities
        for name, vuln in vulnerabilities.items():
            severity = vuln.get("severity", "low").lower()
            if severity in summary:
                summary[severity] += 1
            summary["total"] += 1
    
    # Extract details
    details = []
    for name, vuln in vulnerabilities.items():
        details.append({
            "package": name,
            "severity": vuln.get("severity", "unknown"),
            "via": vuln.get("via", []),
            "fixAvailable": vuln.get("fixAvailable", False)
        })
    
    return {"summary": summary, "details": details}


def parse_snyk_results(data: dict) -> dict:
    """Parse Snyk test results into a summary."""
    if "error" in data and data["error"]:
        return {"error": data["error"], "summary": {}, "details": []}
    
    vulnerabilities = data.get("vulnerabilities", [])
    
    summary = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "total": len(vulnerabilities)
    }
    
    details = []
    for vuln in vulnerabilities:
        severity = vuln.get("severity", "low").lower()
        if severity in summary:
            summary[severity] += 1
        
        details.append({
            "package": vuln.get("packageName", "unknown"),
            "severity": severity,
            "title": vuln.get("title", ""),
            "version": vuln.get("version", ""),
            "fixedIn": vuln.get("fixedIn", [])
        })
    
    return {"summary": summary, "details": details}


def parse_snyk_code_results(data: dict) -> dict:
    """Parse Snyk code test results (SARIF format) into a summary."""
    if "error" in data and data["error"]:
        return {"error": data["error"], "summary": {}, "details": []}
    
    # Directories to exclude from results
    excluded_dirs = ["node_modules/", "dist/", "build/", ".git/"]
    
    summary = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "total": 0
    }
    
    details = []
    
    # Snyk code output is in SARIF format
    runs = data.get("runs", [])
    for run in runs:
        results = run.get("results", [])
        for result in results:
            # Get location info first to check if we should skip
            locations = result.get("locations", [])
            file_path = ""
            line_num = ""
            if locations:
                phys_loc = locations[0].get("physicalLocation", {})
                artifact = phys_loc.get("artifactLocation", {})
                file_path = artifact.get("uri", "unknown")
                region = phys_loc.get("region", {})
                line_num = region.get("startLine", "")
            
            # Skip files in excluded directories
            if any(excluded in file_path for excluded in excluded_dirs):
                continue
            
            # Get severity from level (error=high, warning=medium, note=low)
            level = result.get("level", "note").lower()
            if level == "error":
                severity = "high"
            elif level == "warning":
                severity = "medium"
            else:
                severity = "low"
            
            # Try to get severity from properties if available
            properties = result.get("properties", {})
            if "priorityScore" in properties:
                score = properties["priorityScore"]
                if score >= 800:
                    severity = "critical"
                elif score >= 600:
                    severity = "high"
                elif score >= 400:
                    severity = "medium"
                else:
                    severity = "low"
            
            if severity in summary:
                summary[severity] += 1
            summary["total"] += 1
            
            details.append({
                "rule": result.get("ruleId", "unknown"),
                "severity": severity,
                "message": result.get("message", {}).get("text", "")[:80],
                "file": file_path,
                "line": line_num
            })
    
    return {"summary": summary, "details": details}


def generate_markdown_report(repo_name: str, npm_results: dict, snyk_results: dict, snyk_code_results: dict, sdk_version_check: dict = None) -> str:
    """Generate a markdown health report."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report = f"""# ADaaS Connector Health Report

**Repository:** {repo_name}  
**Generated:** {timestamp}

---

## Summary

"""
    
    # SDK Version Check section (if provided)
    if sdk_version_check:
        report += "### SDK Version Check (@devrev/ts-adaas)\n\n"
        if sdk_version_check.get("error"):
            report += f"**Warning:** {sdk_version_check['error']}\n\n"
        else:
            current = sdk_version_check.get("current_version", "N/A")
            latest = sdk_version_check.get("latest_version", "N/A")
            update_required = sdk_version_check.get("update_required", False)
            
            report += f"| Property | Value |\n"
            report += f"|----------|-------|\n"
            report += f"| Current Version | {current} |\n"
            report += f"| Latest Version | {latest} |\n"
            
            if update_required:
                report += f"| **Status** | **⚠️ UPDATE REQUIRED** |\n\n"
                report += f"> **Action Required:** Please update `@devrev/ts-adaas` from version `{current}` to `{latest}` in your package.json.\n\n"
            else:
                report += f"| Status | ✓ Up to date |\n\n"
    
    # npm audit summary
    report += "### npm audit (Dependencies)\n\n"
    if "error" in npm_results and npm_results["error"]:
        report += f"**Error:** {npm_results['error']}\n\n"
    else:
        npm_summary = npm_results.get("summary", {})
        report += f"| Severity | Count |\n"
        report += f"|----------|-------|\n"
        report += f"| Critical | {npm_summary.get('critical', 0)} |\n"
        report += f"| High | {npm_summary.get('high', 0)} |\n"
        report += f"| Moderate | {npm_summary.get('moderate', 0)} |\n"
        report += f"| Low | {npm_summary.get('low', 0)} |\n"
        report += f"| **Total** | **{npm_summary.get('total', 0)}** |\n\n"
    
    # Snyk dependencies summary
    report += "### Snyk (Dependencies)\n\n"
    if "error" in snyk_results and snyk_results["error"]:
        report += f"**Error:** {snyk_results['error']}\n\n"
    else:
        snyk_summary = snyk_results.get("summary", {})
        report += f"| Severity | Count |\n"
        report += f"|----------|-------|\n"
        report += f"| Critical | {snyk_summary.get('critical', 0)} |\n"
        report += f"| High | {snyk_summary.get('high', 0)} |\n"
        report += f"| Medium | {snyk_summary.get('medium', 0)} |\n"
        report += f"| Low | {snyk_summary.get('low', 0)} |\n"
        report += f"| **Total** | **{snyk_summary.get('total', 0)}** |\n\n"
    
    # Snyk Code summary
    report += "### Snyk Code (Source Code - SAST)\n\n"
    if "error" in snyk_code_results and snyk_code_results["error"]:
        report += f"**Error:** {snyk_code_results['error']}\n\n"
    else:
        code_summary = snyk_code_results.get("summary", {})
        report += f"| Severity | Count |\n"
        report += f"|----------|-------|\n"
        report += f"| Critical | {code_summary.get('critical', 0)} |\n"
        report += f"| High | {code_summary.get('high', 0)} |\n"
        report += f"| Medium | {code_summary.get('medium', 0)} |\n"
        report += f"| Low | {code_summary.get('low', 0)} |\n"
        report += f"| **Total** | **{code_summary.get('total', 0)}** |\n\n"
    
    report += "---\n\n"
    
    # npm audit details
    report += "## npm audit Details\n\n"
    npm_details = npm_results.get("details", [])
    if npm_details:
        report += "| Package | Severity | Fix Available |\n"
        report += "|---------|----------|---------------|\n"
        for vuln in npm_details:
            fix = "Yes" if vuln.get("fixAvailable") else "No"
            report += f"| {vuln['package']} | {vuln['severity']} | {fix} |\n"
        report += "\n"
    else:
        report += "No vulnerabilities found.\n\n"
    
    # Snyk dependencies details
    report += "## Snyk (Dependencies) Details\n\n"
    snyk_details = snyk_results.get("details", [])
    if snyk_details:
        report += "| Package | Version | Severity | Title | Fixed In |\n"
        report += "|---------|---------|----------|-------|----------|\n"
        for vuln in snyk_details:
            fixed_in = ", ".join(vuln.get("fixedIn", [])) or "N/A"
            title = vuln.get("title", "")[:50]  # Truncate long titles
            report += f"| {vuln['package']} | {vuln['version']} | {vuln['severity']} | {title} | {fixed_in} |\n"
        report += "\n"
    else:
        report += "No vulnerabilities found.\n\n"
    
    # Snyk Code details
    report += "## Snyk Code (Source Code) Details\n\n"
    code_details = snyk_code_results.get("details", [])
    if code_details:
        report += "| Rule | Severity | File | Line | Message |\n"
        report += "|------|----------|------|------|--------|\n"
        for issue in code_details:
            file_path = issue.get("file", "")
            # Truncate long file paths
            if len(file_path) > 40:
                file_path = "..." + file_path[-37:]
            message = issue.get("message", "")[:40]
            report += f"| {issue['rule']} | {issue['severity']} | {file_path} | {issue['line']} | {message} |\n"
        report += "\n"
    else:
        report += "No code vulnerabilities found.\n\n"
    
    report += "---\n\n"
    report += "*Report generated by adaas_health.py*\n"
    
    return report


def find_package_json_dir(repo_path: str) -> Optional[str]:
    """Find directory containing package.json, checking root then code/ subdir."""
    # Check root first
    if os.path.exists(os.path.join(repo_path, "package.json")):
        return repo_path
    
    # Check code/ subdirectory (standard connector structure)
    code_path = os.path.join(repo_path, "code")
    if os.path.exists(os.path.join(code_path, "package.json")):
        return code_path
    
    return None


def generate_report(repo_path: str, output_dir: str, sync_main: bool = True) -> None:
    """Generate a health report for the given repository."""
    repo_path = os.path.abspath(repo_path)
    output_dir = os.path.abspath(output_dir)
    repo_name = os.path.basename(repo_path)
    
    print(f"\nGenerating health report for: {repo_name}")
    print(f"  Path: {repo_path}")
    
    if sync_main:
        print("  Syncing main branch...")
        if not sync_main_branch(repo_path):
            print("  Sync failed; aborting.")
            sys.exit(1)
    
    # Find directory containing package.json
    pkg_dir = find_package_json_dir(repo_path)
    if not pkg_dir:
        print(f"  Error: package.json not found in {repo_path} or its subdirectories")
        sys.exit(1)
    
    if pkg_dir != repo_path:
        print(f"  Found package.json in: {os.path.relpath(pkg_dir, repo_path)}/")
    
    scan_path = pkg_dir
    
    # Run npm audit
    npm_data = run_npm_audit(scan_path)
    npm_results = parse_npm_audit(npm_data)
    
    # Run snyk test (dependencies)
    snyk_data = run_snyk_test(scan_path)
    snyk_results = parse_snyk_results(snyk_data)
    
    # Run snyk code test (source code SAST)
    snyk_code_data = run_snyk_code_test(scan_path)
    snyk_code_results = parse_snyk_code_results(snyk_code_data)
    
    # Check SDK version
    sdk_version_check = check_sdk_version(scan_path)
    
    # Generate report
    print("  Generating markdown report...")
    report = generate_markdown_report(repo_name, npm_results, snyk_results, snyk_code_results, sdk_version_check)
    
    # Save report to output_dir/[connector-repo-name]/report_timestamp.md
    report_dir = os.path.join(output_dir, repo_name)
    os.makedirs(report_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"report_{timestamp}.md"
    report_path = os.path.join(report_dir, report_filename)
    
    with open(report_path, "w") as f:
        f.write(report)
    
    print(f"  Report saved to: {report_path}")
    
    # Print summary to console
    npm_summary = npm_results.get("summary", {})
    snyk_summary = snyk_results.get("summary", {})
    snyk_code_summary = snyk_code_results.get("summary", {})
    
    print(f"\n  Summary:")
    print(f"    npm audit (dependencies): {npm_summary.get('total', 0)} vulnerabilities")
    print(f"    Snyk (dependencies): {snyk_summary.get('total', 0)} vulnerabilities")
    print(f"    Snyk Code (source code): {snyk_code_summary.get('total', 0)} issues")
    
    # Print SDK version check summary
    if sdk_version_check.get("error"):
        print(f"    SDK version check: {sdk_version_check['error']}")
    elif sdk_version_check.get("update_required"):
        print(f"    SDK version check: UPDATE REQUIRED ({sdk_version_check['current_version']} -> {sdk_version_check['latest_version']})")
    else:
        print(f"    SDK version check: Up to date ({sdk_version_check.get('current_version', 'N/A')})")


def main():
    parser = argparse.ArgumentParser(
        description="Generate a health report for an ADaaS connector repo."
    )
    parser.add_argument(
        "repo",
        help="Path to the connector repo to scan"
    )
    parser.add_argument(
        "output",
        nargs="?",
        default='/Users/dileepbc/code-base/platform/connectors/security_reports',
        help="Folder path to save the security report (default: full path of ./reports)"
    )
    parser.add_argument(
        "--no-sync-main",
        dest="sync_main",
        action="store_false",
        default=True,
        help="Skip syncing main branch before scanning (default: sync main)"
    )
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.repo):
        print(f"Error: '{args.repo}' is not a directory")
        sys.exit(1)
    
    generate_report(args.repo, args.output, sync_main=args.sync_main)
    print("\nDone!")


if __name__ == "__main__":
    main()
