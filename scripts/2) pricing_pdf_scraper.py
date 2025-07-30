# File: scripts/pricing_finder.py

# 📦 Imports
from urllib.parse import urljoin
import pandas as pd
from serpapi import GoogleSearch  
from playwright.sync_api import sync_playwright
import os
import requests
from dotenv import load_dotenv
load_dotenv()
# 🔐 SerpAPI Key and keywords used in fallback strategy
SEARCH_API_KEY = os.getenv("SEARCH_API_KEY")
KEYWORDS = ["pricing", "cost", "rates"]

# ✅ Filter if a given page or URL is relevant for pricing info
def is_valid_result(url, content):
    if not url:
        return False
    if url.lower().endswith(".pdf"):
        return True
    if content:
        text = content.lower()
        return any(kw in text for kw in ["price", "package", "fee", "$"])
    return False

# 🔍 Run a Google search using SerpAPI
def run_google_search(query):
    params = {
        "engine": "google",
        "q": query,
        "api_key": SEARCH_API_KEY,
        "num": 5  # Limit to top 5 results
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    print(f"🔍 Query: {query}")
    return results.get("organic_results", [])

# 🌐 Playwright-based page content fetcher with PDF detection
def fetch_page_content_with_links(url, download_dir="downloads"):
    os.makedirs(download_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False) 
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            extra_http_headers={  # Spoof headers to mimic real browser
                "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "upgrade-insecure-requests": "1"
            }
        )
        page = context.new_page()
        try:
            # 🔎 Visit target URL
            page.goto(url, timeout=15000)
            page.wait_for_timeout(2000)
            content = page.content()

            hrefs = []
            golden_pdf_url = None

            # 🔗 Extract all links and check for pricing-related PDFs
            for link in page.locator("a").all():
                href = link.get_attribute("href")
                if not href:
                    continue

                full_url = urljoin(url, href)

                # 🎯 Prioritize direct cost-related PDFs
                if full_url.lower().endswith(".pdf") and any(
                    kw in full_url.lower() for kw in ["cost", "price", "package", "fees", "charges"]
                ):
                    golden_pdf_url = full_url
                    break  # Exit once golden link found

                hrefs.append(full_url)

            # 📄 If PDF found, download it
            if golden_pdf_url:
                filename = os.path.basename(golden_pdf_url.split("?")[0])
                filepath = os.path.join(download_dir, filename)
                try:
                    response = requests.get(golden_pdf_url, timeout=10)
                    with open(filepath, "wb") as f:
                        f.write(response.content)
                    print(f"✅ Downloaded PDF: {filename}")
                    return content, [golden_pdf_url], "downloads"
                except Exception as e:
                    print(f"❌ Failed to download PDF: {e}")
                    return content, [golden_pdf_url], None

            # 📸 If no PDF found, save screenshot for manual review
            screenshot_path = os.path.join(download_dir, f"{provider}.png")
            page.screenshot(path=screenshot_path)
            print(f"📸 Screenshot saved: {screenshot_path}")

            return content, hrefs, None

        except Exception as e:
            print(f"❌ Page load error: {e}")
            return None, [], None
        finally:
            browser.close()

# 🧠 Smart fallback: use Google Search + page scraping to find pricing
def smart_fallback_search(provider_name):
    tried_queries = []

    # 🔍 First broad query combining common keywords
    broad_query = f"{provider_name} home care pricing OR cost OR rates"
    tried_queries.append(broad_query)
    results = run_google_search(broad_query)

    # 🔁 Iterate through results and sub-links
    for r in results:
        link = r.get("link")
        try:
            content, hrefs, downloaded_pdf_path = fetch_page_content_with_links(link)
            if is_valid_result(link, content):
                return {"provider": provider_name, "url": link, "strategy": "broad query", "query": broad_query}

            for href in hrefs:
                sub_content, _, _ = fetch_page_content_with_links(href)
                if is_valid_result(href, sub_content):
                    return {"provider": provider_name, "url": href, "strategy": "sub-link", "query": broad_query}
        except Exception as e:
            print(f"⚠️ Error during processing link: {link}, {e}")

    # 🔁 Fallback: search individually with specific keywords
    for keyword in KEYWORDS:
        q = f"{provider_name} home care {keyword}"
        tried_queries.append(q)
        results = run_google_search(q)
        for r in results:
            link = r.get("link")
            try:
                content, hrefs, _ = fetch_page_content_with_links(link)
                if is_valid_result(link, content):
                    return {"provider": provider_name, "url": link, "strategy": f"fallback: {keyword}", "query": q}

                for href in hrefs:
                    sub_content, _, _ = fetch_page_content_with_links(href)
                    if is_valid_result(href, sub_content):
                        return {"provider": provider_name, "url": href, "strategy": f"fallback: {keyword} (sub-link)", "query": q}
            except Exception as e:
                print(f"⚠️ Error during fallback search: {link}, {e}")

    # ❌ If nothing found after all attempts
    return {"provider": provider_name, "url": None, "strategy": "not found", "tried": tried_queries}

# 🔁 Entry Point — Process top 30 providers from CSV
if __name__ == "__main__":
    try:
        df = pd.read_csv("data/unique_providers.csv") 
        top_30 = df.head(30)

        for index, row in top_30.iterrows():
            provider = str(row["Provider Name"]).strip()
            print(f"\n🔄 [{index+1}] Processing: {provider}")
            result = smart_fallback_search(provider)
            print(result)

    except Exception as e:
        print(f"❌ Failed to load or process CSV: {e}")
