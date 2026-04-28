# Naz Lab Input Test Console One-Cell Launcher

Use this when you only want to test the frontend Input Test Console in Colab.

This one cell automatically:

- checks Google Drive mount
- clones or updates the latest repo
- installs Streamlit
- stops old Streamlit/Cloudflare processes
- starts the Input Test Console on port 8508
- creates a Cloudflare public URL
- prints the openable link

## Colab cell

```bash
%%bash
set -Eeuo pipefail

REPO_URL="https://github.com/nazmul73/naz-lab.git"
REPO_DIR="/content/naz-lab"
APP_REL="test_console/app.py"
PORT="8508"
LOCAL_HOST="127.0.0.1"
STREAMLIT_LOG="/content/streamlit_test_console.log"
CLOUDFLARE_LOG="/content/cloudflared_test_console.log"

print_section() {
  echo ""
  echo "============================================================"
  echo "$1"
  echo "============================================================"
}

print_section "Naz Lab Input Test Console One-Cell Launcher"

if [ ! -d /content/drive/MyDrive ]; then
  echo "ERROR: Google Drive is not mounted. Run this first in a Python cell:"
  echo "from google.colab import drive"
  echo "drive.mount('/content/drive')"
  exit 1
fi

print_section "Clone or update repo"
cd /content
if [ -d "$REPO_DIR/.git" ]; then
  cd "$REPO_DIR"
  git fetch --depth 1 origin main
  git reset --hard origin/main
else
  rm -rf "$REPO_DIR"
  git clone --depth 1 "$REPO_URL" "$REPO_DIR"
  cd "$REPO_DIR"
fi

git log -1 --oneline

print_section "Install dependencies"
python -m pip install -q streamlit
python -m streamlit --version

print_section "Validate Input Test Console"
python -m py_compile "$REPO_DIR/$APP_REL"

print_section "Stop old processes"
pkill -f streamlit || true
pkill -f cloudflared || true
sleep 2

print_section "Start Input Test Console"
nohup python -m streamlit run "$REPO_DIR/$APP_REL" \
  --server.port "$PORT" \
  --server.address 0.0.0.0 \
  --server.headless true \
  --server.enableCORS false \
  --server.enableXsrfProtection false \
  > "$STREAMLIT_LOG" 2>&1 &

sleep 10
cat "$STREAMLIT_LOG" | tail -80

print_section "Health check"
if ! pgrep -f "streamlit run .*${APP_REL}" >/dev/null 2>&1; then
  echo "ERROR: Streamlit process is not running. Showing log:"
  cat "$STREAMLIT_LOG"
  exit 1
fi

if ! curl -fsS "http://${LOCAL_HOST}:${PORT}" >/tmp/naz_lab_input_console_health.html 2>/tmp/naz_lab_input_console_health.err; then
  echo "ERROR: Input Test Console is running but not responding on http://${LOCAL_HOST}:${PORT}"
  cat /tmp/naz_lab_input_console_health.err || true
  cat "$STREAMLIT_LOG"
  exit 1
fi

echo "Input Test Console health check OK: http://${LOCAL_HOST}:${PORT}"

print_section "Start Cloudflare tunnel"
if [ ! -x /content/cloudflared ]; then
  wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O /content/cloudflared
  chmod +x /content/cloudflared
fi

nohup /content/cloudflared tunnel --url "http://${LOCAL_HOST}:${PORT}" > "$CLOUDFLARE_LOG" 2>&1 &

PUBLIC_URL=""
for attempt in $(seq 1 30); do
  PUBLIC_URL=$(grep -o 'https://[-a-zA-Z0-9.]*trycloudflare.com' "$CLOUDFLARE_LOG" | head -1 || true)
  if [ -n "$PUBLIC_URL" ]; then
    break
  fi
  sleep 2
done

cat "$CLOUDFLARE_LOG" | tail -100

if [ -z "$PUBLIC_URL" ]; then
  echo "ERROR: Cloudflare public URL was not created."
  echo "Streamlit log: $STREAMLIT_LOG"
  echo "Cloudflare log: $CLOUDFLARE_LOG"
  exit 1
fi

print_section "NAZ LAB INPUT TEST CONSOLE READY"
echo "Open this URL:"
echo "$PUBLIC_URL"
echo ""
echo "If the link does not open immediately, wait 10-20 seconds and refresh once."
echo "Streamlit log: $STREAMLIT_LOG"
echo "Cloudflare log: $CLOUDFLARE_LOG"
```

## What to test after opening

Go to:

```text
Input Builder
```

Use:

```text
Project: General Bangla
Workflow to test: Full Content Package
Language: Bangla
Platform: Facebook Reel
Audience: Bangladeshi Facebook audience
Main input / topic: বাংলাদেশে AI tools দিয়ে ছোট ব্যবসার content বানানো
Direction / style: সহজ বাংলা, practical tone, ৬০ সেকেন্ডের Reel-ready package
```

Then click:

```text
Save JSON package
```
