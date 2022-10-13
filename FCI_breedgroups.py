import requests
from bs4 import BeautifulSoup
import pandas as pd
import spacy
from FCIFunctions import parse_rec_breed
import sys

def retrieve_html(URL):
    """Pulls HTML from IDog and identify the block containing breed info based on
    div tag (ad hoc)
    Input: string
    Returns: string"""
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    return soup.find("div", {"class": "contenu nomenclature"})

def strip_numbered_list(text):
    """Use spacy to strip numbers and punctuation from li"""
    nlp = spacy.load('en_core_web_lg')
    parsed_doc = nlp(text)
    parts = [token.pos_ for token in parsed_doc]
    entry = parsed_doc[parts.index("PUNCT") + 1:].text_with_ws
    return entry


if __name__ == '__main__':
    url, group = sys.argv[1:]
    url_base = 'https://www.fci.be'
    pageContent = retrieve_html(url_base + url)
    fullApproval = dict()
    for ultag in pageContent.find_all('ul', {'class': "pays"}):
        #country = ""
        for litag in ultag.find_all('li'):
            country = strip_numbered_list(litag.find('span').text)
            breeds = litag.find("div", {"class": "races"})
            for tdtag in breeds.find_all('td'):
                link = tdtag.find(href=True)
                print(tdtag)
                exit(0)
                if link:
                    dogInfo = parse_rec_breed(link)
                    fullApproval[dogInfo[0].title()] = [country.title()] + \
                                                       dogInfo[1:] + \
                                                       [group, "Definitive"]

    for key, value in fullApproval.items():
        print(key, "|", " | ".join(value))
    df = pd.DataFrame.from_dict(fullApproval, orient='index', columns=["Country of Origin", "FCI Number", "Synonyms",
                                                                       "Source of Recognition Status",
                                                                       "Breed Group (FCI)",
                                                                       "FCI Recognition Status"])
    df.to_csv("rawdata/FCI_fullrecognition_" + group + ".tsv", sep='\t', index_label="Breed")
    print("Wrote TSV for FCI {0}".format(group))
