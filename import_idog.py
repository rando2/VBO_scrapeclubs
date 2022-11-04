import json
import pandas as pd

def import_json(f):
    with open(f) as json_file:
        return json.load(json_file)

breeds = pd.DataFrame.from_dict(import_json("tmp/idog_processing_breed.json"), orient='index')
breeds.rename(columns={0: "iDog_ID", 1: "iDog_Ref", 2: "Alt_Names", 3: "Country_of_Origin"}, inplace=True)
approval_stats = pd.DataFrame.from_dict(import_json('tmp/idog_processing_approval.json'))

breed_info = breeds.merge(approval_stats, left_index=True, right_index=True)
breed_info.to_csv("rawdata/idog.tsv", index_label="Breed",
                  sep='\t')