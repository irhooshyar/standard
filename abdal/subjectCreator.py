import config
from pathlib import Path
import json

f_list = ["Fava", "Iran500", "Iran6000_tq82mia"]
result_dict = {}
for folder_name in f_list:
    print(folder_name)
    dataPath = str(Path(config.RESULT_PATH, folder_name)) + '/Subject/'
    jsonFile = open(dataPath + "JaccardSimilarity.json")
    data = json.load(jsonFile)
    all_doc = []
    for key, value in data.items():
        doc = key
        max_val = 0
        max_sub = ""
        for key1, value1 in value.items():
            v = value1["value"]
            if v >= max_val:
                max_val = v
                max_sub = key1

        if max_sub not in result_dict:
            result_dict[max_sub] = [doc]
            all_doc.append(key)
        else:
            result_dict[max_sub].append(doc)
            all_doc.append(key)

    result_dict["همه"] = all_doc

    with open(Path(dataPath, "SubjectsDocList.json"), "w", encoding="utf8") as outfile:
        json.dump(result_dict, outfile, indent=4, ensure_ascii=False)