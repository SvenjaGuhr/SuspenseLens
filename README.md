# SuspenseLens 🔍
**A browser-based tool for theory-driven suspense annotation of literary texts**

SuspenseLens lets you load any short story, run it through a local AI model, and receive sentence-level suspense annotations from four distinct theoretical perspectives — displayed as a colour-coded heatmap with CATMA-style underlines, directly in your browser. No server, no subscription, no data leaves your computer.


<--! # SuspenseLens
Website for short story suspense level exploration filtered by different literary suspense theories to allow a multi-perspective approach to literary suspense in US-American and British short stories from the Gutenberg collection. -->

---

## What it does

- Annotates every sentence of a text for **reader suspense** and **character anxiety** on a 0–5 Likert scale
- Applies four suspense theories in parallel:
  - **T1** Uncertainty-based suspense (Carroll / Smuts)
  - **T2** Desire-Frustration suspense (Smuts)
  - **T3** Suspense in the Absence of Uncertainty / Mental Space Theory (Fauconnier)
  - **T4** Casual reader — no theory knowledge
  - **T5** Constitutional / general annotation
- Displays results as a **blue heatmap** overlay with **colour-coded underlines per theory** (comparable to CATMA annotation)
- Filter by theory, suspense level, character, or suspense element
- Export annotations as **JSON, CSV, or TSV** for further analysis

---

## Requirements

- A computer running macOS, Windows, or Linux
- **LM Studio** (free) — runs the AI model locally
- **Python 3** — for serving the HTML file (pre-installed on Mac and most Linux systems)
- A recommended local model: **Qwen3-4B-Instruct-2507 MLX 8bit** (~4 GB, Apple Silicon) or any instruction-tuned model available in LM Studio

---

## Setup — Step by Step

### Step 1 — Download SuspenseLens

Download `SuspenseLens.html` from this repository (click the file → **Download raw file**) and save it somewhere easy to find, for example your Desktop or a project folder.

---

### Step 2 — Install LM Studio

1. Go to **[lmstudio.ai](https://lmstudio.ai)** and download the installer for your operating system
2. Install and open LM Studio

---

### Step 3 — Download a model

Inside LM Studio:

1. Click the **magnifying glass** icon in the left sidebar (Discover / Search)
2. Search for: `Qwen3-4B-Instruct-2507`
3. Download **lmstudio-community / Qwen3-4B-Instruct-2507-MLX-8bit** (~4 GB)

> **Don't have enough RAM?** Any instruction-tuned model works. A 3B–8B model is recommended. Check the model's page for RAM requirements.

---

### Step 4 — Start the local server and enable CORS

1. In LM Studio, click the **`</>` Developer** icon in the left sidebar
2. Select your downloaded model from the model dropdown at the top of the panel
3. Click **Start Server** — the button turns green when running
4. Find the toggle **"Allow cross-origin requests (CORS)"** and turn it **ON**

> CORS must be enabled — without it, the browser cannot communicate with LM Studio.

---

### Step 5 — Serve SuspenseLens from a local web server

Browsers block network requests from HTML files opened directly from disk. You need to serve SuspenseLens via a tiny local web server. This takes one command.

**Open a Terminal** (Mac: `Cmd + Space` → type Terminal → Enter) and run:

```bash
cd ~/Desktop          # or wherever you saved SuspenseLens.html
python3 -m http.server 8080
```

You should see:
```
Serving HTTP on :: port 8080 ...
```

**Keep this Terminal window open** while using SuspenseLens.

> **Windows users:** open PowerShell and use the same command. If `python3` is not found, try `python -m http.server 8080`.

---

### Step 6 — Open SuspenseLens in your browser

Open Chrome, Firefox, or Safari and navigate to:

```
http://localhost:8080/SuspenseLens.html
```

The tool loads with Oscar Wilde's *The Model Millionaire* pre-loaded as a demo text with human baseline annotations already visible.

---

### Step 7 — Connect to LM Studio

In the toolbar at the top of SuspenseLens:

| Field | Value |
|---|---|
| Backend | LM Studio |
| Model | Qwen3-4B-2507 MLX 8bit ★ |
| Server URL | http://localhost:1234 |

1. Click **🔍 Detect** — the model name should appear in green
2. Click **Test ↗** — should show **✓ Connected**

If you see an error, check that the LM Studio server is running and CORS is enabled (Step 4).

---

### Step 8 — Load your text

Click **📂 Load Text** in the top-right and either:
- Paste your short story as plain text, or
- Load a `.txt` file from disk

Sentences are detected automatically.

---

### Step 9 — Annotate

1. In the **left sidebar**, select one or more suspense theories (or leave "All Theories" selected)
2. Click **⚡ Annotate**
3. Watch sentences light up in real time as the model annotates each batch
4. Click any sentence to see the full annotation in the detail panel

---

### Step 10 — Export your results

Click **⬇ Export** and choose:
- **Session JSON ★** — saves everything including all theory annotations; can be re-imported later to continue work
- **CSV / TSV** — for analysis in R, Python, or spreadsheet software

---

## Annotation Scheme

Each sentence receives the following fields per theory:

| Field | Description |
|---|---|
| `reader_suspense_level` | 0–5 Likert scale — suspense experienced by the reader |
| `character_anxiety_level` | 0–5 Likert scale — suspense/anxiety of the focal character |
| `character` | Name of the character experiencing suspense |
| `suspense_element` | Literary element or mechanism causing suspense |
| `arising_question` | The question the suspense raises for the reader |

---

## Theoretical Background

The annotation prompts are grounded in the following theories:

- **Uncertainty-based suspense** — suspense as forward-looking uncertainty about an unknown outcome (Carroll 1996; Smuts 2008)
- **Desire-Frustration suspense** — suspense without uncertainty; the reader possesses information the character lacks and cannot communicate (Smuts 2008)
- **Suspense in the Absence of Uncertainty** — using Fauconnier's Mental Space Theory (1994) to explain how suspense persists even when the reader knows the outcome
- **Casual reader** — surface-level, intuitive annotation without theoretical framing

---

## Troubleshooting

| Problem | Solution |
|---|---|
| 🔍 Detect shows "LMS unreachable" | LM Studio server is not running, or CORS is not enabled |
| "Network error" on Test | You opened the HTML file directly — follow Step 5 |
| Empty annotations after running | Model not fully loaded — wait for the progress bar in LM Studio to finish |
| `Address already in use` in Terminal | Run `python3 -m http.server 8081` and open `localhost:8081` instead |
| Annotations contain `<think>` text | Update to the latest SuspenseLens version — thinking tokens are stripped automatically |

---

## Importing existing annotations

If you have a CSV annotation file in the project scheme format (columns: `Sentence_ID`, `Sentence`, `reader_suspense_level`, `character_anxiety_level`, `character`, `suspense_element`), click **⬆ CSV** in the toolbar to import it as a baseline. The tool will display the human annotations and you can run AI annotations on top for comparison.

---

## Citing this tool

If you use SuspenseLens in your research, please cite:

```
[your citation here]
```

---

## License

[your license here]
