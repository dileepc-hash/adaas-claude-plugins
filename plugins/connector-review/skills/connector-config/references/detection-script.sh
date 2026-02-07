#!/bin/bash

# Code Quality Detection Script for DevRev Connectors
# Validates: package.json, tsconfig.json, ESLint configuration
# Usage: ./detection-script.sh [connector-root-path]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
TOTAL_CHECKS=6
FAILED_CHECKS=0

# Default to current directory if no argument provided
CONNECTOR_ROOT="${1:-.}"

echo "=================================================="
echo "Code Quality Validation for DevRev Connectors"
echo "=================================================="
echo ""
echo "Connector Root: $CONNECTOR_ROOT"
echo ""

# Helper function to check if jq is installed
check_jq() {
  if ! command -v jq &> /dev/null; then
    echo -e "${RED}❌ Error: jq is not installed${NC}"
    echo "Install jq: brew install jq (macOS) or apt-get install jq (Linux)"
    exit 1
  fi
}

# Check jq availability
check_jq

# =============================================================================
# C1: Check if code/package.json exists
# =============================================================================

echo "[C1] Checking if code/package.json exists..."

if [ ! -f "$CONNECTOR_ROOT/code/package.json" ]; then
  echo -e "${RED}❌ C1 FAILED: code/package.json not found${NC}"
  echo "   Fix: Create package.json in the code/ directory"
  FAILED_CHECKS=$((FAILED_CHECKS + 1))
else
  echo -e "${GREEN}✅ C1 PASSED: code/package.json exists${NC}"
fi

echo ""

# =============================================================================
# C2: Check @devrev/ts-adaas SDK version
# =============================================================================

echo "[C2] Checking @devrev/ts-adaas SDK version..."

if [ ! -f "$CONNECTOR_ROOT/code/package.json" ]; then
  echo -e "${YELLOW}⚠️  C2 SKIPPED: package.json not found${NC}"
  FAILED_CHECKS=$((FAILED_CHECKS + 1))
else
  CURRENT_VERSION=$(jq -r '.dependencies["@devrev/ts-adaas"]' "$CONNECTOR_ROOT/code/package.json")

  if [ "$CURRENT_VERSION" = "null" ] || [ -z "$CURRENT_VERSION" ]; then
    echo -e "${RED}❌ C2 FAILED: @devrev/ts-adaas not found in dependencies${NC}"
    echo "   Fix: npm install @devrev/ts-adaas@latest"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
  else
    # Fetch latest version from npm registry
    echo "   Fetching latest version from npm registry..."
    LATEST_VERSION=$(npm view @devrev/ts-adaas version 2>/dev/null)

    if [ -z "$LATEST_VERSION" ]; then
      echo -e "${YELLOW}⚠️  C2 WARNING: Unable to fetch latest version from npm registry${NC}"
      echo "   Current version: $CURRENT_VERSION"
      echo "   Please manually verify this is the latest version"
    else
      # Extract version numbers (handle ^, ~, or exact versions)
      CURRENT_NUM=$(echo "$CURRENT_VERSION" | sed 's/[\^~]//g')

      if [ "$CURRENT_NUM" != "$LATEST_VERSION" ]; then
        echo -e "${RED}❌ C2 FAILED: @devrev/ts-adaas is outdated${NC}"
        echo "   Current: $CURRENT_NUM"
        echo "   Latest:  $LATEST_VERSION"
        echo "   Fix: cd code && npm install @devrev/ts-adaas@$LATEST_VERSION"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
      else
        echo -e "${GREEN}✅ C2 PASSED: @devrev/ts-adaas is up to date ($CURRENT_NUM)${NC}"
      fi
    fi
  fi
fi

echo ""

# =============================================================================
# C3: Check if code/tsconfig.json exists
# =============================================================================

echo "[C3] Checking if code/tsconfig.json exists..."

if [ ! -f "$CONNECTOR_ROOT/code/tsconfig.json" ]; then
  echo -e "${RED}❌ C3 FAILED: code/tsconfig.json not found${NC}"
  echo "   Fix: Create tsconfig.json in the code/ directory"
  FAILED_CHECKS=$((FAILED_CHECKS + 1))
else
  echo -e "${GREEN}✅ C3 PASSED: code/tsconfig.json exists${NC}"
fi

echo ""

# =============================================================================
# C4: Check if TypeScript strict mode is enabled
# =============================================================================

echo "[C4] Checking if TypeScript strict mode is enabled..."

if [ ! -f "$CONNECTOR_ROOT/code/tsconfig.json" ]; then
  echo -e "${YELLOW}⚠️  C4 SKIPPED: tsconfig.json not found${NC}"
  FAILED_CHECKS=$((FAILED_CHECKS + 1))
else
  STRICT=$(jq -r '.compilerOptions.strict' "$CONNECTOR_ROOT/code/tsconfig.json")

  if [ "$STRICT" = "true" ]; then
    echo -e "${GREEN}✅ C4 PASSED: TypeScript strict mode is enabled${NC}"
  else
    echo -e "${RED}❌ C4 FAILED: TypeScript strict mode is not enabled${NC}"
    echo "   Current value: $STRICT"
    echo "   Fix: Set 'strict': true in tsconfig.json compilerOptions"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
  fi
