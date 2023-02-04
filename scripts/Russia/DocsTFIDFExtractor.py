from abdal import config
from scripts.Russia import Preprocessing
import math
import os
from pathlib import Path
from en_doc.models import DocumentTFIDF,Document

# from collections import OrderedDict


def Calculate_Words_Document(data_dict):
    words_document_dict = {}
    for doc, word_list in data_dict.items():
        for word in word_list:
            if word not in words_document_dict:
                words_document_dict[word] = [doc]
            else:
                words_document_dict[word].append(doc)
    return words_document_dict


def Calculate_words_Frequency_inDoc(word_list):
    words_frequency_dict = {}
    for word in word_list:
        if word not in words_frequency_dict:
            words_frequency_dict[word] = 1
        else:
            words_frequency_dict[word] += 1
    return words_frequency_dict


def Calculate_TFIDF(word_frequency_dict, word_document_dict, document_count):
    tfidf_dict = {}

    for word, frequency in word_frequency_dict.items():
        term_frequency_in_document = frequency
        document_frequency = len(set(word_document_dict[word]))
        term_frequency_in_all = len(word_document_dict[word])
        tfidf_value = term_frequency_in_document * math.log((document_count / document_frequency), 10)
        avg_frequency_per_doc = term_frequency_in_all / document_frequency

        tfidf_dict[word] = [term_frequency_in_document,
                            document_frequency,
                            term_frequency_in_all,
                            tfidf_value,
                            avg_frequency_per_doc]

    return tfidf_dict


def write_to_file(doc_name, document_tfidf_sorted_dict, result_path, Country):
    doc_name = str(os.path.basename(doc_name))
    document = Document.objects.get(name=doc_name,country_id=Country)

    file_path = os.path.join(result_path, f'TFIDF/{doc_name}.txt')
    file = open(file_path, "w", encoding="utf8")
    i = 1
    for word, value in document_tfidf_sorted_dict.items():
        term_frequency_in_documnet = str(value[0])
        document_frequency = str(value[1])
        term_frequency_in_all = str(value[2])
        tfidf_value = str(round(value[3], 2))
        avg_frequency_per_doc = str(round(value[4], 2))
        file.write(str(i) + "\t" + word + "\t" +
                   term_frequency_in_documnet + "\t" +
                   document_frequency + "\t" +
                   term_frequency_in_all + "\t" +
                   tfidf_value + "\t" +
                   avg_frequency_per_doc + "\n")

        DocumentTFIDF.objects.create(word=word, count=term_frequency_in_documnet, weight=tfidf_value, document_id=document)

        if i % 20 == 0:
            break
        i += 1

    file.close()


def apply(folder_name, Country):
    dataPath = str(Path(config.DATA_PATH, folder_name))
    resultPath = str(Path(config.RESULT_PATH, folder_name))

    input_data = Preprocessing.readFiles(dataPath, preprocessArg={"stem": False})
    document_count = input_data.__len__()

    words_document_dict = Calculate_Words_Document(input_data)
    # print(input_data.items())
    for doc, wordList in input_data.items():
        words_frequency_dict = Calculate_words_Frequency_inDoc(wordList)
        document_tfidf_dict = Calculate_TFIDF(words_frequency_dict, words_document_dict, document_count)
        document_tfidf_sorted_dict = dict(sorted(document_tfidf_dict.items(), key=lambda x: x[1][3], reverse=True))
        write_to_file(doc, document_tfidf_sorted_dict, resultPath, Country)

