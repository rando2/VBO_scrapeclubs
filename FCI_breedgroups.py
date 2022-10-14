import requests
from bs4 import BeautifulSoup
import pandas as pd
import spacy
from FCIFunctions import parse_rec_breed
from collections import OrderedDict
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
    fullApproval = pd.DataFrame(columns=["Breed", "Variety", "Country of Origin", "FCI Number", "Synonyms",
                                         "Source of Recognition Status", "Breed Group (FCI)",
                                         "FCI Recognition Status"])
    for ultag in pageContent.find_all('ul', {'class': "pays"}):
        for litag in ultag.find_all('li'):
            country = strip_numbered_list(litag.find('span').text)
            country_varieties = litag.find("div", {"class": "races"})
            breeds = OrderedDict()
            varieties = dict()
            for breeds_and_var in country_varieties.find_all('td'):
                # If it's a breed row, it will be a link. If it's a variety, it will just
                # be text. Therefore, test if it's a link to determine what kind of row
                # we are looking at
                link = breeds_and_var.find(href=True)
                if link is not None:
                    breedInfo = parse_rec_breed(link)
                    breeds[breedInfo[breed]] = breedInfo
                else:
                    breed = list(breeds.keys())[-1]
                    for var in breeds_and_var.find_all("td", {"class" : "variete"}):
                        var_list = varieties.get(breed, list())
                        varieties[breed] = var_list + [strip_numbered_list(var.find('span').text)]

            for breed in list(breeds.keys()):
                if breed in varieties.keys():
                    for variety in varieties[breed]:
                        continue
                        #fullApproval.loc[len(fullApproval.index)] = [breed.title(), variety.title(), country.title()] + \
                        #                 breeds[breed][1:] + \
                        #                 [group, "Definitive"]
                else:
                    continue
                    #fullApproval.loc[len(fullApproval.index)] = [breed.title(), "", country.title()] + \
                    #                 breeds[breed][1:] + \
                    #                 [group, "Definitive"]
    fullApproval.to_csv("rawdata/FCI_fullrecognition_" + group + ".tsv", sep='\t', index_label="Breed", index=False)
    print("Wrote TSV for FCI {0}".format(group))
