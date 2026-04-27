# Naz Lab Text Workstation - One-Click Colab Launcher

This launcher is designed for Google Colab. It reduces the repeated setup steps into one main cell.

## Why this is needed

Google Colab runtimes are temporary. When a runtime disconnects or resets, the following disappear:

- `/content/naz-lab` local repo clone
- installed Python packages
- running Ollama server
- running Streamlit server
- running Cloudflare tunnel
- current public tunnel URL

The following remain saved:

- GitHub repository files
- Google Drive `/MyDrive/NazLab` folder
- configs and logs
- output files
- job queue files
- Ollama model files saved through Drive persistence

## How to use

1. Open a fresh Google Colab notebook.
2. If you need better LLM speed, set Runtime to T4 GPU.
3. Run Cell 1 first to mount Google Drive.
4. Run Cell 2, the one-click launcher.
5. Copy the Cloudflare URL and open it.

---

## Cell 1 - Mount Drive

Run this as a normal Python cell, not `%%bash`.

```python
from google.colab import drive
drive.mount('/content/drive')
```

Expected result:

```text
Mounted at /content/drive
```

---

## Cell 2 - One-Click Launcher

Run this as one `%%bash` cell.

```bash
%%bash
set -u

REPO_URL="https://github.com/nazmul73/naz-lab.git"
REPO_DIR="/content/naz-lab"
APP_PATH="$REPO_DIR/text_workstation/app.py"
STREAMLIT_LOG="/content/streamlit_text_workstation.log"
OLLAMA_LOG="/content/ollama.log"
CLOUDFLARE_LOG="/content/cloudflared_text_workstation.log"
MODEL_PRIMARY="gemma2:2b"
MODEL_CPU="tinyllama"

section() {
  echo ""
  echo "============================================================"
  echo "$1"
  echo "============================================================"
}

section "1. Check Drive mount"
if [ ! -d /content/drive/MyDrive ]; then
  echo "ERROR: Google Drive is not mounted. Run Cell 1 first."
  exit 1
fi

echo "Drive OK: /content/drive/MyDrive"

section "2. Clone or update repo"
cd /content
rm -rf "$REPO_DIR"
git clone --depth 1 "$REPO_URL" "$REPO_DIR"
cd "$REPO_DIR"
echo "Latest commit:"
git log -1 --oneline

section "3. Run Phase 0 foundation setup"
python "$REPO_DIR/master_setup/init_drive_structure.py"

section "4. Install Text Workstation dependencies"
python -m pip install -q -r "$REPO_DIR/text_workstation/requirements.txt"
python -m streamlit --version

section "5. Install system requirements for Ollama"
apt-get update -y
apt-get install -y zstd curl wget

section "6. Install Ollama if needed"
curl -fsSL https://ollama.com/install.sh | sh

section "7. Restart Ollama server"
killall ollama || true
pkill -f ollama || true
sleep 3
nohup /usr/local/bin/ollama serve > "$OLLAMA_LOG" 2>&1 &
sleep 12

echo "Ollama log tail:"
cat "$OLLAMA_LOG" | tail -80

echo "Ollama API tags:"
curl -s http://localhost:11434/api/tags || true

section "8. Verify / pull models"
# tinyllama is the CPU fallback. It is small and useful when GPU quota is unavailable.
/usr/local/bin/ollama pull "$MODEL_CPU"

# If GPU is available, also verify/pull gemma2:2b.
# This model is better quality but may be slow on CPU.
if command -v nvidia-smi >/dev/null 2>&1 && nvidia-smi >/dev/null 2>&1; then
  echo "GPU detected. Verifying primary model: $MODEL_PRIMARY"
  /usr/local/bin/ollama pull "$MODEL_PRIMARY"
else
  echo "No GPU detected. Skipping primary model pull by default. Use tinyllama for CPU mode."
fi

echo "Final model list:"
/usr/local/bin/ollama list

section "9. Direct tinyllama backend test"
timeout 180 curl -s http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model":"tinyllama","prompt":"Reply with only one word: OK","stream":false}' \
  | head -c 1000

echo ""

section "10. Validate app"
python -m py_compile "$APP_PATH"
grep -n "AVAILABLE_MODELS" "$APP_PATH" || true
grep -n "tinyllama" "$APP_PATH" || true
grep -n "Phase 1.2 Hotfix" "$APP_PATH" || true

section "11. Start Streamlit"
pkill -f streamlit || true
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
cat "$STREAMLIT_LOG" | tail -120

echo "Localhost check:"
curl -I http://localhost:8501 || true

section "12. Start Cloudflare tunnel"
wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O /content/cloudflared
chmod +x /content/cloudflared
pkill -f cloudflared || true
sleep 2
nohup /content/cloudflared tunnel --url http://localhost:8501 > "$CLOUDFLARE_LOG" 2>&1 &
sleep 12

PUBLIC_URL=$(grep -o 'https://[-a-zA-Z0-9.]*trycloudflare.com' "$CLOUDFLARE_LOG" | head -1 || true)

echo "Cloudflare log tail:"
cat "$CLOUDFLARE_LOG" | tail -60

echo ""
echo "============================================================"
echo "NAZ LAB TEXT WORKSTATION READY"
echo "Open this URL:"
echo "$PUBLIC_URL"
echo "============================================================"
echo "Recommended model if GPU quota is unavailable: tinyllama"
echo "Recommended model if T4 GPU is available: gemma2:2b"
```

---

## Expected final output

At the end, you should see:

```text
NAZ LAB TEXT WORKSTATION READY
Open this URL:
https://something.trycloudflare.com
```

Open that URL in your browser.

## App test order

1. Select `tinyllama` if CPU mode.
2. Select `gemma2:2b` if T4 GPU is available.
3. Test General Chat with: `Reply only OK`.
4. Test Re-writer with a short text.
5. Test Free Writer.
6. Test Prompt Improver and confirm it creates an image job JSON.
7. Test tab switching to confirm input/output persistence.

## Stop everything before closing Colab

Run this cell before closing Colab:

```bash
%%bash
pkill -f streamlit || true
pkill -f cloudflared || true
killall ollama || true
pkill -f ollama || true
ps aux | grep -E "streamlit|cloudflared|ollama" | grep -v grep || true
echo "Naz Lab processes stopped."
```
