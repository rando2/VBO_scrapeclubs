import re
from bs4 import BeautifulSoup
import requests

def retrieve_html(URL):
    """Pulls HTML from IDog and identify the block containing breed info based on
    div tag (ad hoc)
    Input: string
    Returns: string"""
    # To do: streamline this function across whole project
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    return soup

def parse_FCI_breed(link):
    # The names are structured as DOGNAME (##) (ALT NAME)
    # There can be extraneous parentheses in the names, so split based on the ID #
    id_match = re.search(r'\([0-9]+\)', link.text)
    bounds = id_match.span()
    breed = link.text[:bounds[0]].strip()
    try:
        alt_name = link.text[bounds[1]:].strip()[1:-1]
    except AttributeError:
        alt_name = ""
    return {"breed": breed,
            "number": id_match.group()[1:-1],
            "synonyms": alt_name.title(),
            "url": "https://www.fci.be" + link["href"]}

