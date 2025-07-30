# 🧠 Aged Care Automation Suite

A Python-based solution to streamline the collection of public aged care data from government and provider websites.  
It helps reduce manual effort by programmatically gathering, extracting, and logging useful provider information.

---

## 🔍 What It Does

This suite automates the following processes:

- ✅ **Compliance Report Downloads**  
  Automatically fetches `.docx` compliance reports from government service pages based on provider info.

- ✅ **Pricing Document Discovery**  
  Uses Google search and browser automation to locate downloadable **pricing PDFs** from provider websites.  
  If not found, it saves a **page snapshot** for reference.

- ✅ **Star Rating Extraction** *(if included)*  
  Collects provider-level performance ratings from agedcarequality.gov.au (modular).

- ✅ **Structured Google Sheet Logging**  
  All relevant metadata and links are logged directly into a connected Google Sheet for easy access and record-keeping.

---

## ⚙️ Technology

- Python + Playwright for browser automation  
- Google Sheets API for real-time logging  
- SerpAPI for intelligent Google fallback  
- Requests, Pandas, and BeautifulSoup for parsing and data handling

---

## 🔐 Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
