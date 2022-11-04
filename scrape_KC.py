from scrapeFunctions import retrieve_html
import pandas as pd


def clean_name(breedName):
    if "(" not in breedName:
        return breedName, ""
    else:
        name, variety = breedName.split(" (")
        variety = variety.replace(")", "")
        if variety.lower() == "imp":
            variety = ""
        return name, variety


breedTable = pd.DataFrame(columns=["Breed", "Variety", "Breed Group (KC)",
                                   "Import Status (KC)", "Source (KC)"])

pageContent = retrieve_html("https://www.thekennelclub.org.uk/search/breeds-a-to-z/")
breedInfo = pageContent.find_all("div", {"class": "u-card-grid u-card-grid--columns-3"})
for initalGroup in breedInfo:
    for breedData in initalGroup.find_all("div", {"class": "m-breed-card m-breed-card--padded"}):
        a = breedData.find('a')
        if a is not None:
            url = "https://www.thekennelclub.org.uk" + a['href']
        else:
            url = ""

        breedGroup = breedData.find("div", {"class": "m-breed-card__category"}).text
        title = breedData.find("strong", {"class": "m-breed-card__title"}).text
        is_imported = bool()
        if "imp" in title.lower():
            is_imported = True
            title = title.replace(" (Imp)", "")
        else:
            is_imported = False
        breedName, variety = clean_name(title)

        breedTable.loc[len(breedTable.index)] = [breedName, variety, breedGroup, is_imported,
                                                 url]

breedTable.to_csv("rawdata/KC.tsv",
                  sep='\t',
                  index=False)
print("Wrote TSV for KC")
