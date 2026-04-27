# Naz Lab Text Workstation - Option B 2-Cell Colab Launcher

This runbook starts the Naz Lab Text Workstation in a fresh Google Colab runtime.

## Current decision

Option B is the final launcher format:

- Cell 1: Mount Google Drive.
- Cell 2: Run the master shell launcher.
- `app.py` and code files stay in GitHub.
- Google Drive stores persistence: models, configs, logs, outputs, job queue, and generated files.
- Colab runtime is temporary, so every new runtime must rebuild the local environment.

---

## Before you run

### বিষয় পরিষ্কার

এই launcher শুধু Text Workstation চালাবে। সব workstation একসাথে চালানো হবে না।

Recommended model:

- CPU runtime: `tinyllama`
- T4/GPU runtime: `gemma2:2b`

Expected persistent Drive base path:

```text
/content/drive/MyDrive/NazLab
```

---

# Cell 1 - Drive mount

## 1. এই cell কী করবে

এই cell Google Drive mount করবে, যাতে Naz Lab-এর persistent folders, configs, logs, outputs, job queue, এবং Ollama model files ব্যবহার করা যায়।

## 2. আপনার করণীয় কী

Google Colab-এ একটি normal Python cell তৈরি করুন। `%%bash` ব্যবহার করবেন না। নিচের code paste করে run করুন। Permission চাইলে Google account দিয়ে allow করুন।

## 3. Exact code

```python
from google.colab import drive
drive.mount('/content/drive')
```

## 4. Expected result

```text
Mounted at /content/drive
```

অথবা আগে mount করা থাকলে এরকম কিছু দেখতে পারেন:

```text
Drive already mounted at /content/drive
```

## 5. Error হলে কী করবেন

যদি authentication error হয়:

1. Runtime > Disconnect and delete runtime করুন।
2. আবার notebook খুলুন।
3. Cell 1 আবার run করুন।
4. Permission prompt এলে allow করুন।

যদি `/content/drive/MyDrive` না থাকে, তাহলে Drive mount সম্পূর্ণ হয়নি। Cell 2 চালাবেন না।

---

# Cell 2 - Master launcher

## 1. এই cell কী করবে

এই cell পুরো Text Workstation runtime rebuild করবে:

1. Drive mount হয়েছে কিনা check করবে।
2. GitHub repo clone/update করবে।
3. Phase 0 foundation setup run করবে।
4. Python dependencies install করবে।
5. system packages install করবে।
6. Ollama install/start করবে।
7. `/root/.ollama/models` থেকে Drive model folder symlink করবে।
8. CPU হলে `tinyllama` pull/check করবে।
9. GPU/T4 থাকলে `gemma2:2b` pull/check করবে।
10. Direct Ollama backend test করবে।
11. `app.py` syntax validate করবে।
12. Streamlit start করবে।
13. Cloudflare Tunnel start করবে।
14. public URL print করবে।

## 2. আপনার করণীয় কী

Google Colab-এ দ্বিতীয় cell তৈরি করুন। এই cell অবশ্যই `%%bash` cell হবে। নিচের code paste করে run করুন।

## 3. Exact code

```bash
%%bash
set -Eeuo pipefail

REPO_URL="https://github.com/nazmul73/naz-lab.git"
REPO_DIR="/content/naz-lab"

if [ ! -d /content/drive/MyDrive ]; then
  echo "ERROR: Google Drive is not mounted. Run Cell 1 first."
  exit 1
fi

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

chmod +x text_workstation/launch_text_workstation.sh
bash text_workstation/launch_text_workstation.sh
```

## 4. Expected result

শেষে এরকম output দেখতে হবে:

```text
============================================================
14. Final status
============================================================
NAZ LAB TEXT WORKSTATION READY
Open this URL:
https://something.trycloudflare.com

Recommended model for this runtime: tinyllama
```

GPU/T4 runtime হলে recommended model হবে:

```text
Recommended model for this runtime: gemma2:2b
```

Cloudflare URL browser-এ open করুন।

## 5. Error হলে কী করবেন

### Error: Google Drive is not mounted

Cell 1 run হয়নি বা mount incomplete। Cell 1 আবার run করুন।

### Error: Ollama API did not start

নিচের debug cell run করুন:

```bash
%%bash
cat /content/ollama.log | tail -120
ps aux | grep -E "ollama" | grep -v grep || true
```

তারপর Cell 2 আবার run করুন।

### Error: selected model test timed out

CPU runtime হলে `tinyllama` select করুন। `gemma2:2b` CPU-তে slow হতে পারে। T4 GPU available থাকলে Runtime > Change runtime type > T4 GPU দিন, তারপর Cell 1 ও Cell 2 আবার run করুন।

### Cloudflare URL blank থাকলে

কখনও tunnel URL আসতে একটু দেরি হয়। নিচের cell run করুন:

```bash
%%bash
cat /content/cloudflared_text_workstation.log | tail -120
```

যদি URL দেখা যায়, সেটি open করুন। URL না এলে Cell 2 আবার run করুন।

### Streamlit page open না হলে

নিচের cell run করুন:

```bash
%%bash
cat /content/streamlit_text_workstation.log | tail -120
curl -I http://localhost:8501 || true
```

যদি Streamlit running না থাকে, Cell 2 আবার run করুন।

---

# App test order

Cloudflare URL open করার পর এই order-এ test করুন:

1. Sidebar থেকে model select করুন:
   - CPU হলে `tinyllama`
   - T4/GPU হলে `gemma2:2b`
2. Settings tab খুলুন।
3. `Check Ollama Health` click করুন।
4. `Test Selected Model` click করুন।
5. General Chat এ লিখুন: `Reply only OK`
6. Free Writer test করুন।
7. Re-writer test করুন।
8. Prompt Improver test করুন।
9. Prompt Improver output এর পর Drive folder check করুন:

```text
/content/drive/MyDrive/NazLab/job_queue/image_jobs
```

10. Tab/mode switch করে দেখুন input/output থাকে কিনা।

---

# Stop everything before closing Colab

## 1. এই cell কী করবে

Colab runtime-এর running Streamlit, Cloudflare, এবং Ollama process stop করবে।

## 2. আপনার করণীয় কী

কাজ শেষ হলে optional cleanup হিসেবে run করুন।

## 3. Exact code

```bash
%%bash
pkill -f streamlit || true
pkill -f cloudflared || true
killall ollama || true
pkill -f ollama || true
ps aux | grep -E "streamlit|cloudflared|ollama" | grep -v grep || true
echo "Naz Lab processes stopped."
```

## 4. Expected result

```text
Naz Lab processes stopped.
```

## 5. Error হলে কী করবেন

`No such process` type message এলে সমস্যা নেই। এর মানে process আগে থেকেই বন্ধ ছিল।

---

# Notes

- Colab exported `.py` notebook files runtime logs নয়।
- Actual runtime output সবসময় active Colab cell output থেকে যাচাই করবেন।
- Cloudflare URL প্রতি runtime/session-এ বদলাবে।
- Localtunnel fallback only; primary tunnel Cloudflare।
- `mistral` optional এবং CPU runtime-এর জন্য heavy হতে পারে।
