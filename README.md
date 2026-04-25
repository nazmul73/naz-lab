# Naz Lab AI Workstation

Naz Lab is a modular, free AI content creation workstation designed for Google Colab, Streamlit, Ollama, Google Drive, and open-source creative tools.

## Vision

Naz Lab is designed around this workflow:

```text
Idea -> Story -> Script -> Image Prompt -> Image Generation -> Voice Generation -> FaceFusion / LivePortrait -> Final Reel Pack
```

The system is intentionally modular. The main dashboard stays lightweight, while heavy tools run in separate Colab notebooks.

## Current Main Dashboard

The main dashboard is built with Streamlit and includes:

- AI Agents
- Custom Gems
- Image Tools control center
- Voice Tools control center
- Video Tools control center
- Output Library
- Settings
- Ollama health check
- Google Drive output saving

## Backend

The main AI backend is Ollama running locally inside Colab.

Default model:

```text
gemma2:2b
```

Optional model:

```text
mistral
```

Ollama API endpoint:

```text
http://localhost:11434/api/generate
```

## Default Naz Gems

- 📖 Storyteller
- 📱 Viral Scripter
- 🎬 Video Planner
- 💼 Business Guru

Custom Gems are stored in:

```text
/content/drive/MyDrive/NazLab/config/custom_gems.json
```

## Tool Architecture

### Main Dashboard Notebook

Lightweight control center:

- Streamlit UI
- Ollama text generation
- Custom Gems
- Tool links
- Job plans
- Output preview

### FaceFusion Lab

Separate Colab notebook for face swap / face enhancement workflows.

Output folder:

```text
/content/drive/MyDrive/NazLab/facefusion_outputs
```

### LivePortrait Lab

Separate Colab notebook for animating static portraits using a driving video.

Output folder:

```text
/content/drive/MyDrive/NazLab/liveportrait_outputs
```

### Fooocus Image Lab

Separate planned notebook for image generation from scene prompts.

Output folder:

```text
/content/drive/MyDrive/NazLab/image_outputs
```

### XTTS v2 Voice Lab

Separate planned notebook for text-to-speech and voice cloning.

Output folder:

```text
/content/drive/MyDrive/NazLab/voice_outputs
```

## Why Separate Notebooks?

FaceFusion, LivePortrait, Fooocus, and XTTS v2 can require heavy dependencies such as CUDA, PyTorch, ONNX Runtime, FFmpeg, and model weights. Keeping them separate prevents the main dashboard from becoming unstable.

## Safety Notice

Use FaceFusion, LivePortrait, and XTTS v2 only with your own face/voice, licensed assets, or people who gave clear permission. Do not impersonate real people or create misleading content.

## Main Files

```text
app.py
requirements.txt
README.md
colab_main_dashboard.md
colab_facefusion_lab.md
colab_liveportrait_lab.md
colab_fooocus_image_lab.md
colab_xtts_voice_lab.md
project_plan.md
.gitignore
```

## First Test Order

1. Run the main dashboard notebook.
2. Confirm Ollama works with gemma2:2b.
3. Confirm the Streamlit dashboard opens.
4. Test 📱 Viral Scripter.
5. Save one output to Google Drive.
6. Test Custom Gems.
7. Then run FaceFusion Lab separately.
8. Then run LivePortrait Lab separately.

## Validation

```bash
python -m py_compile app.py
grep -n "Viral" app.py
grep -n "Fooocus" app.py
grep -n "XTTS" app.py
grep -n "FaceFusion" app.py
grep -n "LivePortrait" app.py
cat requirements.txt
```
