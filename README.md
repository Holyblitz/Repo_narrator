# Repo_narrator

# Repo Narrator 📝

**Repo Narrator** is a text generation project that automatically summarizes your GitHub repositories.  
It fetches metadata, topics and READMEs from the GitHub API, generates concise blurbs using a language model, and exports them as a clean Markdown portfolio.

---

## 🚀 Features
- Fetch repositories via the **GitHub REST API** (with optional token authentication).
- Extract metadata: name, description, language, stars, topics, README excerpts.
- Summarize each repo with a **language model** (`distilgpt2` by default).
- Export the portfolio as **Markdown** for direct use in GitHub profiles or LinkedIn.
- Modular pipeline: `fetch → summarize → render`.

---

## 📂 Project Structure
- `fetch_github.py` → Download repos & READMEs into `raw_repos.json`
- `generate_summaries.py` → Summarize repos into `summaries.json`
- `render_portfolio.py` → Render Markdown portfolio (`portfolio.md`)
- `utils_text.py` → Helpers (cleaning, seeding, truncation)

---

## 🔧 Installation
```bash
git clone https://github.com/Holyblitz/repo_narrator.git
cd repo_narrator
pip install -r requirements.txt
