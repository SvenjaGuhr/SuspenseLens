"""
Build a SuspenseLens (v3.6) gold-standard workbook from multi-annotator Excel files.

Input
-----
One .xlsx per theory, with the theory in the file name ("T1_...", "T2_...", ...).
Each sheet in a file is one annotator; all sheets share the column layout
    Sentence_ID | Sentence | reader_suspense_level | character_anxiety_level |
    character | suspense/anxiety-evoking_element | arising_questions | question_answered_in_Sentence_ID

Output
------
One .xlsx with one sheet per theory (T1_gold ... T4_gold), in the column layout that
SuspenseLens parses, plus an "agreement" sheet with per-annotator statistics.
SuspenseLens picks the sheet whose name starts with the selected theory ("t1", "t2", ...).

Majority vote (per sentence, per dimension)
-------------------------------------------
* Plurality vote over the annotators' 0-5 levels.
* Ties are broken by the value closest to the median of all votes; if still tied,
  the lower value wins (conservative).
* Empty cells count as missing votes, not as 0.
* An annotator whose column is 0 throughout (e.g. character anxiety not annotated)
  is excluded from that dimension's vote, so the silent default does not outvote others.

Usage
-----
    pip install pandas openpyxl
    python build_gold_standard.py --input-dir . --output Doyle_How_it_happened_gold.xlsx
"""

import argparse
import itertools
import re
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

# ── settings ──────────────────────────────────────────────────────────────
THEORY_RE = re.compile(r"(?:^|[^A-Za-z0-9])T([1-4])_", re.IGNORECASE)
EXCLUDE_ALL_ZERO_ANNOTATORS = True   # drop an annotator from a dimension they never used
DROP_NON_TEXT_ROWS = True            # drop rows such as "*   *   *" (section breaks)
DUPLICATE_WARN_THRESHOLD = 0.95      # warn when two sheets agree on >= 95 % of reader levels

# Column positions in the annotator sheets (headers vary slightly, positions do not)
COL_ID, COL_TEXT, COL_READER, COL_CHAR_LVL, COL_CHARACTER, COL_ELEMENT = range(6)


# ── reading ───────────────────────────────────────────────────────────────
def annotator_label(sheet_name: str) -> str:
    """'T3a_Doyle_How_It_Happened' -> 'a'."""
    m = re.match(r"T\d([A-Za-z0-9]+)_", sheet_name)
    return m.group(1) if m else sheet_name


def read_theory_file(path: Path) -> dict[str, pd.DataFrame]:
    """Return {annotator: tidy DataFrame indexed by Sentence_ID}."""
    sheets = pd.read_excel(path, sheet_name=None)
    out = {}
    for name, df in sheets.items():
        cols = df.columns
        tidy = pd.DataFrame({
            "id":        pd.to_numeric(df[cols[COL_ID]], errors="coerce"),
            "text":      df[cols[COL_TEXT]].astype(str).str.strip(),
            "reader":    pd.to_numeric(df[cols[COL_READER]], errors="coerce"),
            "char_lvl":  pd.to_numeric(df[cols[COL_CHAR_LVL]], errors="coerce"),
            "character": df[cols[COL_CHARACTER]].fillna("").astype(str)
                           .str.replace("\xa0", " ").str.strip(),
            "element":   df[cols[COL_ELEMENT]].fillna("").astype(str)
                           .str.replace("\xa0", " ").str.strip(),
        }).dropna(subset=["id"])
        tidy["id"] = tidy["id"].astype(int)
        out[annotator_label(name)] = tidy.set_index("id")
    return out


# ── voting ────────────────────────────────────────────────────────────────
def majority_level(values: list[float]) -> tuple[float, int, int]:
    """Plurality vote with median tie-break. Returns (level, n_votes, n_agreeing)."""
    votes = [int(v) for v in values if not pd.isna(v)]
    if not votes:
        return np.nan, 0, 0
    counts = Counter(votes)
    top = max(counts.values())
    tied = [v for v, c in counts.items() if c == top]
    if len(tied) > 1:
        med = float(np.median(votes))
        tied.sort(key=lambda v: (abs(v - med), v))
    return tied[0], len(votes), top


def majority_label(values: list[str]) -> str:
    """Most frequent non-empty label (case-insensitive), returned in its first spelling."""
    vals = [v for v in values if v]
    if not vals:
        return ""
    counts = Counter(v.lower() for v in vals)
    winner = counts.most_common(1)[0][0]
    return next(v for v in vals if v.lower() == winner)


