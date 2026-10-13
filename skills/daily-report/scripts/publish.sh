#!/usr/bin/env bash
# Optional: copy a report into ~/standup and make sure a LAN-reachable static server serves it.
# Never takes a port that is already in use. Usage: publish.sh report.html
# Note: the server has no auth and lists the whole ~/standup directory to anyone who can reach it.
set -uo pipefail
SRC=$(realpath "$1") || exit 1
DIR="$HOME/standup"; LOG="$HOME/.cache/standup-server.log"
mkdir -p "$DIR" "$(dirname "$LOG")"
[ "$(dirname "$SRC")" = "$DIR" ] || cp "$SRC" "$DIR/"
NAME=$(basename "$SRC")
NAME_Q=$(python3 -c 'import sys,urllib.parse;print(urllib.parse.quote(sys.argv[1]))' "$NAME")

port_free() { python3 -c 'import socket,sys;s=socket.socket();s.bind(("",int(sys.argv[1])))' "$1" 2>/dev/null; }
serves_dir() {  # does http://127.0.0.1:$1/ serve ~/standup? (our marker file is reachable)
  curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:$1/$NAME_Q" 2>/dev/null | grep -q '^200$'
}

# Reuse a server already serving ~/standup: any listening port in range that returns our file.
PORT=""
for p in $(seq 8098 8120); do
  if ! port_free "$p" && serves_dir "$p"; then PORT=$p; echo "reusing static server on $PORT"; break; fi
done

if [ -z "$PORT" ]; then
  for p in $(seq 8098 8120); do
    if port_free "$p"; then PORT=$p; break; fi
  done
  [ -z "$PORT" ] && { echo "no free port in 8098-8120; not starting a server" >&2; exit 1; }
  nohup python3 -m http.server "$PORT" --bind 0.0.0.0 --directory "$DIR" >"$LOG" 2>&1 &
  echo "started static server on $PORT (pid $!, log $LOG)"
  for _ in $(seq 1 10); do serves_dir "$PORT" && break; sleep 0.5; done
fi

if serves_dir "$PORT"; then echo "HTTP 200"; else echo "server on $PORT did not answer; see $LOG" >&2; exit 1; fi

python3 - "$PORT" "$NAME_Q" <<'EOF'
import ipaddress, socket, subprocess, sys
port, name = sys.argv[1], sys.argv[2]
ips = set()
try:
    ips.update(subprocess.run(["hostname", "-I"], capture_output=True, text=True).stdout.split())
except OSError:
    pass
try:  # fallback (macOS etc.): the address used for outbound traffic
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(("10.255.255.255", 1)); ips.add(s.getsockname()[0])
except OSError:
    pass
tailnet = ipaddress.ip_network("100.64.0.0/10")
for ip in sorted(ips):
    try:
        a = ipaddress.ip_address(ip)
    except ValueError:
        continue
    if a.version != 4:
        continue
    if a in tailnet:
        print(f"Tailscale: http://{ip}:{port}/{name}")
    elif a.is_private and not a.is_loopback:
        print(f"LAN:       http://{ip}:{port}/{name}")
EOF
