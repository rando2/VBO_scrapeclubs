import requests
from bs4 import BeautifulSoup
import pandas as pd

def retrieve_html(URL):
    # Pulls HTML from specified source and parses with bs4
    page = requests.get(URL)
    return BeautifulSoup(page.content, "html.parser")

def get_AKC(iso="USA", org="AKC"):
    # Retrieve AKC data and parse based on structure
    # Transboundary name is set equal to breed name (for now)
    # Updated Sept 15 2022
    breeds = dict()
    soup = retrieve_html("https://www.akc.org/public-education/resources/general-tips-information/dog-breeds-sorted-groups/")
    breednameDiv = soup.find("div", {"class": "custom-select"})
    for option in breednameDiv.find_all('option'):
        if option['value'] != "":
            breeds[option.text] = option['value']
    breedData = pd.DataFrame.from_dict(breeds, orient='index', columns=["Source"])
    breedData['Organization'] = [org] * len(breedData)
    breedData['Country'] = [iso] * len(breedData)
    breedData['TransboundaryName'] = breedData.index
    return breedData

def get_UKC(iso="USA", org="UKC"):
    # Retrieve UKC data and parse based on structure
    # Transboundary name is set equal to breed name (for now)
    # Updated Sept 15 2022
    breeds = dict()
    soup = retrieve_html("https://www.ukcdogs.com/breed-standards")
    breednameDiv = soup.find("div", {"class": "dog_breeds"})
    for ultag in breednameDiv.find_all('ul'):
        for litag in ultag.find_all('li'):
            link = litag.find(href=True)
            breeds[link.text] = "https://www.ukcdogs.com/" + link['href']
    breedData = pd.DataFrame.from_dict(breeds, orient='index', columns=["Source"])
    breedData['Organization'] = [org] * len(breedData)
    breedData['Country'] = [iso] * len(breedData)
    breedData['TransboundaryName'] = breedData.index
    return breedData

def get_SKK(iso="SWE", org="SKK"):
    # Retrieve SKK data and parse based on structure
    # Transboundary name is blank, needs filling in through translation
    # Updated Sept 15 2022
    breeds = dict()
    soup = retrieve_html("https://hundar.skk.se/hunddata/Hund_sok.aspx#")
    breednameDiv = soup.find_all("div", {"class": "col-sm-3"})
    for htmlblock in breednameDiv:
        try:
            for option in htmlblock.find_all('option'):
                if option['value'] != "":
                    breed = option.text.replace('"', "")
                    urlBreed = breed.replace(" ", "-")
                    breeds[breed] = "https://www.skk.se/sv/hundraser/" + urlBreed
            if len(breeds) > 0:
                #breedData = pd.DataFrame.from_dict(breeds, orient='index', columns=["Source"])
                return pd.DataFrame(list(zip(breeds.values(), [org] * len(breeds),
                                         [iso] * len(breeds), [""] * len(breeds))),
                                         index=breeds.keys(), columns=["Source", "Organization", "Country",
                                                                "TransboundaryName"])

        except AttributeError:
            continue

def get_IDog():
    # Automate retrieval of number of entries
    url = "https://ngdc.cncb.ac.cn/idog/breed/getAllBreed.action?totalCount=481&pageNo=1&rowCount=481&isFirstSearchFlag=0&pageSize="
    soup = retrieve_html(url)
    breednameDiv = soup.find_all("div", {"class": "media-body"})
    print(len(breednameDiv))
    for breed in breednameDiv:
        print(breed)
        exit(0)
    #for litag in ultag.find_all('li'):
    #link = litag.find(href=True)


if __name__ == '__main__':
    #breeds = pd.concat([get_AKC(), get_UKC(), get_SKK()])
    #breeds.to_csv("scraped_breed_data.csv")
    get_IDog()