def build_theory_gold(annotators: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, dict]:
    labels = list(annotators)
    ref = annotators[labels[0]]

    # Which annotators count for which dimension
    def active(dim):
        if not EXCLUDE_ALL_ZERO_ANNOTATORS:
            return labels
        return [a for a in labels if annotators[a][dim].fillna(0).ne(0).any()]
    reader_voters, char_voters = active("reader"), active("char_lvl")

    rows = []
    for sid in ref.index:
        text = ref.at[sid, "text"]
        if DROP_NON_TEXT_ROWS and not re.search(r"\w", text):
            continue
        r_vals = [annotators[a].at[sid, "reader"] for a in reader_voters if sid in annotators[a].index]
        c_vals = [annotators[a].at[sid, "char_lvl"] for a in char_voters if sid in annotators[a].index]
        r_lvl, r_n, r_top = majority_level(r_vals)
        c_lvl, c_n, c_top = majority_level(c_vals) if char_voters else (0, 0, 0)

        character = majority_label([annotators[a].at[sid, "character"] for a in labels]) if c_lvl else ""
        elements = " | ".join(f"{a}: {annotators[a].at[sid, 'element']}"
                              for a in labels if annotators[a].at[sid, "element"])

        rows.append({
            # Order matters: SuspenseLens takes the FIRST column whose header contains a
            # keyword, so "character" must precede "character_anxiety_level", and no
            # later column may contain "sentence", "id", "character" or "element".
            "Sentence_ID": sid,
            "Sentence": text,
            "reader_suspense_level": int(r_lvl) if not pd.isna(r_lvl) else 0,
            "character": character,
            "character_anxiety_level": int(c_lvl) if not pd.isna(c_lvl) else 0,
            "suspense_evoking_element": elements,
            "R_votes": " ".join(f"{a}={'' if pd.isna(v) else int(v)}" for a, v in zip(reader_voters, r_vals)),
            "R_share_agreeing": round(r_top / r_n, 2) if r_n else np.nan,
            "C_votes": " ".join(f"{a}={'' if pd.isna(v) else int(v)}" for a, v in zip(char_voters, c_vals)),
            "C_share_agreeing": round(c_top / c_n, 2) if c_n else np.nan,
        })

    info = {
        "annotators": labels,
        "reader_voters": reader_voters,
        "char_voters": char_voters,
        "excluded_char": [a for a in labels if a not in char_voters],
        "excluded_reader": [a for a in labels if a not in reader_voters],
    }
    return pd.DataFrame(rows), info


# ── diagnostics ───────────────────────────────────────────────────────────
def agreement_rows(theory, annotators, gold):
    """Per-annotator agreement with the majority vote (exact match and mean abs. difference)."""
    g = gold.set_index("Sentence_ID")
    out = []
    for a, df in annotators.items():
        common = g.index.intersection(df.index)
        for dim, gcol in (("reader", "reader_suspense_level"), ("char_lvl", "character_anxiety_level")):
            pair = pd.DataFrame({"a": df.loc[common, dim], "g": g.loc[common, gcol]}).dropna()
            out.append({
                "theory": theory, "annotator": a,
                "dimension": "reader_suspense" if dim == "reader" else "character_anxiety",
                "n": len(pair),
                "exact_match_with_vote": round((pair.a == pair.g).mean(), 3) if len(pair) else np.nan,
                "mean_abs_diff_to_vote": round((pair.a - pair.g).abs().mean(), 3) if len(pair) else np.nan,
                "all_zero": bool(df[dim].fillna(0).eq(0).all()),
            })
    return out


def warn_duplicates(all_sheets):
    """Flag annotator sheets with near-identical reader levels (possible copy errors)."""
    for (k1, d1), (k2, d2) in itertools.combinations(all_sheets.items(), 2):
        common = d1.index.intersection(d2.index)
        same = (d1.loc[common, "reader"].fillna(-1) == d2.loc[common, "reader"].fillna(-1)).mean()
        if same >= DUPLICATE_WARN_THRESHOLD:
            print(f"  ! {k1} and {k2} agree on {same:.0%} of reader levels: check for a copied sheet")


# ── main ──────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-dir", default=".", help="folder with the T1_ ... T4_ .xlsx files")
    ap.add_argument("--output", default="gold_standard_SuspenseLens.xlsx")
    args = ap.parse_args()

    files = {}
    for p in sorted(Path(args.input_dir).glob("*.xlsx")):
        m = THEORY_RE.search(p.name)
        if m and "gold" not in p.name.lower():
            files[int(m.group(1))] = p
    if not files:
        raise SystemExit("No T1_ ... T4_ .xlsx files found in " + args.input_dir)

    golds, stats, all_sheets = {}, [], {}
    for t in sorted(files):
        annotators = read_theory_file(files[t])
        gold, info = build_theory_gold(annotators)
        golds[t] = gold
        stats += agreement_rows(f"T{t}", annotators, gold)
        all_sheets.update({f"T{t}{a}": df for a, df in annotators.items()})
        print(f"T{t}: {files[t].name}")
        print(f"  annotators: {', '.join(info['annotators'])}  ·  {len(gold)} sentences")
        if info["excluded_char"]:
            print(f"  character anxiety all 0, excluded from that vote: {', '.join(info['excluded_char'])}")
        print(f"  mean share agreeing with vote: reader {gold.R_share_agreeing.mean():.2f}, "
              f"character {gold.C_share_agreeing.mean():.2f}")
    warn_duplicates(all_sheets)

    with pd.ExcelWriter(args.output, engine="openpyxl") as xw:
        for t, gold in golds.items():
            gold.to_excel(xw, sheet_name=f"T{t}_gold", index=False)   # name must start with "T1" etc.
        pd.DataFrame(stats).to_excel(xw, sheet_name="agreement", index=False)
        for ws in xw.book.worksheets:
            ws.freeze_panes = "C2"
            for col in ws.columns:
                width = max(len(str(c.value or "")) for c in col[:50])
                ws.column_dimensions[col[0].column_letter].width = min(max(10, width + 2), 60)
    print(f"\nWrote {args.output}  (sheets: {', '.join(f'T{t}_gold' for t in golds)}, agreement)")


if __name__ == "__main__":
    main()
