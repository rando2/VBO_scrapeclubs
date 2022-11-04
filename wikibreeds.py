from scrapeFunctions import retrieve_html
import csv


pageContent = retrieve_html("https://en.wikipedia.org/wiki/List_of_dog_breeds")
breeds = list()
breedgroupInfo = pageContent.find_all("div", {"class": "div-col"})
for metacategory in breedgroupInfo:
    for litag in metacategory.find_all('li'):
        linkInfo = litag.find(href=True)
        breed = linkInfo.text
        url = "https://en.wikipedia.org" + linkInfo['href']
        breeds.append([breed, url])

with open("rawdata/wiki.csv", "w",  newline="") as f:
    writer = csv.writer(f)
    writer.writerows(breeds)

