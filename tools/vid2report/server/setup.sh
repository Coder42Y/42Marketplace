#!/bin/bash
set -e

# vid2report — one-command setup
# Usage: ./setup.sh <your-api-key>
#         ./setup.sh sk-cp-xxx

if [ $# -eq 0 ]; then
    echo "Usage: ./setup.sh <your-api-key>"
    echo "  e.g.: ./setup.sh sk-cp-xxx"
    echo ""
    echo "Get a key from any OpenAI-compatible provider (MiniMax, DeepSeek, etc.)"
    exit 1
fi

API_KEY="$1"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

echo -e "${YELLOW}🔧 vid2report — setup${NC}"
echo ""

# 1. Node deps
cd "$(dirname "$0")"
if [ -d "node_modules" ]; then
    echo -e "${GREEN}[1/3] Node dependencies already installed, skipping${NC}"
else
    echo -e "${YELLOW}[1/3] Installing Node dependencies...${NC}"
    npm install --silent
    echo -e "${GREEN}  ✓ npm packages${NC}"
fi

# 2. System deps
echo -e "${YELLOW}[2/3] Installing system dependencies...${NC}"

if command -v yt-dlp &>/dev/null; then
    echo -e "${GREEN}  ✓ yt-dlp (already installed)${NC}"
else
    if command -v brew &>/dev/null; then
        brew install yt-dlp --quiet 2>/dev/null && echo -e "${GREEN}  ✓ yt-dlp${NC}" || echo -e "${RED}  ✗ yt-dlp — install manually: brew install yt-dlp${NC}"
    else
        echo -e "${RED}  ✗ yt-dlp — install manually: brew install yt-dlp${NC}"
    fi
fi

if python3 -c "import faster_whisper" 2>/dev/null; then
    echo -e "${GREEN}  ✓ faster-whisper (already installed)${NC}"
else
    pip3 install faster-whisper -q 2>/dev/null && echo -e "${GREEN}  ✓ faster-whisper${NC}" || echo -e "${RED}  ✗ faster-whisper — install manually: pip3 install faster-whisper${NC}"
fi

# 3. Configure
echo -e "${YELLOW}[3/3] Configuring...${NC}"

# Detect API key prefix to guess provider
BASE_URL="https://api.openai.com/v1"
MODEL="gpt-4o-mini"
PROVIDER="openai-compatible"

if echo "$API_KEY" | grep -q "^sk-cp-"; then
    BASE_URL="https://api.minimaxi.com/v1"
    MODEL="MiniMax-M2.7-highspeed"
    PROVIDER="minimax"
fi

cat > .env <<EOF
OPENAI_COMPATIBLE_API_KEY=$API_KEY
OPENAI_COMPATIBLE_BASE_URL=$BASE_URL
OPENAI_COMPATIBLE_MODEL=$MODEL
OPENAI_PROVIDER_NAME=$PROVIDER
PORT=3550
EOF

echo -e "${GREEN}  ✓ .env configured${NC}"
echo ""

echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "   Server:  ${YELLOW}npm start${NC}  →  http://localhost:3550"
echo "   Test:    ${YELLOW}curl http://localhost:3550/ping${NC}"
echo "   CLI:     ${YELLOW}../bin/analyze-video.sh BVxxx${NC}"
echo ""
echo "   Then in Claude Code:  ${YELLOW}/av https://bilibili.com/video/BVxxx${NC}"
