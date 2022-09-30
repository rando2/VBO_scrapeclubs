import requests
import os
from bs4 import BeautifulSoup
import pandas as pd
import spacy
import re

def retrieve_html(URL):
    """Pulls HTML from IDog and identify the block containing breed info based on
    div tag (ad hoc)
    Input: string
    Returns: string"""
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    return soup

if __name__ == '__main__':
    url = "https://www.fci.be/en/Nomenclature/"
    pageContent = retrieve_html(url)

    # First, identify URL and pull data by breed group for recognized dogs
    breedgroupInfo = pageContent.find("ul", {"class": "grouplist"})
    for litag in breedgroupInfo.find_all('li'):
        linkInfo = litag.find(href=True)
        groupName = litag.find("span").text
        run_command = "python  FCI_breedgroups.py '{0}' '{1}'".format(linkInfo['href'], groupName)
        print(run_command)
        os.system(run_command)
        exit(0)


