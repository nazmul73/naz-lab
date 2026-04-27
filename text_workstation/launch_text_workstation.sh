#!/usr/bin/env bash
set -Eeuo pipefail

REPO_URL="${REPO_URL:-https://github.com/nazmul73/naz-lab.git}"
REPO_DIR="${REPO_DIR:-/content/naz-lab}"
APP_PATH="$REPO_DIR/text_workstation/app.py"

DRIVE_ROOT="${DRIVE_ROOT:-/content/drive/MyDrive/NazLab}"
OLLAMA_MODELS_DIR="$DRIVE_ROOT/models/ollama"

STREAMLIT_LOG="${STREAMLIT_LOG:-/content/streamlit_text_workstation.log}"
OLLAMA_LOG="${OLLAMA_LOG:-/content/ollama.log}"
CLOUDFLARE_LOG="${CLOUDFLARE_LOG:-/content/cloudflared_text_workstation.log}"

MODEL_PRIMARY="${MODEL_PRIMARY:-gemma2:2b}"
MODEL_CPU="${MODEL_CPU:-qwen2.5:0.5b}"
MODEL_LEGACY="${MODEL_LEGACY:-tinyllama}"

section() {
  echo ""
  echo "============================================================"
  echo "$1"
  echo "============================================================"
}

fail() {
  echo "ERROR: $1" >&2
  exit 1
}

has_gpu() {
  command -v nvidia-smi >/dev/null 2>&1 && nvidia-smi >/dev/null 2>&1
}

section "1. Check Google Drive mount"
if [ ! -d /content/drive/MyDrive ]; then
  fail "Google Drive is not mounted. Run Cell 1 first."
fi
echo "Drive OK: /content/drive/MyDrive"

section "2. Clone or update Naz Lab repo"
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
echo "Latest commit:"
git log -1 --oneline

section "3. Run Phase 0 foundation setup"
python "$REPO_DIR/master_setup/init_drive_structure.py"

section "4. Install Python dependencies"
python -m pip install -q --upgrade pip
python -m pip install -q -r "$REPO_DIR/text_workstation/requirements.txt"
python -m streamlit --version

section "5. Install system packages"
apt-get update -y
apt-get install -y zstd curl wget ca-certificates

section "6. Install or verify Ollama"
if ! command -v ollama >/dev/null 2>&1; then
  curl -fsSL https://ollama.com/install.sh | sh
else
  echo "Ollama already installed: $(command -v ollama)"
fi

section "7. Verify Ollama Drive model persistence"
mkdir -p "$OLLAMA_MODELS_DIR"
mkdir -p /root/.ollama
if [ -e /root/.ollama/models ] && [ ! -L /root/.ollama/models ]; then
  rm -rf /root/.ollama/models
fi
ln -sfn "$OLLAMA_MODELS_DIR" /root/.ollama/models
echo "Ollama model path:"
ls -ld /root/.ollama/models
echo "Drive model path:"
ls -ld "$OLLAMA_MODELS_DIR"

section "8. Restart Ollama server"
killall ollama >/dev/null 2>&1 || true
pkill -f "ollama serve" >/dev/null 2>&1 || true
sleep 3
nohup "$(command -v ollama)" serve > "$OLLAMA_LOG" 2>&1 &
sleep 12

echo "Ollama health check:"
if ! curl -fsS http://localhost:11434/api/tags >/tmp/ollama_tags.json; then
  echo "Ollama log tail:"
  tail -100 "$OLLAMA_LOG" || true
  fail "Ollama API did not start."
fi
cat /tmp/ollama_tags.json || true

section "9. Pull or verify recommended models"
echo "Pulling CPU recommended instruction model: $MODEL_CPU"
ollama pull "$MODEL_CPU"

echo "Verifying legacy tiny model is available only if already present."
ollama list | grep -q "^$MODEL_LEGACY" && echo "Legacy model present: $MODEL_LEGACY" || true

if has_gpu; then
  echo "GPU detected:"
  nvidia-smi || true
  echo "Pulling GPU recommended model: $MODEL_PRIMARY"
  ollama pull "$MODEL_PRIMARY"
  RECOMMENDED_MODEL="$MODEL_PRIMARY"
else
  echo "No GPU detected. CPU instruction fallback will be used."
  RECOMMENDED_MODEL="$MODEL_CPU"
fi

echo "Installed Ollama models:"
ollama list

section "10. Direct backend test"
timeout 180 curl -fsS http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"$RECOMMENDED_MODEL\",\"prompt\":\"Write one short sentence: AI saves time.\",\"stream\":false,\"options\":{\"num_predict\":40,\"temperature\":0.2}}" \
  | head -c 1200
echo ""

section "11. Validate Text Workstation app"
python -m py_compile "$APP_PATH"
grep -n "AVAILABLE_MODELS" "$APP_PATH" || true
grep -n "Test Selected Model" "$APP_PATH" || true
grep -n "Phase 1.6" "$APP_PATH" || true

section "12. Start Streamlit"
pkill -f streamlit >/dev/null 2>&1 || true
sleep 2
nohup python -m streamlit run "$APP_PATH" \
  --server.port 8501 \
  --server.address 0.0.0.0 \
  --server.headless true \
  --server.enableCORS false \
  --server.enableXsrfProtection false \
  > "$STREAMLIT_LOG" 2>&1 &

sleep 10

echo "Streamlit log tail:"
tail -120 "$STREAMLIT_LOG" || true

echo "Streamlit localhost check:"
curl -I http://localhost:8501 || true

section "13. Start Cloudflare tunnel"
if [ ! -x /content/cloudflared ]; then
  wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O /content/cloudflared
  chmod +x /content/cloudflared
fi

pkill -f cloudflared >/dev/null 2>&1 || true
sleep 2
nohup /content/cloudflared tunnel --url http://localhost:8501 > "$CLOUDFLARE_LOG" 2>&1 &
sleep 15

PUBLIC_URL="$(grep -o 'https://[-a-zA-Z0-9.]*trycloudflare.com' "$CLOUDFLARE_LOG" | head -1 || true)"

echo "Cloudflare log tail:"
tail -80 "$CLOUDFLARE_LOG" || true

section "14. Final status"
if [ -z "$PUBLIC_URL" ]; then
  echo "Cloudflare URL was not detected yet."
  echo "Run this command in a new Colab cell to inspect:"
  echo "cat $CLOUDFLARE_LOG | tail -120"
else
  echo "NAZ LAB TEXT WORKSTATION READY"
  echo "Open this URL:"
  echo "$PUBLIC_URL"
fi

echo ""
echo "Recommended model for this runtime: $RECOMMENDED_MODEL"
echo "CPU recommendation: $MODEL_CPU"
echo "GPU/T4 recommendation: $MODEL_PRIMARY"
echo "Legacy model, not recommended for writing: $MODEL_LEGACY"
echo ""
echo "Logs:"
echo "Ollama: $OLLAMA_LOG"
echo "Streamlit: $STREAMLIT_LOG"
echo "Cloudflare: $CLOUDFLARE_LOG"
