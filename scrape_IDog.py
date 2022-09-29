import requests
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz
import pandas as pd
import spacy

def retrieve_html(URL):
    """Pulls HTML from IDog and identify the block containing breed info based on
    div tag (ad hoc)
    Input: string
    Returns: string"""
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    return soup.find("div", {"class": "col-xs-12 col-sm-12 col-md-9"})

def parse_fields(text):
    """Use spacy to identify text of entry in a form"""
    nlp = spacy.load('en_core_web_lg')
    parsed_doc = nlp(text)
    parts = [token.pos_ for token in parsed_doc]
    entry = parsed_doc[parts.index("PUNCT")+1:].text_with_ws
    return entry

def parse_list(text):
    """Use spacy to identify items in a list separated by punctuation"""
    print(parsed_doc)
    items = list()
    punc = [i for i in range(len(parsed_doc)) if parsed_doc[i].pos_ == "PUNCT"]
    if len(punc) == 0:
        return [parsed_doc]
    else:
        start = 0
        for pmarkindex in punc:
            items.append(parsed_doc[start:pmarkindex])
            start = pmarkindex + 1
        if start < len(parsed_doc):
            items.append(parsed_doc[start:])
        print(items)
        #return entry

def identifyFields(fieldIDs, text):
    """Extract basic breed information from below photo (ad hoc)
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
    if lines[0] == "Web Source Name: ":
        return None

    for field, fieldDesc in fieldIDs.items():
        scores = list()
        for line in lines:
            if len(line) > 0:
                scores.append(fuzz.partial_ratio(fieldDesc, line))
        match = lines[scores.index(max(scores))]
        if field != "breed name source":
            extractedInfo[field] = parse_fields(match)
        else:
            extractedInfo[field] = match.replace("from ", "")
    return extractedInfo

def parse_recognition(text):
    clubNames = list()
    clubLinks = list()
    for thtag in text.find_all('th'):
        clubNames.append(thtag.text)
    for tdtag in text.find_all('td'):
        link = tdtag.find(href=True)
        if link:
            clubLinks.append(link['href'])
        else:
            clubLinks.append("")
    return dict(zip([clubNames[i] for i, x in enumerate(clubLinks) if x != ""],
                    [l for l in clubLinks if l != ""]))

if __name__ == '__main__':
    # Define dictionaries to store data
    breed_summary = dict()
    approval_data = dict()

    # Iterate through entries in iDog database
    i = 2
    while i != 0 and i < 10:
        url = "https://ngdc.cncb.ac.cn/idog/breed/getBreedDetail.action?breedId=" + str(i)
        breedData = retrieve_html(url)

        # The "find" functions use the html coding I identified just by looking at the page source
        # There are two separate sections demarcated with div. The text used to
        basicInfoRaw = breedData.find("div", {"class": "col-xs-12 col-sm-4 col-sm-offset-1"}).text
        basicInfo = identifyFields({"breed name": "Web Source Name:",
                                    "breed name source": "from ",
                                    "other name": "Other Name:",
                                    "common name": "Common Name:"}, basicInfoRaw)
        if basicInfo is None:
            i = 0
            continue
        parse_list(basicInfo["common name"])
        print(parse_list(basicInfo["other name"]))
        exit(0)

        # Now extract iDog info
        detailInfoRaw = breedData.find("div", {"class": "col-xs-12 col-sm-7"}).text
        basicInfo.update(identifyFields({"iDog identifier": "iDog Breed Number: ",
                                         "origin": "Original: "}, detailInfoRaw))
        recognitionInfoRaw = breedData.find("div", {"class": "table-responsive"})
        basicInfo["recognition"] = parse_recognition(recognitionInfoRaw)

        breed_summary[basicInfo["breed name"]] = [
            basicInfo['iDog identifier'], url, basicInfo["other name"] + "," + basicInfo["common name"]
        ]
        for org, URL in basicInfo.items():
            orgdict = approval_data.get(org, dict())
            orgdict["breed name"] = URL
            approval_data[org] = orgdict

        # Need to integrate recognition from FCI
        i+=1
    idog_out = pd.DataFrame.from_dict(breed_summary, orient='index',
                                      columns=["Breed code", "Breed code source",
                                               "synonyms"])
    print(idog_out)