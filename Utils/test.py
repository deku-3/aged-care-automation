import requests

headers = {
    "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"
}

url = "https://www.agedcarequality.gov.au/sites/default/files/media/BaptistCare%20-%20ACT200952-0.docx"

try:
    r = requests.get(url, headers=headers, timeout=30)
    with open("downloaded_file.docx", "wb") as f:
        f.write(r.content)
    print("✅ Downloaded!")
except Exception as e:
    print("❌ Failed:", e)
