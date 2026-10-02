# SuspenseLens 🔍
**A browser-based tool for theory-driven suspense annotation and evaluation of literary texts**

SuspenseLens lets you load a short story, annotate it sentence by sentence with a local large language model system, and compare the results with human gold annotations. Annotations follow four theoretical perspectives on suspense and appear as a color-coded heatmap with colored underlines per theory, directly in your browser. No server, no subscription, and no text leaves your computer.

Current version: **3.8** (`SuspenseLens_V3_8.html`)

---

## What it does

- Annotates every sentence of a text for **reader suspense** and **character anxiety** on a 0–5 Likert scale
- Applies four suspense theories, separately or in one run:
  - **T1** Uncertainty-based suspense (Nomikos, Opton & Averill 1968; Iwata 2009)
  - **T2** Desire-frustration suspense (Smuts 2008)
  - **T3** Anomalous suspense under partial outcome knowledge (Gerrig 1989)
  - **T4** Casual reader, an atheoretical baseline
- Uses **feed-forward reading context**: for every sentence, the model receives the story up to that sentence, with theory-specific additions for T2 and T3 (see below)
- Displays results as a heatmap overlay with color-coded underlines per theory, and as a suspense curve (📈 Chart)
- Filters by theory, suspense level, character, or suspense element
- **Evaluates** model annotations against a human gold standard (📊 Evaluation)
- Exports annotations as **Session JSON, CSV, or TSV**, charts as **HTML or PNG**, and evaluation results as **CSV**

---

## What's new in version 3.8

- **Prompts identical to the paper.** The constitutional prompt and the four theory prompts (T1–T4) use the exact wording of the appendix of Guhr, Bamman et al. (in preparation). Theory names and citations in the interface match the paper.
- **Model menu shows your downloaded models.** SuspenseLens asks LM Studio for all downloaded language models (embedding models excluded) and lists only these. The currently loaded model is marked with ●. The list refreshes on page load, when you switch to LM Studio, when you change the server URL, and with **↻ Refresh models**.
- **Feed-forward context.** Every request carries the reading knowledge the selected theory presupposes, so the model's knowledge grows with every sentence, as a human reader's does.
- **Strict sentence-by-sentence mode.** With *Batch 1*, the model never sees a sentence after the one it rates.
- **Missing answers stay missing.** If a model returns no usable levels for a sentence, SuspenseLens retries up to three times. Sentences that still receive no answer stay unannotated, are listed at the end of the run, and are left out of the evaluation. Earlier versions stored them as 0.
- **Support for reasoning models.** SuspenseLens asks models to skip their reasoning phase, retries once with a larger output budget if reasoning used up the budget, and recovers answers that a model writes into its reasoning output.
- **Shorter output and timing readout.** The model is asked for minimal answers (suspense element of at most six words). The progress bar shows seconds per request, output tokens, and an estimate of the remaining time.
- **Light and dark mode.** The **☀ Light / ☾ Dark** button in the toolbar switches to a white background. The choice is remembered in your browser, and chart exports (PNG, HTML) use the current theme.
- **Evaluation fixes.** The evaluation CSV export now escapes quotation marks correctly and includes a `Gold_Sentence_ID` column. The **⚡ Run Evaluation** button becomes available after every finished or cancelled run.

---

## Requirements

- A computer running macOS, Windows, or Linux
- **LM Studio** (free), which runs the model locally
- **Python 3**, for serving the HTML file (pre-installed on Mac and most Linux systems)
- An internet connection for the 📈 Chart view and for Excel gold files (both libraries load from a CDN); annotation itself runs offline
- At least one instruction-tuned model in LM Studio. Models used in our experiments:

| Model | Size on disk (approx.) | Notes |
|---|---|---|
| Qwen3-4B-Instruct-2507 (MLX) | 4 GB | Fast; no reasoning phase; recommended for testing |
| Olmo 3 7B Instruct (MLX) | 4 GB | Fully open training data |
| Llama 3.1 8B Instruct | 8.5 GB | Established reference model |
| Qwen3.8-27B | 16 GB | Reasons by default; turn thinking off (see Step 4) |

