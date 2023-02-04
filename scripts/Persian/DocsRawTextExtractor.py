from pathlib import Path
from abdal import config
from scripts.Persian import Preprocessing
from doc.models import Document,DocumentParagraphs
import math
import threading
from itertools import chain
import time



def apply(folder_name, Country):
    batch_size = 10000

    t = time.time()

    dataPath = str(Path(config.DATA_PATH, folder_name))
    files_text = Preprocessing.read_raw_text(dataPath)


    documents = Document.objects.filter(country_id=Country)


    for doc in documents:
        doc.raw_text = files_text[doc.file_name]

    Document.objects.bulk_update(
        documents,['raw_text'],batch_size)

    print("time ", time.time() - t)


