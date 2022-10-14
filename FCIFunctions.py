import re

def parse_FCI_names(link):
    # The names are structured as DOGNAME (##) (ALT NAME)
    name_info = link.text
    dog_info = [i.strip() for i in re.findall(r'[^\(\)]*', name_info) if re.match(r'\S+', i) is not None]
    if len(dog_info) == 2:
        dog_info.append("")
    dog_info.append("https://www.fci.be" + link["href"])
    return dog_info

def parse_rec_breed(link):
    # The names are structured as DOGNAME (##) (ALT NAME)
    # There can be extraneous parentheses in the names, so split based on the ID #
    id_match = re.search(r'\([0-9]+\)', link.text)
    bounds = id_match.span()
    breed = link.text[:bounds[0]].strip()
    try:
        alt_name = link.text[bounds[1]:].strip()[1:-1]
    except AttributeError:
        alt_name = ""
    print(breed, id_match.group()[1:-1], alt_name.title(), "https://www.fci.be" + link["href"])
    return {"breed": breed,
            "number": id_match.group()[1:-1],
            "synonyms": alt_name.title(),
            "url": "https://www.fci.be" + link["href"]}

