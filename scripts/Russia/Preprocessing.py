import os
from pathlib import Path
import docx2txt
import glob
from hazm import *
from abdal import config


def readFiles(path, readContent=True, preprocess=True, preprocessArg={}):
    all_files = glob.glob(path + "//*.docx")
    result_text = {}
    for file in all_files:
        if readContent:
            text = docx2txt.process(file)
            # Arabic char convert
            text = arabicCharConvert(text)
            if preprocess:
                text = Preprocessing(text, **preprocessArg)
        else:
            text = ""
        file = str(os.path.basename(file)).split(".")[0]
        result_text[file] = text

    all_files = glob.glob(path + "//*.txt")
    for file in all_files:
        if readContent:
           
            text = open(file, encoding="utf16").read()
            # Arabic char convert
            text = arabicCharConvert(text)
            if preprocess:
                text = Preprocessing(text, **preprocessArg)
        else:
            text = ""
        file = str(os.path.basename(file)).split(".")[0]
        result_text[file] = text

    return result_text


def readFile(filePath, preprocess=True, preprocessArg={}):
    if str(filePath).split(".")[-1] == "docx":
        text = docx2txt.process(filePath)
        # Arabic char convert
        text = arabicCharConvert(text)
        if preprocess:
            text = Preprocessing(text, **preprocessArg)
    else:
        # windows-1251/KOI8-R
        text = open(filePath,encoding="utf16").read()
        # Arabic char convert
        text = arabicCharConvert(text)
        if preprocess:
            text = Preprocessing(text, **preprocessArg)

    return text


def renameFilesToStandard(folder_name):
    try:
        dataPath = str(Path(config.DATA_PATH, folder_name))
        all_files = glob.glob(dataPath + "/*.docx")
        for file in all_files:
            format = "." + str(os.path.basename(file)).split(".")[-1]
            file_old = str(os.path.basename(file))[:-len(format)]
            file_new = standardFileName(file_old)
            if file_old != file_new:
                os.rename(Path(dataPath, file_old + format), Path(dataPath, file_new + format))

        all_files = glob.glob(dataPath + "/*.txt")
        for file in all_files:
            try:
                format = "." + str(os.path.basename(file)).split(".")[-1]
                file_old = str(os.path.basename(file))[:-len(format)]
                file_new = standardFileName(file_old)
                if file_old != file_new:
                    os.rename(Path(dataPath, file_old + format), Path(dataPath, file_new + format))
            except Exception as e:
                print(file+"\t"+str(e)+"\n")

    except Exception as e:
        print(e)



def getStemDict(path, stem=False, remove_sw=False):
    all_files = readFiles(path, preprocessArg={"stem": stem, "removeSW": remove_sw})
    stem_dict = {}
    for file in all_files:
        text = all_files[file]
        for word in text:
            word_s = stemming(word)
            stem_dict[word] = word_s
    return stem_dict


def standardFileName(name):
    name = name.replace(".", "")
    name = englishCharConvert(name)
    name = name.strip()

    while "  " in name:
        name = name.replace("  "," ")

    return name


def englishCharConvert(text):
    while "\n" in text:
        text = text.replace("\n"," ")

    while "  " in text:
        text = text.replace("  ", " ")

    return text

def arabicCharConvert(text):
    arabic_char_dict = {"ك": "ک", "آ": "ا", "أ": "ا", "إ": "ا", "ي": "ی", "ة": "ه", "ۀ": "ه", "  ":" ", "\n\n":"\n", "\n ":"\n" , }
    for key, value in arabic_char_dict.items():
        text = text.replace(key, value)

    return text


stemmer = Stemmer()


def stemming(word):
    word_s = stemmer.stem(word)
    return word_s


def Preprocessing(text, tokenize=True, stem=True, removeSW=True, normalize=True, removeSpecialChar=True):
    # Normalization
    if normalize:
        normalizer = Normalizer()
        text = normalizer.normalize(text)

    # Cleaning
    if removeSpecialChar:
        ignoreList = ["!", "@", "$", "%", "^", "&", "*", "(", ")", "_",":","+", "-", "/", "*", "'", "،", "؛", ",", ""
                    "{", "}", "[", "]", "«", "»", "<", ">", ".", "?", "؟", "\n", "\t", '"', '۱', '۲', '۳', '۴', '۵',
                      '۶', '۷', '۸', '۹', '۰', "٫", '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        for item in ignoreList:
            text = text.replace(item, " ")

    # Tokenization
    if tokenize:
        text = [word for word in text.split(" ") if word != ""]

        # stopwords
        if removeSW:
            stopwords_list = open(Path(config.BASE_PATH, "text_files/englishStopWord.txt"), encoding="utf8").read().split(
                "\n")
            text = [word for word in text if word not in stopwords_list]

            # filtering
            text = [word for word in text if len(word) >= 2]

        # stemming
        if stem:
            text = [stemming(word) for word in text]

    return text
