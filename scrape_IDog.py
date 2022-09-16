import requests
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz
import pandas as pd

def retrieve_html(URL):
    """Pulls HTML from IDog and identify the block containing breed info based on
    div tag (ad hoc)
    Input: string
    Returns: string"""
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    return soup.find("div", {"class": "col-xs-12 col-sm-12 col-md-9"})

def eval_basic_info(text):
    """Extract basic breed information from below photo (ad hoc)
    May be able to use fuzzywuzzy to make more robust
    input: string
    returns:"""
    lines = text.splitlines()
    breedInfo = list()
    for line in text.splitlines():
        line = line.strip()
        if len(line) > 0:
            breedInfo.append(line)
    print(breedInfo)


i = 1
while i <2:
    breedData = retrieve_html("https://ngdc.cncb.ac.cn/idog/breed/getBreedDetail.action?breedId=" +
                              str(i))
    basicInfo = eval_basic_info(breedData.find("div", {"class": "col-xs-12 col-sm-4 col-sm-offset-1"}).text)

    #print("*****")
    #print(breedData)
    i+=1