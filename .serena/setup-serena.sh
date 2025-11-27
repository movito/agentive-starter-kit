#!/bin/bash

# Serena MCP Setup Script
# =======================
# Installs and configures Serena for semantic code navigation in Claude Code.
#
# What this script does:
# 1. Verifies prerequisites (uvx or pipx)
# 2. Adds Serena to Claude Code's MCP configuration
# 3. Creates project.yml from template
# 4. Verifies the installation
#
# Usage: ./.serena/setup-serena.sh [project-name]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PROJECT_NAME="${1:-$(basename "$PROJECT_ROOT")}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                                ║${NC}"
echo -e "${CYAN}║   ${GREEN}Serena MCP Setup${CYAN}                                            ║${NC}"
echo -e "${CYAN}║   ${NC}Semantic code navigation for Claude Code${CYAN}                    ║${NC}"
echo -e "${CYAN}║                                                                ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo

# Step 1: Check prerequisites
echo -e "${BLUE}Step 1: Checking prerequisites...${NC}"

HAS_UVX=false
HAS_PIPX=false
HAS_CLAUDE=false

if command -v uvx &> /dev/null; then
    HAS_UVX=true
    echo -e "  ${GREEN}✓${NC} uvx found"
fi

if command -v pipx &> /dev/null; then
    HAS_PIPX=true
    echo -e "  ${GREEN}✓${NC} pipx found"
fi

if command -v claude &> /dev/null; then
    HAS_CLAUDE=true
    CLAUDE_VERSION=$(claude --version 2>/dev/null || echo "unknown")
    echo -e "  ${GREEN}✓${NC} Claude Code found ($CLAUDE_VERSION)"
else
    echo -e "  ${RED}✗${NC} Claude Code not found"
    echo -e "    Install: https://claude.com/code"
    exit 1
fi

if [[ "$HAS_UVX" == false && "$HAS_PIPX" == false ]]; then
    echo -e "  ${RED}✗${NC} Neither uvx nor pipx found"
    echo -e "    Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo -e "    Or pipx: brew install pipx && pipx ensurepath"
    exit 1
fi

echo

# Step 2: Add Serena to Claude Code MCP configuration
echo -e "${BLUE}Step 2: Configuring Claude Code MCP...${NC}"

# Check if Serena is already configured
if claude mcp list 2>/dev/null | grep -q "serena"; then
    echo -e "  ${YELLOW}!${NC} Serena already configured in Claude Code"
else
    # Add Serena MCP server
    if [[ "$HAS_UVX" == true ]]; then
        echo -e "  Adding Serena via uvx..."
        claude mcp add serena -- uvx --from "git+https://github.com/oraios/serena" serena-mcp-server
    else
        echo -e "  Adding Serena via pipx..."
        # First install with pipx if needed
        if ! pipx list | grep -q serena; then
            pipx install "git+https://github.com/oraios/serena"
        fi
        claude mcp add serena -- serena-mcp-server
    fi
    echo -e "  ${GREEN}✓${NC} Serena added to Claude Code MCP"
fi

echo

# Step 3: Create project.yml from template
echo -e "${BLUE}Step 3: Creating project configuration...${NC}"

TEMPLATE="$SCRIPT_DIR/project.yml.template"
CONFIG="$SCRIPT_DIR/project.yml"

if [[ -f "$CONFIG" ]]; then
    echo -e "  ${YELLOW}!${NC} project.yml already exists"
    read -p "  Overwrite? (y/N): " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        echo -e "  Skipping project.yml creation"
    else
        cp "$TEMPLATE" "$CONFIG"
        sed -i '' "s/\${PROJECT_NAME}/$PROJECT_NAME/" "$CONFIG" 2>/dev/null || \
            sed -i "s/\${PROJECT_NAME}/$PROJECT_NAME/" "$CONFIG"
        echo -e "  ${GREEN}✓${NC} project.yml created"
    fi
else
    cp "$TEMPLATE" "$CONFIG"
    sed -i '' "s/\${PROJECT_NAME}/$PROJECT_NAME/" "$CONFIG" 2>/dev/null || \
        sed -i "s/\${PROJECT_NAME}/$PROJECT_NAME/" "$CONFIG"
    echo -e "  ${GREEN}✓${NC} project.yml created for project: $PROJECT_NAME"
fi

echo

# Step 4: Verify configuration (NOT the running server)
echo -e "${BLUE}Step 4: Verifying configuration...${NC}"

if claude mcp list 2>/dev/null | grep -q "serena"; then
    echo -e "  ${GREEN}✓${NC} Serena MCP server configured"
else
    echo -e "  ${YELLOW}!${NC} Serena not yet in MCP list (may need Claude Code restart)"
fi

if [[ -f "$CONFIG" ]]; then
    echo -e "  ${GREEN}✓${NC} project.yml exists"
else
    echo -e "  ${RED}✗${NC} project.yml not found"
fi

echo
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Serena configuration complete!${NC}"
echo
echo -e "${YELLOW}Important:${NC} Serena starts when an agent first uses it, not immediately."
echo -e "If you see a browser error about connecting to localhost, just close it."
echo
echo -e "Next steps:"
echo -e "1. Edit ${CYAN}.serena/project.yml${NC} to enable your languages"
echo -e "2. ${YELLOW}Restart Claude Code${NC} (quit and reopen, or restart your IDE)"
echo -e "3. Launch an agent: ${CYAN}./agents/launch planner${NC}"
echo -e "4. Agent will auto-activate Serena on first use"
echo
echo -e "To verify Serena is configured:"
echo -e "  ${CYAN}claude mcp list | grep serena${NC}"
echo
