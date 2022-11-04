from scrapeFunctions import retrieve_html
import csv


pageContent = retrieve_html("https://www.ckc.ca/en/Choosing-a-Dog/Choosing-a-Breed/All-Dogs")
breeds = list()
breedgroupInfo = pageContent.find_all("div", {"class": "post clearfix breedPost"})
for breedgroup in breedgroupInfo:
    #print(breedgroup)
    linkInfo = breedgroup.find(href=True)['href']
    url = "https://www.ckc.ca" + linkInfo
    group = linkInfo.split("/")[-2].replace("-", " ")
    breedName = breedgroup.find("h3", {"class": "breedListing"}).text
    breeds.append([breedName, group, url])

with open("rawdata/ckc.csv", "w",  newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Breed", "Group", "URL"])
    writer.writerows(breeds)

