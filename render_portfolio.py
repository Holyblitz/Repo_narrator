# render_portfolio.py
import json, datetime
from pathlib import Path

def to_md(items):
    lines = [
        "# GitHub Projects — Portfolio Blurbs",
        "",
        f"_Auto-generated on {datetime.date.today().isoformat()}_",
        ""
    ]
    for it in items:
        stars = f"⭐ {it['stars']}" if it.get("stars", 0) else ""
        topics = ", ".join(it.get("topics", [])[:6])
        meta = " · ".join([m for m in [it.get("lang", ""), stars, topics] if m])
        lines.append(f"## [{it['name']}]({it['url']})")
        if meta:
            lines.append(f"**{meta}**")
        lines.append("")
        lines.append(it["blurb"])
        lines.append("")
    return "\n".join(lines)

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--infile", default="out/summaries.json")
    ap.add_argument("--outfile", default="out/portfolio.md")
    args = ap.parse_args()

    with open(args.infile, "r", encoding="utf-8") as f:
        items = json.load(f)

    md = to_md(items)
    Path(args.outfile).parent.mkdir(exist_ok=True)
    with open(args.outfile, "w", encoding="utf-8") as f:
        f.write(md)

    print(f"Wrote {args.outfile}")

