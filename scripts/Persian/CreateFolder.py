import os
from pathlib import Path

from abdal import config


def CreateBase():
    os.mkdir(config.RESULT_PATH)
    os.mkdir(config.DATA_PATH)
    os.mkdir(config.ZIPS_PATH)

def apply(folder_name):
    if not os.path.isdir(config.RESULT_PATH):
        CreateBase()

    resultPath = str(Path(config.RESULT_PATH, folder_name))
    os.mkdir(resultPath)

    inner_folder = ["Graph", "Ngram", "Ngram/2gram", "Ngram/3gram", "TFIDF", "Paragraphs", "InvertedIndex"]
    for folder in inner_folder:
        path = Path(resultPath, folder)
        os.mkdir(path)
