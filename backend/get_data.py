import requests
import time
import json
from newspaper import Article
import os
from dotenv import load_dotenv

load_dotenv()

def get_full_text(url, max_chars=800):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text[:max_chars].strip()
    except:
        return ""

API_KEY = os.getenv("GNEWS_API_KEY")
if not API_KEY:
    raise RuntimeError("❌ GNEWS_API_KEY not set in the environment!")

BASE_URL = "https://gnews.io/api/v4/top-headlines"
LANG = "en"
PAGE_SIZE = 3  # ⬅️ Reduced to 3 per category for memory control
PAUSE_SECONDS = 2

# Define varied queries to maximize uniqueness
queries = [
    {"category": "general"},
    {"category": "technology"},
    {"category": "science"},
    {"category": "business"},
    {"category": "entertainment"},
    {"category": "sports"},
    {"q": "AI"},
    {"q": "climate"},
    {"q": "startups"},
    {"q": "economy"},
]

all_articles = []
seen_urls = set()

try:
    for q in queries:
        params = {
            "lang": LANG,
            "max": PAGE_SIZE,
            "token": API_KEY,
            **q
        }

        print(f"\nFetching with params: {q}")
        response = requests.get(BASE_URL, params=params)
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", PAUSE_SECONDS))
            print(f"Rate limited. Retrying after {retry_after} seconds...")
            time.sleep(retry_after)
            response = requests.get(BASE_URL, params=params)

        response.raise_for_status()
        data = response.json()
        articles = data.get("articles", [])

        print(f"Found {len(articles)} articles. Extracting...")

        for article in articles:
            url = article['url']
            if url in seen_urls:
                continue
            seen_urls.add(url)

            content = article.get('content', "")[:800].strip()
            full_text = get_full_text(url)

            all_articles.append({
                "title": article["title"],
                "url": url,
                "text": full_text if full_text else content
            })

            time.sleep(1)

        time.sleep(PAUSE_SECONDS)

    # Save to JSON
    with open("articles.json", "w", encoding="utf-8") as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Successfully saved {len(all_articles)} unique articles to 'articles.json'.")

except requests.exceptions.RequestException as e:
    print(f"❌ Error calling GNews API: {e}")
except json.JSONDecodeError:
    print("❌ Failed to decode JSON from the response.")
    print("Response text:", response.text)
