#!/bin/bash
# Serena Configuration Verification Script
# Run this after restarting Claude Desktop to verify Serena is properly configured

echo "=================================================="
echo "Serena Configuration Verification"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASS="${GREEN}✓ PASS${NC}"
FAIL="${RED}✗ FAIL${NC}"
WARN="${YELLOW}⚠ WARN${NC}"

# Check 1: Serena process is running
echo "1. Checking Serena MCP server process..."
SERENA_PROC=$(ps aux | grep "serena start-mcp-server\|serena-mcp-server" | grep -v grep)
if [ -n "$SERENA_PROC" ]; then
    echo -e "   $PASS Serena MCP server is running"
    echo "   Process: $(echo $SERENA_PROC | awk '{print $2, $11, $12, $13}')"
else
    echo -e "   $FAIL Serena MCP server is NOT running"
    echo "   Action: Start Claude Desktop to launch Serena"
    exit 1
fi
echo ""

# Check 2: Most recent log file
echo "2. Checking most recent log file..."
LATEST_LOG=$(find ~/.serena/logs -name "mcp_*.txt" -type f -print0 | xargs -0 ls -t | head -1)
if [ -n "$LATEST_LOG" ]; then
    echo -e "   $PASS Found log: $LATEST_LOG"
    LOG_TIME=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$LATEST_LOG")
    echo "   Last modified: $LOG_TIME"
else
    echo -e "   $FAIL No log files found"
    exit 1
fi
echo ""

# Check 3: Context setting in log
echo "3. Verifying context setting..."
CONTEXT_LINE=$(grep "SerenaAgentContext\[name=" "$LATEST_LOG" | tail -1)
if echo "$CONTEXT_LINE" | grep -q "SerenaAgentContext\[name='agent'\]"; then
    echo -e "   $PASS Context is set to 'agent'"
    echo "   Found: $(echo $CONTEXT_LINE | grep -o "SerenaAgentContext\[name='[^']*'\]")"
elif echo "$CONTEXT_LINE" | grep -q "SerenaAgentContext\[name='desktop-app'\]"; then
    echo -e "   $FAIL Context is still 'desktop-app'"
    echo "   Found: $(echo $CONTEXT_LINE | grep -o "SerenaAgentContext\[name='[^']*'\]")"
    echo "   Action: Quit Claude Desktop completely (⌘+Q) and restart"
    exit 1
else
    echo -e "   $WARN Could not determine context from log"
    echo "   Action: Check manually using MCP tool"
fi
echo ""

# Check 4: Language servers
echo "4. Checking language servers..."
PYTHON_LS=$(grep "Starting language server for.*python" "$LATEST_LOG" 2>/dev/null)
SWIFT_LS=$(grep "Starting language server for.*swift" "$LATEST_LOG" 2>/dev/null)
TS_LS=$(grep "Starting language server for.*typescript" "$LATEST_LOG" 2>/dev/null)

if [ -n "$PYTHON_LS" ]; then
    echo -e "   $PASS Python language server started"
else
    echo -e "   $WARN Python language server not found in log"
fi

if [ -n "$SWIFT_LS" ]; then
    echo -e "   $PASS Swift language server started"
else
    echo -e "   $WARN Swift language server not found in log"
fi

if [ -n "$TS_LS" ]; then
    echo -e "   $PASS TypeScript language server started"
else
    echo -e "   $WARN TypeScript language server not found in log"
fi
echo ""

# Check 5: Language server processes
echo "5. Checking language server processes..."
PYLSP=$(ps aux | grep pylsp | grep -v grep)
SOURCEKIT=$(ps aux | grep sourcekit-lsp | grep -v grep)
TSSERVER=$(ps aux | grep typescript-language-server | grep -v grep)

if [ -n "$PYLSP" ]; then
    echo -e "   $PASS Python LSP (pylsp) is running"
else
    echo -e "   $WARN Python LSP not found in processes"
fi

if [ -n "$SOURCEKIT" ]; then
    echo -e "   $PASS Swift LSP (sourcekit-lsp) is running"
else
    echo -e "   $WARN Swift LSP not found in processes"
fi

if [ -n "$TSSERVER" ]; then
    echo -e "   $PASS TypeScript LSP is running"
else
    echo -e "   $WARN TypeScript LSP not found in processes"
fi
echo ""

# Check 6: Dashboard
echo "6. Checking web dashboard..."
if curl -s http://127.0.0.1:24282/dashboard/index.html > /dev/null 2>&1; then
    echo -e "   $PASS Dashboard is accessible at http://127.0.0.1:24282/dashboard/index.html"
else
    echo -e "   $WARN Dashboard not accessible (may not be enabled)"
fi
echo ""

# Check 7: Claude Desktop config
echo "7. Verifying Claude Desktop configuration..."
CONFIG_FILE="/Users/broadcaster_three/Library/Application Support/Claude/claude_desktop_config.json"
if [ -f "$CONFIG_FILE" ]; then
    if grep -q '"--context"' "$CONFIG_FILE" && grep -q '"agent"' "$CONFIG_FILE"; then
        echo -e "   $PASS Config file contains --context agent"
    else
        echo -e "   $FAIL Config file missing --context agent"
        exit 1
    fi

    if grep -q '"--project"' "$CONFIG_FILE"; then
        echo -e "   $PASS Config file contains --project flag"
    else
        echo -e "   $WARN Config file missing --project flag"
    fi
else
    echo -e "   $FAIL Config file not found"
    exit 1
fi
echo ""

# Summary
echo "=================================================="
echo "Verification Summary"
echo "=================================================="
echo ""
echo "✓ Serena MCP server is running"
echo "✓ Context should be verified with MCP tool"
echo "✓ Language servers configured for: Python, Swift, TypeScript"
echo ""
echo "Next Steps:"
echo "1. In Claude Code, run: mcp__serena__get_current_config"
echo "2. Verify output shows: 'Active context: agent'"
echo "3. Verify output shows: 'Programming languages: python, swift, typescript'"
echo ""
echo "Dashboard: http://127.0.0.1:24282/dashboard/index.html"
echo ""
