import webbrowser
import urllib.parse
import json
import os

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "search_engines.json")

def load_engines():
    """Load search engines from JSON config"""
    if not os.path.exists(CONFIG_FILE):
        # default engines
        default = {
            "google": "https://www.google.com/search?q={}",
            "duckduckgo": "https://duckduckgo.com/?q={}",
            "bing": "https://www.bing.com/search?q={}"
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(default, f, indent=4)
        return default

    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def search_web(query, engine="google"):
    """Perform a web search using the chosen engine"""
    engines = load_engines()
    engine = engine.lower()

    if engine not in engines:
        print(f"⚠️ Unknown engine: {engine}. Defaulting to Google.")
        engine = "google"

    encoded_query = urllib.parse.quote(query)
    url = engines[engine].format(encoded_query)

    print(f"🌐 Searching via {engine}: {url}")
    webbrowser.open(url)
    return url