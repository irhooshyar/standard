from abdal import config
from pathlib import Path
from scripts.Russia import Preprocessing
from en_doc.models import Document

def apply(folder_name, Country):
    dataPath = str(Path(config.DATA_PATH, folder_name))
    resultPath = str(Path(config.RESULT_PATH, folder_name))

    all_files = Preprocessing.readFiles(dataPath, readContent=False)
    all_files = sorted(all_files.keys())
    resultFile = open(Path(resultPath, "Documents.txt"), "w", encoding="utf8")

    for file in all_files:
        resultFile.write(file + "\n")
        Document.objects.create(name=file, country_id=Country)

    resultFile.close()
