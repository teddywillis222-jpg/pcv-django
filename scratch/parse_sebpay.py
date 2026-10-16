import requests
from bs4 import BeautifulSoup
import re
import json

urls = [
    "https://new.sebpay.bj/fr/docs/auth",
    "https://new.sebpay.bj/fr/docs/collections",
    "https://new.sebpay.bj/fr/docs/webhooks",
    "https://new.sebpay.bj/fr/docs/status-codes",
]

for url in urls:
    print(f"\n====================== {url} ======================")
    try:
        r = requests.get(url, timeout=10)
        # Search for json next data or main text
        soup = BeautifulSoup(r.text, 'html.parser')
        main = soup.find('main')
        if main:
            print("MAIN TEXT:")
            print(main.get_text(separator="\n", strip=True)[:1500])
        else:
            # Look in next_f scripts
            scripts = soup.find_all('script')
            for s in scripts:
                if s.string and 'self.__next_f.push' in s.string:
                    # extract snippets with endpoints or curl or Authorization
                    matches = re.findall(r'(https?://[^\s"\\]+|/api/[^\s"\\]+|Bearer[^\s"\\]+|POST|GET)', s.string)
                    if matches:
                        print("MATCHES:", set(matches[:20]))
    except Exception as e:
        print(f"Error fetching {url}: {e}")
