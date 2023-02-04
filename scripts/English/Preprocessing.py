import os
from pathlib import Path
import docx2txt
import glob
from hazm import *
from abdal import config
from abdal.settings import LOCAL_SETTING
import threading
import math
import PyPDF2 

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
            text = open(file, encoding="utf8").read()
            # Arabic char convert
            text = arabicCharConvert(text)
            if preprocess:
                text = Preprocessing(text, **preprocessArg)
        else:
            text = ""
        file = str(os.path.basename(file)).split(".")[0]
        result_text[file] = text

    return result_text

def readFiles_parallel(path, readContent=True, preprocess=True, preprocessArg={}):

    numbers_of_thread = LOCAL_SETTING['NUMBER_OF_THREAD']
    result_list = [None] * numbers_of_thread

    def splitArray(arr, n):
        return_li = []

        step = math.ceil(arr.__len__() / n)
        for i in range(n):
            start_idx = i * step
            end_idx = min(start_idx + step, arr.__len__())
            return_li.append(arr[start_idx:end_idx])

        return return_li

    def body(files, thread_number):
        result_text = {}
        for file in files:
            if readContent:
                # read
                if file[-3:] == 'txt':
                    text = open(file, encoding="utf-8-sig").read()
                else:
                    text = docx2txt.process(file)

                # Arabic char convert
                text = arabicCharConvert(text)
                if preprocess:
                    text = Preprocessing(text, **preprocessArg)
            else:
                text = ""
            file = str(os.path.basename(file)).split(".")[0]
            result_text[file] = text

    #     return
        result_list[thread_number] = result_text

    def parallel_run(func, li, arg=()):
        thread_obj = []
        thread_number = 0
        for S in li:
            thread = threading.Thread(target=func,
                                      args=(S, thread_number)+arg)
            thread_obj.append(thread)
            thread_number += 1
            thread.start()

        for thread in thread_obj:
            thread.join()

    all_files = (glob.glob(path + "//*.docx") + glob.glob(path + "//*.txt"))
    all_files = splitArray(all_files, numbers_of_thread)
    parallel_run(body, all_files)

    # join res
    result = {}
    for r in result_list:
        result = {**result, **r}

    return result

def readFile(filePath, preprocess=True, preprocessArg={}):
    if str(filePath).split(".")[-1] == "docx":
        text = docx2txt.process(filePath)
        # Arabic char convert
        text = arabicCharConvert(text)
        if preprocess:
            text = Preprocessing(text, **preprocessArg)
    else:
        text = open(filePath,encoding="utf8").read()
        # Arabic char convert
        text = arabicCharConvert(text)
        if preprocess:
            text = Preprocessing(text, **preprocessArg)

    return text


def pdf2txt(dataPath,file_old,format):
    address = dataPath + "/" + file_old + format
    new_address = dataPath + "/" + file_old + '.txt'
    text = ""   
    pdfFileObj = open(address, 'rb') 
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj) 
        
    for i in range(pdfReader.numPages): 
        pageObj = pdfReader.getPage(i) 
        text += pageObj.extractText()
    # new_text = ""
    # for word in text.split():
    #     new_text += word[::-1]+" "
    pdfFileObj.close() 
    os.remove(address) 
    new_file = open(new_address, 'w', encoding="utf8")
    new_file.write(text)
    print(text)

    return


def convert_all_pdfs_to_txt(folder_name):
    dataPath = str(Path(config.DATA_PATH, folder_name))
    all_files = glob.glob(dataPath + "/*.pdf")
    for file in all_files:
        file_name = str(os.path.basename(file))
        format = "." + str(os.path.basename(file)).split(".")[-1]
        file_old = str(os.path.basename(file))[:-len(format)]
        pdf2txt(dataPath,file_old,format)
        
        
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

    name = name.lower()

    return name

def otherLangCharConvert(text):
    arabic_char_dict = { 'ü':'u', 'é':'e' , 'â':'a', 'á':'a', "ó":'o', 'ộ':'o', 'ô':'o', 'ö':'o', 'ŷ':'y', 'ù':'u',
                         'í':'i', 'è':'e', 'ê':'e', 'ģ':'g', 'ò':'o'}
    for key, value in arabic_char_dict.items():
        text = text.replace(key, value)
    return text


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
        # normalizer = Normalizer()
        # text = normalizer.normalize(text)
        text = text.lower()

    text = otherLangCharConvert(text)
    # Cleaning
    if removeSpecialChar:
        ignoreList = ["!", "@", "$", "%", "^", "&", "*", "(", ")", "_",":","+", "-", "/", "*", "'", "،", "؛", ",", "\ufeff", ""
                    "{", "}", "[", "]", "«", "»", "<", ">", ".", "?", "؟", "\n", "\t", '"', '۱', '۲', '۳', '۴', '۵',
                      '۶', '۷', '۸', '۹', '۰', "٫"]
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
