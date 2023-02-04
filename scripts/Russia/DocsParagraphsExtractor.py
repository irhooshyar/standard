from pathlib import Path
from abdal import config
from scripts.Russia import Preprocessing
from en_doc.models import Document,DocumentParagraphs

def arabic_preprocessing(text):
    arabic_char = {"آ": "ا", "أ": "ا", "إ": "ا", "ي": "ی", "ة": "ه", "ۀ": "ه", "ك": "ک", "َ": "", "ُ": "", "ِ": "",
                   "": ""}
    for key, value in arabic_char.items():
        text = text.replace(key, value)

    return text


def apply(folder_name, Country):
    dataPath = str(Path(config.DATA_PATH, folder_name))
    resultPath = str(Path(config.RESULT_PATH, folder_name))

    files_text = Preprocessing.readFiles(dataPath, preprocess=False)

    for key, value in files_text.items():
        paragraphs = value.split("\n")
        paragraphs = delete_empty_line(paragraphs)

        document = Document.objects.get(name=key, country_id=Country)
        for i in range(paragraphs.__len__()):
            paragraph = arabic_preprocessing(paragraphs[i])
            DocumentParagraphs.objects.create(document_id=document, text=paragraph, number=i)

def delete_empty_line(line_list:list):
    result_line = []
    for line in line_list:
        if len(line.strip()) > 0:
            result_line.append(line.strip().replace("\t", " ").replace("  ", " "))
    return result_line
