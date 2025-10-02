# generate_summaries.py
import os, json
from typing import Dict
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from utils_text import set_seed, clean_text, truncate_tokens

PROMPT_TMPL = (
    "You are a helpful assistant that writes concise, upbeat blurbs about GitHub repos.\n"
    "Write a 2-3 sentence summary for the repo below, focusing on what it does and the tech stack.\n\n"
    "Repo name: {name}\n"
    "Main language: {lang}\n"
    "Topics: {topics}\n"
    "Short description: {desc}\n"
    "README excerpt: {readme}\n\n"
    "Blurb:"
)

@torch.no_grad()
def generate_blurb(tok, model, meta: Dict, max_new_tokens=90, temperature=0.8, top_p=0.92):
    prompt = PROMPT_TMPL.format(
        name=meta.get("name",""),
        lang=meta.get("language","") or "mixed",
        topics=", ".join(meta.get("topics", [])[:8]) or "",
        desc=(meta.get("description") or "")[:180],
        readme=(truncate_tokens(clean_text(meta.get("readme","")), max_chars=800)),
    )
    inputs = tok(prompt, return_tensors="pt").to(model.device)
    out = model.generate(
        **inputs,
        do_sample=True,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        top_p=top_p,
        pad_token_id=tok.eos_token_id
    )
    text = tok.decode(out[0], skip_special_tokens=True)
    blurb = text.split("Blurb:")[-1].strip()
    # stop at double newline if present
    blurb = blurb.split("\n\n")[0].strip()
    # light post-processing
    if not blurb.endswith(('.', '!', '?')):
        blurb += '.'
    return blurb

if __name__ == "__main__":
    import argparse, pathlib
    ap = argparse.ArgumentParser()
    ap.add_argument("--infile", default="out/raw_repos.json")
    ap.add_argument("--outfile", default="out/summaries.json")
    ap.add_argument("--model", default="distilgpt2")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    pathlib.Path("out").mkdir(exist_ok=True)
    with open(args.infile, "r", encoding="utf-8") as f:
        repos = json.load(f)

    set_seed(args.seed)
    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(args.model)
    model.to("cuda" if torch.cuda.is_available() else "cpu")

    out = []
    for r in repos:
        blurb = generate_blurb(tok, model, r)
        out.append({
            "name": r["name"],
            "url": r["html_url"],
            "blurb": blurb,
            "stars": r["stargazers_count"],
            "lang": r["language"],
            "topics": r["topics"]
        })
        print(f"✔ {r['name']}: {blurb[:80]}…")

    with open(args.outfile, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(out)} blurbs to {args.outfile}")

