import os
import pandas as pd
import spacy
from scrapeFunctions import retrieve_html
from bs4 import BeautifulSoup
import csv


pageContent = retrieve_html("https://en.wikipedia.org/wiki/List_of_dog_breeds")
breedgroupInfo = pageContent.find("div", {"class": "div-col"})
breeds = list()
for litag in breedgroupInfo.find_all('li'):
    linkInfo = litag.find(href=True)
    breed = linkInfo.text
    url = "https://en.wikipedia.org" + linkInfo['href']
    breeds.append([breed, url])

with open("rawdata/wiki.csv", "w",  newline="") as f:
    writer = csv.writer(f)
    writer.writerows(breeds)

