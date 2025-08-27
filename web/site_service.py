import webbrowser
import json
import os

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "sites.json")

def load_sites():
    """Load site mappings from JSON config"""
    if not os.path.exists(CONFIG_FILE):
        default = {
            "youtube": "https://www.youtube.com",
            "gmail": "https://mail.google.com",
            "google": "https://www.google.com",
            "reddit": "https://www.reddit.com",
            "twitter": "https://twitter.com",
            "linkedin": "https://www.linkedin.com",
            "github": "https://github.com"
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(default, f, indent=4)
        return default

    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def open_site(site_name):
    """Open a known website from config"""
    sites = load_sites()
    site_name = site_name.lower().strip()

    if site_name in sites:
        url = sites[site_name]
        print(f"🌐 Opening site: {url}")
        webbrowser.open(url)
        return url
    else:
        print(f"⚠️ Unknown site: {site_name}")
        return None