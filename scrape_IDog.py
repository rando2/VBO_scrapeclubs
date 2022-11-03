import requests
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz
import pandas as pd
import spacy
import json

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
    """Identify items in a list separated by punctuation. iDog seems to use commas UNTIL
    it encounters a name with a comma, and then it switched to semicolons. It also sometimes uses "or" to
    separate different names. I coded these patterns here"""
    if text is None:
        return []

    text = text.replace(" or ", ", ")
    if ';' in text:
        split_semi = text.split(";")
        cleaned_items = list()
        mixed_list = split_semi[0]
        while mixed_list.count(",") > 1:
            new_item = mixed_list.split(",")[0]
            cleaned_items.append(new_item.strip())
            mixed_list = mixed_list.replace(new_item + ",", "")
        cleaned_items.append(mixed_list.strip())
        return cleaned_items + [name.strip() for name in split_semi[1:]]

    else:
        return [name.strip() for name in text.split(',')]


def identifyFields(fieldIDs, text):
    """Extract basic breed information from below photo (ad hoc)
    input:
          dictionary: fields (keys) and exact text demarcating fields (values)
          string: .text of relevant section of html
    returns:
          dictionary: fields (keys of input dictionary) with the values extracted
          Unless page is empty, in which case it returns None
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
    i = 1
    while i != 0: # < is just for testing to keep the dataset small-ish
        url = "https://ngdc.cncb.ac.cn/idog/breed/getBreedDetail.action?breedId=" + str(i)
        breedData = retrieve_html(url)

        # The "find" functions use the html coding I identified just by looking at the page source
        # There are two separate sections demarcated with div
        basicInfoRaw = breedData.find("div", {"class": "col-xs-12 col-sm-4 col-sm-offset-1"}).text
        basicInfo = identifyFields({"breed name": "Web Source Name:",
                                    "breed name source": "from ",
                                    "other name": "Other Name:",
                                    "common name": "Common Name:"}, basicInfoRaw)
        if basicInfo is None:
            i = 0
            continue
        names = parse_list(basicInfo["common name"]) + parse_list(basicInfo["other name"])

        # Now extract iDog info
        detailInfoRaw = breedData.find("div", {"class": "col-xs-12 col-sm-7"}).text
        basicInfo.update(identifyFields({"iDog identifier": "iDog Breed Number: ",
                                         "origin": "Original: "}, detailInfoRaw))
        recognitionInfoRaw = breedData.find("div", {"class": "table-responsive"})

        breed_summary[basicInfo["breed name"]] = [basicInfo['iDog identifier'], url,
                                                  "|".join([n for n in names if len(n) > 0]),
                                                  basicInfo["origin"]]

        for org, URL in parse_recognition(recognitionInfoRaw).items():
            orgdict = approval_data.get(org, dict())
            orgdict[basicInfo["breed name"]] = URL
            approval_data[org] = orgdict

        if i % 10 == 0:
            print(i)
            with open('tmp/idog_processing_breed.json', 'w') as outfile:
                outfile.write(json.dumps(breed_summary))
            with open('tmp/idog_processing_approval.json', 'w') as outfile:
                outfile.write(json.dumps(approval_data))
        i+=1

    idog_out = pd.DataFrame.from_dict(breed_summary,
                                      orient='index',
                                      columns=["Breed code", "Breed code source",
                                               "Synonyms", "Country of Origin"])


    # For each breed organization in the table
    for breed_org, rec_breeds in approval_data.items():
        org_df = pd.DataFrame.from_dict(rec_breeds,
                                        orient='index',
                                        columns=["Source of recognition status"])

        org_data = idog_out.join(org_df, how="right")
        org_data.to_csv("rawdata/" + breed_org + ".tsv", sep='\t', index_label="Breed")