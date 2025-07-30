# File: scripts/download_compliance_report.py

# 📦 Imports
import os
import pandas as pd
from urllib.parse import urlencode, urljoin
from playwright.sync_api import sync_playwright
import requests

from googleapiclient.discovery import build
from google.oauth2 import service_account
from dotenv import load_dotenv
load_dotenv()
# 🌐 Aged Care Website Base URLs
BASE_URL = "https://www.agedcarequality.gov.au/service-and-reports"
BASE_DETAIL_URL = "https://www.agedcarequality.gov.au"

# 📁 Directory to save downloaded compliance reports
DOWNLOAD_DIR = "downloads/compliance_reports"

# 🔐 Google Sheets API Configuration

SERVICE_ACCOUNT_FILE=os.getenv('SERVICE_ACCOUNT_FILE')
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID=os.getenv('SPREADSHEET_ID')
SHEET_NAME = 'Sheet1'

# 📄 Logs provider details and download link to Google Sheet
def log_to_sheet_only(provider, suburb, postcode, file_url):
    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
        sheets_service = build('sheets', 'v4', credentials=credentials)
        row = [[provider, suburb, postcode, file_url]]
        sheets_service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SHEET_NAME}!A:D",
            valueInputOption="USER_ENTERED",
            body={"values": row}
        ).execute()
    except Exception as e:
        print(f"❌ Google Sheets logging failed: {e}")

# 🧠 Main function to download compliance report for a given provider
def download_compliance_report(provider, suburb, postcode):
    # Build search URL with query parameters
    query_params = {
        "field_acqsc_report_provider_name": provider,
        "field_acqsc_service_postcode": postcode,
        "field_acqsc_service_suburb": suburb,
        "sort_by": "title"
    }
    search_url = f"{BASE_URL}?{urlencode(query_params)}"

    try:
        with sync_playwright() as p:
            # 🚀 Launch headless browser and spoof headers to avoid bot detection
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
                extra_http_headers={
                    "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": '"Windows"',
                    "upgrade-insecure-requests": "1"
                }
            )
            page = context.new_page()

            # 🔎 Load search results page
            page.goto(search_url, wait_until="domcontentloaded", timeout=30000)

            try:
                # 🔗 Find the first service link on the page
                href = page.locator("a[href^='/services/']").first.get_attribute("href")
                if not href:
                    print(f"❌ No service detail page found for {provider}")
                    return None

                detail_url = urljoin(BASE_DETAIL_URL, href)
                print(f"🌐 Opening service page: {detail_url}")

                # 🌐 Open service detail page
                detail_page = context.new_page()
                detail_page.goto(detail_url, wait_until="domcontentloaded", timeout=3000)

                # 📄 Locate the .docx compliance report link
                docx_link = detail_page.locator("a[href$='.docx']").first
                href = docx_link.get_attribute("href")
                if not href:
                    print(f"❌ No .docx link found for {provider}")
                    return None

                full_url = urljoin(BASE_DETAIL_URL, href)

                # 🧾 Define headers for the file download request
                headers = {
                    "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": '"Windows"',
                    "upgrade-insecure-requests": "1",
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"
                }

                try:
                    # 📁 Create download directory if not exists
                    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

                    # 🧼 Safe filename formatting
                    safe_provider = provider.replace(" ", "_").replace("&", "and")
                    filename = f"{safe_provider}_{suburb}_{postcode}.docx"
                    save_path = os.path.join(DOWNLOAD_DIR, filename)

                    # ⬇️ Download the file
                    r = requests.get(full_url, headers=headers, timeout=30)
                    with open(save_path, "wb") as f:
                        f.write(r.content)

                    print(f"✅ Downloaded: {filename}")

                    # 📊 Log the result to Google Sheet
                    log_to_sheet_only(provider, suburb, postcode, full_url)

                except Exception as e:
                    print(f"❌ Download error for {provider}: {e}")

            except Exception as e:
                print(f"❌ Service page error for {provider}: {e}")

            finally:
                browser.close()

    except Exception as e:
        print(f"❌ Browser setup failed for {provider}: {e}")

    return None


# 🔁 Entry point — for batch or single provider test
if __name__ == "__main__":
    try:
        # 🔁 Loop over top 30 providers from CSV (Uncomment for batch mode)
        df = pd.read_csv("data/filtered_providers_for_compliance.csv")  # Columns: Provider Name, Suburb, Postal Code
        top_30 = df.head(30)
        for index, row in top_30.iterrows():
            provider = str(row["Provider Name"]).strip()
            suburb = str(row["Suburb"]).strip()
            postcode = str(row["Postal Code"]).strip()
            print(f"\n🔄 [{index+1}] Processing: {provider} | {suburb} | {postcode}")
            download_compliance_report(provider, suburb, postcode)

        # 🧪 Test with a single provider
        # download_compliance_report(
        #     provider='KinCare Health Services Pty Ltd',
        #     suburb='DEAKIN',
        #     postcode='2600'
        # )

    except Exception as e:
        print(f"❌ Failed to load or process CSV: {e}")
