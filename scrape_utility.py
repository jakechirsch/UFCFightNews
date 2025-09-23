# Imports
from urllib.parse import unquote
from bs4 import BeautifulSoup
import requests

# This function creates the parameters to pass to a request
def get_params(page):
    return {
        "action": "parse",
        "page": page,
        "format": "json",
        "prop": "text"
    }

# This function gets the HTML for a page with the provided params
def get_html(params):
    url = "https://en.wikipedia.org/w/api.php"
    headers = {
        "User-Agent": "UFCFightNews/0.1 (jchirsch@umich.edu)"
    }

    r = requests.get(url, params=params, headers=headers)
    data = r.json()
    html = data["parse"]["text"]["*"]
    return BeautifulSoup(html, "html.parser")

# This functon gets the event title from the full href
def get_title(link):
    if link.startswith("/wiki/"):
        return unquote(link.split("/wiki/")[-1].split("#")[0])
    return None