---

## Setup, step by step

### Step 1: Download SuspenseLens

Download `SuspenseLens_V3_8.html` from this repository (click the file → **Download raw file**) and save it in an easy-to-find folder, for example your Desktop or a project folder.

### Step 2: Install LM Studio

1. Go to **[lmstudio.ai](https://lmstudio.ai)** and download the installer for your operating system
2. Install and open LM Studio

### Step 3: Download a model

1. In LM Studio, click the **magnifying glass** icon in the left sidebar (Discover)
2. Search for a model from the table above, for example `Qwen3-4B-Instruct-2507`
3. Download it

> **Not enough memory?** Any instruction-tuned model works. Models with 3B–8B parameters run on most laptops.

### Step 4: Load the model with the right settings

When you load a model in LM Studio, check two settings:

1. **Context length: at least 8192 tokens.** Feed-forward annotation sends the story so far with every request, and T2 sends the whole story in addition. For "How It Happened" (106 sentences), a T2 request reaches about 4,000 tokens. LM Studio often loads models with 4096 tokens by default, which is too short.
2. **Thinking off** for reasoning models (for example Qwen3.8-27B). With thinking on, every request produces hundreds to thousands of reasoning tokens before the answer, which can stretch one theory over several hours.

### Step 5: Start the local server and enable CORS

1. In LM Studio, click the **`</>` Developer** icon in the left sidebar
2. Click **Start Server**; the button turns green when the server is running
3. Turn on **"Allow cross-origin requests (CORS)"**

> Without CORS, the browser cannot communicate with LM Studio.

### Step 6: Serve SuspenseLens from a local web server

Browsers block network requests from HTML files opened directly from disk, so SuspenseLens needs a small local web server. Open a Terminal (Mac: `Cmd + Space` → type Terminal → Enter) and run:

```bash
cd ~/Desktop          # or the folder where you saved SuspenseLens_V3_8.html
python3 -m http.server 8080
```

You should see `Serving HTTP on :: port 8080 ...`. **Keep this window open** while you use SuspenseLens.

> **Windows:** use PowerShell. If `python3` is not found, try `python -m http.server 8080`.

### Step 7: Open SuspenseLens in your browser

Open Chrome, Firefox, or Safari and go to:

```
http://localhost:8080/SuspenseLens_V3_8.html
```

The tool opens with Oscar Wilde's *The Model Millionaire* as a demo text with human baseline annotations.

### Step 8: Connect to LM Studio

In the toolbar:

| Field | Value |
|---|---|
| Backend | LM Studio (local) |
| Model | one of your downloaded models (● = currently loaded) |
| Server URL | http://localhost:1234 |

1. If the list is empty or outdated, click **↻ Refresh models**
2. Click **Test ↗**; it should show **✓ Connected**

### Step 9: Load your text

Click **📂 Load Text** and paste your story as plain text or load a `.txt` file. SuspenseLens splits the text into sentences automatically.

### Step 10: Choose the annotation settings and annotate

1. In the left sidebar, select one theory or **All Theories**
2. Choose the **context** and **batch size** next to the Annotate button (see *Annotation settings*)
3. Click **⚡ Annotate** and watch the sentences light up as the model annotates them
4. Click any sentence to see its full annotation in the detail panel

### Step 11: Export your results

Click **⬇ Export ▾** and choose:
- **💾 Session JSON ★**: saves the text and all theory annotations; re-import it later with **⬆ Session JSON**
- **CSV / TSV**: for analysis in R, Python, or spreadsheet software

> Annotations are kept only while the page is open. **Export the session JSON after every run.**

**Run information in every export.** The first line of every export records how the annotations were produced: SuspenseLens version, text, export time, and for each theory the model, backend, context setting, batch size, temperature, status (completed or cancelled), end time, number of annotated sentences, and sentences without an answer. In CSV, TSV, and evaluation CSV files, this line starts with `#` (read them with `pandas.read_csv(path, comment='#')` in Python or `read.csv(path, comment.char = '#')` in R). In JSON files, it is the first field, `suspenselens_run`, and the full settings follow under `runs`. Chart HTML files begin with it as an HTML comment, and PNG charts show it above the chart. Sentences without an annotation for a theory are left empty in CSV and TSV exports.

---

## Annotation settings

### Reading context

| Setting | What the model receives before the sentence to annotate |
|---|---|
| **Context: per theory** (default) | T1, T4: all preceding sentences · T2: the complete story as a first read, then all preceding sentences (second read) · T3: the final 10% of the story, then all preceding sentences |
| **Context: story so far** | All preceding sentences, for every theory |
| **Context: none (batch only)** | Only the sentences being annotated (the behavior of versions up to 3.5) |

Context sentences are marked as context and keep their sentence IDs. For long texts, the context is capped at about 10,000 tokens; the oldest lines are dropped first, with a note in the prompt.

### Batch size

| Setting | Requests for a 106-sentence story | Effect |
|---|---|---|
| **Batch 1 (strict)** | 106 per theory | The model never sees a later sentence. Recommended for evaluation runs. |
| **Batch 3** | 36 per theory | Faster; the first sentence of each batch is rated with knowledge of the next two |
| **Batch 5** | 22 per theory | Fastest; more look-ahead and a higher risk of incomplete answers |

### Speed

The progress bar shows seconds per request, average output tokens, reasoning tokens (if the server reports them), and the estimated time left. With thinking off, a minimal answer has about 40–60 output tokens. If the readout shows reasoning tokens or well over 100 output tokens per request, the model is still reasoning (see Step 4).

---

## Running several theories, resuming, and merging sessions

- **Annotations are stored per theory.** A T3 run after a T2 run adds T3 annotations and leaves the T2 annotations unchanged. Both are available for the evaluation.
- **Cancelling keeps everything annotated so far.** The request in progress finishes and is saved, then the run stops. The partial annotations can be exported and evaluated; the evaluation then covers only the annotated sentences.
- **Resuming a run.** Choose **Only missing (resume)** next to the batch size and click **⚡ Annotate**. SuspenseLens annotates only the sentences that have no annotation yet for the selected theory, so a cancelled run continues where it stopped and sentences without an answer are filled in. The reading context is rebuilt from the text, so a resumed sentence receives the same context as in an uninterrupted run. If the earlier part was annotated with another model, SuspenseLens asks before mixing models, and the run information records the resumption.
- **Rerunning a theory.** With **All sentences**, SuspenseLens asks before replacing existing annotations of that theory.
- **Merging sessions.** To combine theories annotated in separate sessions (for example T2 on one day and T3 on another), load one session, click **⬆ Session JSON**, tick **Merge into the current session**, and load the other. Annotations the open session lacks are added sentence by sentence; existing annotations are kept. Both sessions must contain the same text with the same sentence split. The run information of both sessions is kept per theory.
- **Loading a text or importing a CSV clears all annotations** for all theories. Export the session JSON first.

---

## Evaluation against a gold standard

Open **📊 Evaluation**, upload a gold file, choose a theory under **Compare gold vs.** (or **All theories**), and click **⚡ Run Evaluation**.

### Gold file format

- **Excel (`.xlsx`):** one sheet per theory, with sheet names beginning with `T1`, `T2`, `T3`, `T4` (for example `T1_gold`). SuspenseLens selects the sheet that matches the chosen theory.
- **CSV:** a single sheet, used for every theory.
- **Columns**, in this order: `Sentence_ID`, `Sentence`, `reader_suspense_level`, `character`, `character_anxiety_level`, `suspense_evoking_element`. Additional columns may follow if their names do not contain `sentence`, `id`, `character`, or `element`. SuspenseLens uses the first column whose name contains these keywords, which is why `character` must come before `character_anxiety_level`.

### Building a gold file from several annotators

`build_gold_standard.py` creates the gold file from one Excel file per theory (file names beginning with `T1_`, `T2_`, …), each with one sheet per annotator:

```bash
pip install pandas openpyxl
python build_gold_standard.py --input-dir <folder> --output <name>_gold.xlsx                       # mean (default)
python build_gold_standard.py --input-dir <folder> --output <name>_gold_median.xlsx --aggregate median
```

For every sentence and both scales, the script computes three aggregates of the annotators' ratings and writes all of them to each theory sheet: (1) the **mean** (`R_mean`, `C_mean`, two decimals), (2) the **median** (`R_median`, `C_median`; with an even number of annotators a half value is rounded down), and (3) the **majority vote** (`R_majority`, `C_majority`; ties go to the value closest to the median, then to the lower value). `--aggregate` chooses which of them fills `reader_suspense_level` and `character_anxiety_level`, the columns SuspenseLens evaluates against; the default is the mean. In addition, the script (4) treats empty cells as missing ratings, (5) counts every annotator, including those who rated a scale 0 throughout a text, since 0 is a valid rating (`--exclude-all-zero` leaves them out), (6) removes lines without text (such as section breaks), and (7) warns when two annotator sheets are nearly identical. Each theory sheet also lists every annotator's ratings; an `agreement` sheet reports each annotator's exact agreement with the majority vote and mean distance to the mean.

**Which aggregate?** The mean uses every rating and keeps the distances on the scale, which suits correlation measures such as Spearman's ρ. The median suits metrics that need whole levels (exact agreement, κ). The majority vote is kept for comparison; on a 0–5 scale with many default zeros, it often falls to 0 although several annotators rated a sentence clearly above 0.

### Matching and metrics

Gold and model sentences are aligned by text similarity (Jaccard similarity and longest common subsequence, threshold 0.35), so a gold file also works when SuspenseLens has split the text slightly differently. For each theory and scale, SuspenseLens reports exact agreement, agreement within one level, mean absolute error, root mean squared error, Pearson and Spearman correlation, Cohen's κ, linearly weighted κ, and per-level precision, recall, and F1. **⬇ Export CSV** saves the sentence-level comparison.

Gold values may be decimals (for example a mean of 2.67). Correlations, mean absolute error, and root mean squared error use the exact value; exact agreement, agreement within one level, κ, and per-level scores use the value rounded to the nearest level. Spearman's ρ is computed as the correlation of average ranks, which is exact with tied ratings.

### Human–model agreement heat maps

`iaa_heatmap.py` draws one heat map per scale, with every annotator and the mean, median, and majority vote per theory as rows and one model per column:

```bash
pip install pandas numpy matplotlib scipy openpyxl
python iaa_heatmap.py --gold <name>_gold.xlsx --metric spearman \
  --model "Qwen3-4B=eval_qwen4b.csv" --model "Qwen3.8-27B=eval_qwen27b.csv" --out <name>_spearman
```

Each `--model` is a SuspenseLens evaluation CSV (version 3.8 or later). `--metric` is `spearman`, `alpha` (Krippendorff's α, ordinal; the default), or `qwk` (quadratic weighted κ). Spearman uses decimal gold values as they are; α and κ round them to the nearest level. The script writes PNG and PDF figures and a CSV with every value and the number of sentences it is based on.

---

## Annotation scheme

Each sentence receives the following fields per theory:

| Field | Description |
|---|---|
| `reader_suspense_level` | 0–5, suspense experienced by the reader |
| `character_anxiety_level` | 0–5, suspense or anxiety of a story-world character |
| `character` | Character experiencing suspense; `Narrator` only for the narrating self's present, retrospective reflection |
| `suspense_element` | Literary element or mechanism evoking suspense |

---

## Prompts

The prompts are documented in the appendix of the accompanying paper; SuspenseLens uses them verbatim. Each request also contains (1) four few-shot annotations per theory from Wilde's *The Model Millionaire*, (2) the reading context described above, (3) the instruction to read the input sentences in order and keep the answer minimal, and (4) for LM Studio, a request to skip the reasoning phase (`/no_think`, `enable_thinking: false`). Models that do not support these settings ignore them.

---

## Theoretical background

- **T1 Uncertainty-based suspense:** suspense as forward-looking uncertainty about an anticipated outcome (Nomikos, Opton & Averill 1968; Iwata 2009)
- **T2 Desire-frustration suspense:** the reader holds information that could help a character, wants to intervene, and cannot; uncertainty is not required (Smuts 2008)
- **T3 Anomalous suspense:** suspense that persists with partial outcome knowledge; the reader reads the final 10% of the story first (Gerrig 1989)
- **T4 Casual reader:** intuitive annotation without any theory, as a baseline for the model's default concept of suspense

---

## Troubleshooting

| Problem | Solution |
|---|---|
| Model list empty or "Offline: showing saved list" | LM Studio server is not running, or CORS is off (Step 5); then click ↻ Refresh models |
| "Network error" on Test | The HTML file was opened directly from disk; follow Step 6 |
| "Empty content in response" / "The model only returned reasoning" | Turn thinking off for the model in LM Studio (Step 4) |
| Annotation is very slow | Check the timing readout; turn thinking off, or use a smaller model or a larger batch for test runs |
| "Response cut off (finish_reason=length)" | Increase the model's context length in LM Studio (Step 4) |
| "… without answer" at the end of a run | These sentences received no usable answer after three attempts; they are listed in the debug panel and excluded from the evaluation |
| Run Evaluation stays disabled | Upload a gold file and annotate at least one theory |
| `Address already in use` in Terminal | Run `python3 -m http.server 8081` and open `localhost:8081` instead |

---

## Importing existing annotations

To display human annotations, click **⬆ CSV** and select a CSV file in the project scheme (`Sentence_ID`, `Sentence`, `reader_suspense_level`, `character_anxiety_level`, `character`, `suspense_element`). This replaces the current text and its annotations. Excel gold files for the evaluation are uploaded in **📊 Evaluation** instead.

---

## References

De Ford, Miriam Allen. 1961. "Oh, Rats!" *Galaxy Magazine*, December 1961. https://www.gutenberg.org/ebooks/51751. <br>
Gerrig, Richard J. 1989. "Suspense in the Absence of Uncertainty." *Journal of Memory and Language* 28 (6): 633–48. https://doi.org/10.1016/0749-596X(89)90001-6. <br>
Guhr, Svenja. 2026. *Suspense in Shorts*. GitHub repository. https://github.com/SvenjaGuhr/Suspense_in_Shorts. <br>
Guhr, Svenja, David Bamman, et al. In preparation. "Keeping Us in Suspense: Testing Theory Pluralism Against LLMs' Intrinsic Concepts." <br>
Iwata, Yumiko. 2009. "Creating Suspense and Surprise in Short Literary Fiction: A Stylistic and Narratological Approach." Doctoral thesis, University of Birmingham. <br>
Nomikos, Markellos S., Edward Opton Jr., and James R. Averill. 1968. "Surprise versus Suspense in the Production of Stress Reaction." *Journal of Personality and Social Psychology* 8 (2): 204–8. <br>
Smuts, Aaron. 2008. "The Desire-Frustration Theory of Suspense." *Journal of Aesthetics and Art Criticism* 66 (3): 281–90. https://doi.org/10.1111/j.1540-6245.2008.00309.x. <br>

---

## Citing this tool

If you use SuspenseLens in your research, please cite:

```
Guhr, Svenja. 2026. SuspenseLens. Version 3.8. GitHub repository. https://github.com/SvenjaGuhr/SuspenseLens.
```

---

## AI-use declaration

The code was developed with the support of Anthropic's Claude models (Sonnet 4.6 and Opus 5.5) in the Claude app.

Last update: 2026-10-01
