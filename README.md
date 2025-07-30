# aged-care-automation
🧠 Aged Care Automation Suite
This project automates four key data collection tasks from public Australian aged care sources:

✅ Extracting government star ratings

✅ Downloading compliance reports in .docx format

✅ Locating and downloading home care pricing PDFs

✅ Logging everything automatically to a Google Sheet

⚙️ Technologies Used
Python + Playwright (headless browser automation)

Google Sheets API (for central logging)

SerpAPI (intelligent Google fallback for pricing)

requests, pandas, BeautifulSoup

🗂️ Project Structure
bash
Copy
Edit
AGED_CARE_AUTOMATION/
├── data/                    # Input CSVs (provider lists)
├── downloads/              # Saved compliance reports, PDFs, screenshots
├── scripts/
│   ├── download_compliance_report.py  # Automates .docx compliance downloads
│   ├── pricing_finder.py              # Finds pricing via smart Google search
│   └── [other automation modules]
├── credentials/            # Place your Google credentials here (gitignored)
├── .env                    # Your local API keys (gitignored)
├── .env.template           # Safe template for others
├── .gitignore
└── README.md
🔐 Setup Instructions
⚠️ Required before running: Python 3.10+ and Chrome/Edge installed

1. Clone the Repo
bash
Copy
Edit
git clone https://github.com/deku-3/aged-care-automation.git
cd aged-care-automation
2. Install Requirements
bash
Copy
Edit
pip install -r requirements.txt
3. Configure Environment Variables
Copy the environment template:

bash
Copy
Edit
cp .env.template .env
Fill in your .env with:

Your SerpAPI key

Your Google Sheet ID

Your path to credentials.json

4. Place Your Google Credentials
Save your Google service account file as:

bash
Copy
Edit
credentials/credentials.json
5. Run the Automations
Each script can be run independently:

bash
Copy
Edit
# Download .docx compliance reports for top 30 providers
python scripts/download_compliance_report.py

# Fetch pricing PDFs using Google + Playwright
python scripts/pricing_finder.py
You can customize which providers to target by editing the CSVs in the data/ folder.

📊 Output
📁 downloads/: All scraped files, PDFs, and screenshots

📄 Google Sheet: Logs provider, suburb, postcode, and source URL
