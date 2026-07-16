#!/usr/bin/env bash
set -u

input=$(cat)

if ! command -v jq >/dev/null 2>&1; then
  printf 'statusLine: jq is required\n'
  exit 0
fi

fields=$(
  printf '%s' "$input" | jq -r '
    [
      (.session_id // "default"),
      (.workspace.current_dir // .cwd // ""),
      (.model.display_name // .model.id // "未知"),
      (if (.context_window.used_percentage | type) == "number" then (.context_window.used_percentage | floor) else "-" end),
      (.context_window.total_input_tokens // .context_window.current_usage.input_tokens // 0 | floor),
      (.context_window.total_output_tokens // .context_window.current_usage.output_tokens // 0 | floor),
      (.context_window.context_window_size // 200000 | floor)
    ] | @tsv
  ' 2>/dev/null
)

if [ -n "$fields" ]; then
  IFS=$'\t' read -r session_id current_dir model percentage input_tokens output_tokens context_size <<< "$fields"
else
  session_id=default
  current_dir=${PWD:-/}
  model=未知
  percentage=-
  input_tokens=0
  output_tokens=0
  context_size=200000
fi

current_dir=${current_dir:-${PWD:-/}}
model=${model:-未知}
input_tokens=${input_tokens:-0}
output_tokens=${output_tokens:-0}
context_size=${context_size:-200000}

for numeric_name in input_tokens output_tokens context_size; do
  value=${!numeric_name}
  if ! [[ $value =~ ^[0-9]+$ ]]; then
    printf -v "$numeric_name" '%s' 0
  fi
done

used_tokens=$((input_tokens + output_tokens))
if ! [[ $percentage =~ ^[0-9]+$ ]]; then
  if [ "$context_size" -gt 0 ]; then
    percentage=$((used_tokens * 100 / context_size))
  else
    percentage=0
  fi
fi
[ "$percentage" -lt 0 ] && percentage=0
[ "$percentage" -gt 100 ] && percentage=100

format_tokens() {
  local value=$1
  if [ "$value" -ge 1000000 ]; then
    awk -v value="$value" 'BEGIN { printf "%.1fM", value / 1000000 }'
  elif [ "$value" -ge 1000 ]; then
    awk -v value="$value" 'BEGIN { printf "%.0fk", value / 1000 }'
  else
    printf '%s' "$value"
  fi
}

run_quickly() {
  if command -v timeout >/dev/null 2>&1; then
    timeout 1 "$@"
  else
    "$@"
  fi
}

memory_display='n/a'
if [ -r /proc/meminfo ]; then
  mem_total_kb=$(awk '/^MemTotal:/ { print $2; exit }' /proc/meminfo)
  mem_available_kb=$(awk '/^MemAvailable:/ { print $2; exit }' /proc/meminfo)
  if [ -z "$mem_available_kb" ]; then
    mem_available_kb=$(awk '
      /^MemFree:/ { free = $2 }
      /^Buffers:/ { buffers = $2 }
      /^Cached:/ { cached = $2 }
      END { print free + buffers + cached }
    ' /proc/meminfo)
  fi
  memory_display=$(awk -v available="$mem_available_kb" -v total="$mem_total_kb" '
    BEGIN { printf "%.1fG/%.1fG", available / 1048576, total / 1048576 }
  ')
fi

branch='无 Git'
git_display='无'
if [ -d "$current_dir" ] && (
  cd "$current_dir" && run_quickly git rev-parse --is-inside-work-tree >/dev/null 2>&1
); then
  branch=$(
    cd "$current_dir" &&
      run_quickly git symbolic-ref --short HEAD 2>/dev/null ||
      run_quickly git rev-parse --short HEAD 2>/dev/null ||
      printf 'detached'
  )
  numstat=$(cd "$current_dir" && run_quickly git diff HEAD --numstat 2>/dev/null || true)
  read -r added deleted <<< "$({
    printf '%s\n' "$numstat" | awk '
      $1 ~ /^[0-9]+$/ { added += $1 }
      $2 ~ /^[0-9]+$/ { deleted += $2 }
      END { print added + 0, deleted + 0 }
    '
  })"
  untracked=$(
    cd "$current_dir" &&
      run_quickly git ls-files --others --exclude-standard 2>/dev/null |
      awk 'END { print NR + 0 }'
  )
  git_display="+${added} -${deleted}"
  if [ "$untracked" -gt 0 ]; then
    git_display="${git_display} ?${untracked}"
  fi
fi

safe_session=$(printf '%s' "$session_id" | tr -cd 'A-Za-z0-9._-')
[ -z "$safe_session" ] && safe_session=default
session_dir="$HOME/.cache/claude-statusline/sessions"
session_file="$session_dir/$safe_session"
umask 077
mkdir -p "$session_dir"
chmod 0700 "$HOME/.cache/claude-statusline" "$session_dir" 2>/dev/null || true
now=$(date +%s)
start=''
if [ -f "$session_file" ]; then
  start=$(cat "$session_file" 2>/dev/null || true)
fi
if ! [[ $start =~ ^[0-9]+$ ]]; then
  start=$now
  printf '%s\n' "$start" > "$session_file"
fi
find "$session_dir" -type f -mtime +30 -delete 2>/dev/null || true
elapsed_seconds=$((now - start))
elapsed_minutes=$((elapsed_seconds / 60))
if [ "$elapsed_minutes" -lt 1 ]; then
  elapsed_display='<1分'
elif [ "$elapsed_minutes" -lt 60 ]; then
  elapsed_display="${elapsed_minutes}分"
else
  elapsed_display=$(printf '%d时%02d分' $((elapsed_minutes / 60)) $((elapsed_minutes % 60)))
fi

skill_count=0
skills_root="$HOME/.claude/skills"
if [ -d "$skills_root" ]; then
  for skill_dir in "$skills_root"/*; do
    [ -d "$skill_dir" ] || continue
    if [ -f "$skill_dir/SKILL.md" ]; then
      skill_count=$((skill_count + 1))
    elif [ -d "$skill_dir/skills" ]; then
      nested_count=$(find "$skill_dir/skills" -mindepth 2 -maxdepth 2 -name SKILL.md -type f 2>/dev/null | wc -l)
      skill_count=$((skill_count + nested_count))
    fi
  done
fi

case "$current_dir" in
  "$HOME") cwd_display='~' ;;
  "$HOME"/*) cwd_display="~/${current_dir#"$HOME"/}" ;;
  *) cwd_display=$current_dir ;;
esac

bar_width=16
filled=$((percentage * bar_width / 100))
empty=$((bar_width - filled))
bar=''
index=0
while [ "$index" -lt "$filled" ]; do
  bar="${bar}█"
  index=$((index + 1))
done
index=0
while [ "$index" -lt "$empty" ]; do
  bar="${bar}░"
  index=$((index + 1))
done

YELLOW='\033[38;5;178m'
GREEN='\033[38;5;30m'
MAGENTA='\033[38;5;96m'
BLUE='\033[38;5;111m'
CYAN='\033[38;5;30m'
BRIGHT_CYAN='\033[1;38;5;80m'
RESET='\033[0m'

printf "%b模型: %s%b | %b内存: %s%b | %bGit: %s%b\n" \
  "$YELLOW" "$model" "$RESET" "$GREEN" "$memory_display" "$RESET" "$YELLOW" "$git_display" "$RESET"
printf "%b分支: %s%b | %b会话: %s%b | %b技能: %s%b\n" \
  "$MAGENTA" "$branch" "$RESET" "$CYAN" "$elapsed_display" "$RESET" "$BLUE" "$skill_count" "$RESET"
printf "%bcwd: %s%b\n" "$CYAN" "$cwd_display" "$RESET"
printf "%b上下文: [%s] %s/%s (%s%%)%b\n" \
  "$BRIGHT_CYAN" "$bar" "$(format_tokens "$used_tokens")" "$(format_tokens "$context_size")" "$percentage" "$RESET"
