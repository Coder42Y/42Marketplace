#!/bin/bash
# Video analysis pipeline — standalone server
# Usage: ./analyze-video.sh <url-or-video-id>

set -e

API_BASE="${BILIGPT_API:-http://localhost:3550}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

if [ $# -eq 0 ]; then
    echo "Usage: $0 <video-url-or-id>"
    echo "  e.g.: $0 https://www.bilibili.com/video/BV16HoyBKEa8"
    echo "  e.g.: $0 BV16HoyBKEa8"
    exit 1
fi

INPUT="$1"

# Parse video ID and service
if echo "$INPUT" | grep -qE 'BV[0-9A-Za-z]{10}'; then
    VIDEO_ID=$(echo "$INPUT" | grep -oE 'BV[0-9A-Za-z]{10}' | head -1)
    SERVICE="bilibili"
elif echo "$INPUT" | grep -qE '^av[0-9]+'; then
    VIDEO_ID="$INPUT"
    SERVICE="bilibili"
elif echo "$INPUT" | grep -qE '(youtube\.com/watch\?v=|youtu\.be/)'; then
    VIDEO_ID=$(echo "$INPUT" | sed -E 's/.*(watch\?v=|youtu\.be\/)([A-Za-z0-9_-]+).*/\2/')
    SERVICE="youtube"
elif echo "$INPUT" | grep -qE '^[A-Za-z0-9_-]{11}$'; then
    VIDEO_ID="$INPUT"
    SERVICE="youtube"
else
    echo -e "${RED}❌ Cannot parse video ID from: $INPUT${NC}"
    exit 1
fi

echo -e "${YELLOW}🎬 视频分析${NC}"
echo "  服务: $SERVICE"
echo "  ID:   $VIDEO_ID"
echo ""

# Check if server is running
if ! curl -sf "$API_BASE/ping" > /dev/null 2>&1; then
    echo -e "${RED}❌ 服务未运行。请先启动: cd server && npm start${NC}"
    exit 1
fi

echo -e "${YELLOW}⏳ 运行中...${NC}"
echo "  阶段1: 提取文案 → 阶段2: 语音转录(如需) → 阶段3: AI分析 → 存档"
echo ""

START=$(date +%s)

RESPONSE=$(curl -s -X POST "$API_BASE/api/save-transcript" \
    -H "Content-Type: application/json" \
    -d "{\"videoConfig\":{\"videoId\":\"$VIDEO_ID\",\"service\":\"$SERVICE\"}}" \
    --max-time 600 2>&1)

END=$(date +%s)
ELAPSED=$((END - START))
MIN=$((ELAPSED / 60))
SEC=$((ELAPSED % 60))

SUCCESS=$(echo "$RESPONSE" | python3 -c "import json,sys; d=json.load(sys.stdin); print('yes' if d.get('success') else 'no')" 2>/dev/null || echo "no")

if [ "$SUCCESS" = "yes" ]; then
    TITLE=$(echo "$RESPONSE" | python3 -c "import json,sys; print(json.load(sys.stdin).get('title',''))")
    FILEPATH=$(echo "$RESPONSE" | python3 -c "import json,sys; print(json.load(sys.stdin).get('filepath',''))")
    ALEN=$(echo "$RESPONSE" | python3 -c "import json,sys; print(json.load(sys.stdin).get('analysisLength',0))")
    TLEN=$(echo "$RESPONSE" | python3 -c "import json,sys; print(json.load(sys.stdin).get('transcriptLength',0))")
    TRANSCRIBED=$(echo "$RESPONSE" | python3 -c "import json,sys; d=json.load(sys.stdin); print('Yes' if d.get('hasTranscribed') else 'No')")

    echo -e "${GREEN}✅ 分析完成 ($MIN 分 $SEC 秒)${NC}"
    echo ""
    echo "  标题:     $TITLE"
    echo "  转录:     $TRANSCRIBED ($TLEN 字)"
    echo "  分析:     $ALEN 字"
    echo "  存档:     $FILEPATH"
    echo ""
    open "$FILEPATH" 2>/dev/null || echo "  文件: $FILEPATH"
else
    ERROR=$(echo "$RESPONSE" | python3 -c "import json,sys; print(json.load(sys.stdin).get('error','Unknown'))" 2>/dev/null || echo "API error")
    echo -e "${RED}❌ 失败: $ERROR${NC}"
    exit 1
fi
