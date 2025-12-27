import requests
import sys

REPO = "lolelarap8/server-08-worker"
TOKEN = "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"

def check_status():
    url = f"https://api.github.com/repos/{REPO}/actions/permissions"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    print(f"Checking status for {REPO}...")
    resp = requests.get(url, headers=headers)
    
    print(f"Status Code: {resp.status_code}")
    print(f"Response: {resp.text}")

if __name__ == "__main__":
    check_status()