fi

echo ""

# =============================================================================
# C5 & C6: Check ESLint configuration
# =============================================================================

echo "[C5] Checking if ESLint is configured to error on 'any' type..."
echo "[C6] Checking if ESLint is configured to error on deprecated code..."
echo ""

ESLINT_CONFIG=""
ESLINT_TYPE=""

# Find ESLint config
if [ -f "$CONNECTOR_ROOT/code/.eslintrc.json" ]; then
  ESLINT_CONFIG="$CONNECTOR_ROOT/code/.eslintrc.json"
  ESLINT_TYPE="json"
  echo "   Found .eslintrc.json"
elif [ -f "$CONNECTOR_ROOT/code/.eslintrc.js" ]; then
  ESLINT_CONFIG="$CONNECTOR_ROOT/code/.eslintrc.js"
  ESLINT_TYPE="js"
  echo "   Found .eslintrc.js (cannot parse with this script)"
  echo -e "${YELLOW}⚠️  C5 & C6 SKIPPED: .eslintrc.js parsing not supported${NC}"
  echo "   Please manually verify ESLint rules in .eslintrc.js"
  FAILED_CHECKS=$((FAILED_CHECKS + 2))
elif jq -e '.eslintConfig' "$CONNECTOR_ROOT/code/package.json" >/dev/null 2>&1; then
  ESLINT_CONFIG="$CONNECTOR_ROOT/code/package.json"
  ESLINT_TYPE="package"
  echo "   Found eslintConfig in package.json"
else
  echo -e "${RED}❌ C5 & C6 FAILED: No ESLint configuration found${NC}"
  echo "   Fix: Create .eslintrc.json or add eslintConfig to package.json"
  FAILED_CHECKS=$((FAILED_CHECKS + 2))
fi

echo ""

# Check C5 and C6 rules if config found
if [ -n "$ESLINT_CONFIG" ] && [ "$ESLINT_TYPE" != "js" ]; then

  # Check C5: @typescript-eslint/no-explicit-any
  if [ "$ESLINT_TYPE" = "json" ]; then
    NO_EXPLICIT_ANY=$(jq -r '.rules["@typescript-eslint/no-explicit-any"]' "$ESLINT_CONFIG" 2>/dev/null)
  elif [ "$ESLINT_TYPE" = "package" ]; then
    NO_EXPLICIT_ANY=$(jq -r '.eslintConfig.rules["@typescript-eslint/no-explicit-any"]' "$ESLINT_CONFIG" 2>/dev/null)
  fi

  if [ "$NO_EXPLICIT_ANY" = "error" ] || [ "$NO_EXPLICIT_ANY" = "2" ]; then
    echo -e "${GREEN}✅ C5 PASSED: ESLint configured to error on 'any' type${NC}"
  else
    echo -e "${RED}❌ C5 FAILED: ESLint not configured to error on 'any' type${NC}"
    echo "   Current value: $NO_EXPLICIT_ANY"
    echo "   Fix: Add to ESLint rules:"
    echo '   "@typescript-eslint/no-explicit-any": "error"'
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
  fi

  echo ""

  # Check C6: deprecation/deprecation
  if [ "$ESLINT_TYPE" = "json" ]; then
    DEPRECATION=$(jq -r '.rules["deprecation/deprecation"]' "$ESLINT_CONFIG" 2>/dev/null)
  elif [ "$ESLINT_TYPE" = "package" ]; then
    DEPRECATION=$(jq -r '.eslintConfig.rules["deprecation/deprecation"]' "$ESLINT_CONFIG" 2>/dev/null)
  fi

  if [ "$DEPRECATION" = "error" ] || [ "$DEPRECATION" = "2" ]; then
    echo -e "${GREEN}✅ C6 PASSED: ESLint configured to error on deprecated code${NC}"
  else
    echo -e "${RED}❌ C6 FAILED: ESLint not configured to error on deprecated code${NC}"
    echo "   Current value: $DEPRECATION"
    echo "   Fix: Install plugin and add rule:"
    echo "   npm install --save-dev eslint-plugin-deprecation"
    echo '   Add to ESLint rules: "deprecation/deprecation": "error"'
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
  fi
fi

echo ""
echo "=================================================="
echo "Validation Summary"
echo "=================================================="
echo ""
echo "Total Checks: $TOTAL_CHECKS"
echo "Failed Checks: $FAILED_CHECKS"
echo ""

if [ $FAILED_CHECKS -eq 0 ]; then
  echo -e "${GREEN}✅ ALL CHECKS PASSED${NC}"
  echo ""
  echo "Code quality configuration is valid!"
  exit 0
else
  echo -e "${RED}❌ $FAILED_CHECKS CHECK(S) FAILED${NC}"
  echo ""
  echo "Please fix the issues above before deployment."
  exit 1
fi
