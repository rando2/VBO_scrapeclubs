import requests
import os
from bs4 import BeautifulSoup
import pandas as pd
import spacy
from scrapeFunctions import parse_FCI_breed

def retrieve_html(URL):
    """Pulls HTML from IDog and identify the block containing breed info based on
    div tag (ad hoc)
    Input: string
    Returns: string"""
    # To do: streamline this function across whole project
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    return soup

def get_rec_breeds(breedgroupInfo):
    groups = list()
    for litag in breedgroupInfo.find_all('li'):
        linkInfo = litag.find(href=True)
        groupName = litag.find("span").text
        run_command = "python  FCI_breedgroups.py '{0}' '{1}'".format(linkInfo['href'],
                                                                      groupName.split()[0])
        print(run_command)
        #os.system(run_command)
        groups.append(groupName.split()[0])
    return groups

if __name__ == '__main__':
    url = "https://www.fci.be/en/Nomenclature/"
    pageContent = retrieve_html(url)

    # Find provisional breeds
    provDF = dict()
    provBreeds = pageContent.find("div", {"class": "races"})
    for tdtag in provBreeds.find_all('td', {"class": "race"}):
        link = tdtag.find(href=True)
        dogInfo = parse_FCI_breed(link)

        provDogPage = retrieve_html(dogInfo["url"])
        country = provDogPage.find("span", {"id": "ContentPlaceHolder1_PaysOrigineLabel"}).text
        group = provDogPage.find('a', {"id": "ContentPlaceHolder1_GroupeHyperLink"}).text
        group = group.split("-")[1].strip()
        provDF[dogInfo["breed"].title()] = [country.title(), "",
                                            dogInfo["number"], dogInfo["synonyms"],
                                            dogInfo["url"], group.split()[0], "Provisional"]

    df = pd.DataFrame.from_dict(provDF, orient='index',
                                columns=["Country of Origin", "Variety",
                                         "FCI Number", "Synonyms",
                                         "Source of Recognition Status",
                                         "Breed Group (FCI)",
                                         "FCI Recognition Status"])

    df.to_csv("rawdata/FCI_data.tsv", sep='\t', index_label="Breed")
    print("Wrote TSV for FCI provisionally recognized breeds")

    # First, identify URL and pull data by breed group for recognized dogs
    breedgroupInfo = pageContent.find("ul", {"class": "grouplist"})
    groups = get_rec_breeds(breedgroupInfo)

# combine all tsvs and add "definitive" vs

