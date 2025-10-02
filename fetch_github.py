# fetch_github.py
import os, base64, json, time
from typing import List, Dict
import requests
from rich import print
from tqdm import tqdm

API = "https://api.github.com"
TOKEN = os.getenv("GITHUB_TOKEN", "")
HEADERS = {"Accept": "application/vnd.github+json"}
if TOKEN:
    HEADERS["Authorization"] = f"Bearer {TOKEN}"

EXCLUDE_FORKS = True

def get_repos(user: str) -> List[Dict]:
    repos = []
    page = 1
    while True:
        r = requests.get(
            f"{API}/users/{user}/repos",
            params={"per_page": 100, "page": page, "type": "owner", "sort": "updated"},
            headers=HEADERS
        )
        r.raise_for_status()
        data = r.json()
        if not data:
            break
        for repo in data:
            if EXCLUDE_FORKS and repo.get("fork"):
                continue
            repos.append({
                "name": repo["name"],
                "full_name": repo["full_name"],
                "html_url": repo["html_url"],
                "description": repo.get("description") or "",
                "stargazers_count": repo.get("stargazers_count", 0),
                "language": repo.get("language") or "",
                "topics": fetch_topics(repo["full_name"]),
                "readme": fetch_readme(repo["full_name"]) or "",
                "updated_at": repo.get("updated_at", ""),
            })
        page += 1
        time.sleep(0.1)
    return repos

def fetch_topics(full: str) -> List[str]:
    r = requests.get(
        f"{API}/repos/{full}/topics",
        headers={**HEADERS, "Accept": "application/vnd.github.mercy-preview+json"}
    )
    if r.status_code != 200:
        return []
    return r.json().get("names", [])

def fetch_readme(full: str) -> str:
    r = requests.get(f"{API}/repos/{full}/readme", headers=HEADERS)
    if r.status_code != 200:
        return ""
    try:
        content = base64.b64decode(r.json()["content"]).decode("utf-8", errors="ignore")
    except Exception:
        return ""
    return content

# === Partie manquante ===
if __name__ == "__main__":
    import argparse, pathlib
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", required=True)
    ap.add_argument("--out", default="out/raw_repos.json")
    args = ap.parse_args()

    pathlib.Path("out").mkdir(exist_ok=True)
    repos = get_repos(args.user)
    print(f"Found {len(repos)} repos for {args.user}")

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(repos, f, ensure_ascii=False, indent=2)

    print(f"[green]Saved[/green] {len(repos)} repos to {args.out}")


