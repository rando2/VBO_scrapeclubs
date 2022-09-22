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

def identifyFields(fieldIDs, text):
    """Extract basic breed information from below photo (ad hoc)
    May be able to use fuzzywuzzy to make more robust
    input:
          dictionary: fields (keys) and exact text demarcating fields (values)
          string: .text of relevant section of html
    returns:
          dictionary: fields (keys of input dictionary) with the values extracted
          Unless page is empty, in which case it returns None

    Note: should we switch to fuzzy replacement?
    See: https://www.imranabdullah.com/2021-09-17/Fuzzy-word-replace-from-string-in-Python
    """
    extractedInfo = dict()
    lines = [line.strip() for line in text.splitlines() if len(line.strip()) > 0]
    if lines[0] == 'Web Source Name:':
        return None

    for field, fieldDesc in fieldIDs.items():
        scores = list()
        for line in lines:
            if len(line) > 0:
                scores.append(fuzz.partial_ratio(fieldDesc, line))
        match = lines[scores.index(max(scores))]
        extractedInfo[field] = match.replace(fieldDesc, "")
    return extractedInfo

def parse_recognition(text):
    clubNames = list()
    clubLinks = list()
    for thtag in text.find_all('th'):
        clubNames.append(thtag.text)
    for tdtag in text.find_all('td'):
        link = tdtag.find(href=True)
        clubLinks.append(link['href'])
    return dict(zip(clubNames, clubLinks))

if __name__ == '__main__':
    i = 1
    while i != 0:
        breedData = retrieve_html("https://ngdc.cncb.ac.cn/idog/breed/getBreedDetail.action?breedId=" +
                                  str(i))

        # The "find" functions use the html coding I identified just by looking at the page source
        # There are two separate sections demarcated with div. The text used to
        basicInfoRaw = breedData.find("div", {"class": "col-xs-12 col-sm-4 col-sm-offset-1"}).text
        basicInfo = identifyFields({"breed name":"Web Source Name: ",
                                    "breed name source": "from ",
                                    "other name": "Other Name: ",
                                    "common name": "Common Name: "}, basicInfoRaw)
        if basicInfo is None:
            i = 0
            continue
        detailInfoRaw = breedData.find("div", {"class": "col-xs-12 col-sm-7"}).text
        basicInfo.update(identifyFields({"iDog identifier": "iDog Breed Number: ",
                                         "origin": "Original: "}, detailInfoRaw))
        recognitionInfoRaw = breedData.find("div", {"class": "table-responsive"})
        basicInfo["recognition"] = parse_recognition(recognitionInfoRaw)
        print(basicInfo)
        i+=1
        break