from pathlib import Path
from abdal import config
from scripts.Russia import Preprocessing
from en_doc.models import Document

def apply(folder_name, Country):
    dataPath = str(Path(config.DATA_PATH, folder_name))
    resultPath = str(Path(config.RESULT_PATH, folder_name))

    input_data = Preprocessing.readFiles(dataPath, preprocess=False)
    doc_features = ["TotalWords\tDinstinctWords\tStopwords\tMainWords\tFileName\n"]
    for file in input_data:
        st = ""
        text = input_data[file]
        text1 = Preprocessing.Preprocessing(text, removeSW=False, stem=False)
        total = len(text1)
        distinct = len(list(set(text1)))
        st += str(total) + "\t" + str(distinct)
        text2 = Preprocessing.Preprocessing(text, stem=False)
        stopWords = total - len(text2)
        st += "\t" + str(stopWords) + "\t" + str(len(text2))
        doc_features.append(st + "\t" + file + "\n")

        Document.objects.filter(name=file, country_id=Country).update(word_count= total, distinct_word_count=distinct,stopword_count = stopWords)

    file = open(Path(resultPath, "Features.txt"), "w", encoding="utf8")
    for i in doc_features:
        file.write(i)
    file.close()
