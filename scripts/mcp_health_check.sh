#!/bin/bash
# 🔱 Omega Engine — MCP Health Check (Pre-flight)
# AP: AP-MCP-HEALTH-CHECK-v1.0.0

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

declare -A PORTS
PORTS["omega-hub"]=8016
# Note: omega-research and omega-stats are merged into omega-hub (Decision 050)

FAILED=0

echo -e "${YELLOW}🔍 Checking Omega MCP health...${NC}"

for mcp in "${!PORTS[@]}"; do
    PORT=${PORTS[$mcp]}
    if curl -s -I -f "http://127.0.0.1:$PORT/sse" > /dev/null; then
        echo -e "${GREEN}✅ $mcp is alive on port $PORT${NC}"
    else
        echo -e "${RED}❌ $mcp is DOWN on port $PORT${NC}"
        FAILED=1
    fi
done

if [ $FAILED -eq 1 ]; then
    echo -e "${RED}⚠️ Some MCP services are unresponsive.${NC}"
    exit 1
else
    echo -e "${GREEN}🚀 All MCP services are healthy.${NC}"
    exit 0
fi
