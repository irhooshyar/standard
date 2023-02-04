from pathlib import Path
from abdal import config
from scripts.Persian import Preprocessing
import re
from hazm import *
from doc.models import DocumentDefinition, ExtractedKeywords, Document
from scripts.parallel import Parallel
import time

normalizer = Normalizer()

# Cleaning
ignoreList = ["!", "@", "$", "%", "^", "&", "*", "(", ")", "_", "+", "-", "/", "*", "'", "،", "؛", ",",
              ""
              "{", "}", "[", "]", "«", "»", "<", ">", ".", "?", "؟", "\n", "\t", '"',
              '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹', '۰', "٫",
              '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '\u200f']

alphabet = ["الف", "ب", "پ", "ت", "ث", "ج", "چ", "ح", "خ", "د", "ذ", "ر", "ز", "ژ", "س", "ش", "ص", "ض",
            "ط", "ظ", "ع", "غ", "ف", "ق", "ک", "گ", "ل", "م", "ن", "و", "ه", "ی", "ا", "آ"]


class DocsDefinitionsExtractor(Parallel):
    result_key = ['Create_List_ExtractedKeywords', 'Create_List_Definitions']

    def clearModel(self, Country):

        DocumentDefinition.objects.filter(document_id__country_id=Country).delete()
        # ExtractedKeywords.objects.filter(country=Country).delete()

    def start(self, folderName, Country, **arg):
        dataPath = str(Path(config.DATA_PATH, folderName))
        input_data = Preprocessing.readFiles_parallel(dataPath, preprocess=False)
        document_list = Document.objects.filter(country_id=Country)
        for doc in document_list:
            input_data[doc.id] = input_data.pop(doc.file_name)
        return input_data

    def parallelPhase(self, li, threadNumber):
        for doc_id in li:
            self.statusProgress.progress()
            if type(doc_id) == str:
                print(f'Error in DocsDefinitionsExtractor: not found document id for name: {doc_id}')
                continue
            dic = {}
            max_len_for_search_definition_part = 125000
            text = li[doc_id][:max_len_for_search_definition_part]

            startIndex = -1
            endIndex = -1

            list_keyword_definition = ["تعاریف", "اصطلاحات", "تعاريف"]
            # find minimum index
            for definition_word in list_keyword_definition:
                index = text.find(definition_word)
                if -1 < index:
                    if startIndex == -1:
                        startIndex = index
                    elif index < startIndex:
                        startIndex = index

            if startIndex > -1:

                preText = text[startIndex - 20:startIndex]
                list_keyword_partition = ["فصل", "ماده", "گفتار", "بخش"]
                keyword_partition = None

                for partition_word in list_keyword_partition:
                    index = preText.find(partition_word)
                    if index > -1:
                        keyword_partition = partition_word
                        offset = text[startIndex:].find(keyword_partition + " ")
                        endIndex = -1 if offset == -1 else startIndex + offset
                        break

                if keyword_partition is None:
                    postText = text[startIndex:startIndex + 40]
                    for partition_word in list_keyword_partition:
                        index = postText.find(partition_word)
                        if index > -1:
                            keyword_partition = partition_word
                            offset = text[startIndex:].find(keyword_partition + " ")
                            endIndex = -1 if offset == -1 else startIndex + 40 + offset
                            break

            keyword_list_filterd = []

            if endIndex > -1:
                text = text[startIndex:endIndex]

                dic["definition part"] = text

                list_sent = text.split("\n")
                keyList = [re.sub(r'\t', '', i[:i.find(":")]) for i in list_sent if i.find(":") > -1]

                keyList2 = []
                for kw in keyList:
                    main_kw = kw
                    kw = normalizer.normalize(kw)

                    for item in ignoreList:
                        kw = kw.replace(item, " ")

                    kw = [word for word in kw.split(" ") if word != ""]

                    if len(kw) > 0:
                        if kw[0] in alphabet:
                            keyList2.append(" ".join(kw[1:]))

                        if len(kw) < 6:
                            keyword_list_filterd.append(main_kw)

                if len(keyList2) > 0:
                    dic["final keyword set"] = keyList2


            # document = Document.objects.get(file_name=doc_name, country_id=Country)
            definition_part = "definition part"
            final_keyword_set = "final keyword set"
            text = dic[definition_part] if definition_part in dic else None

            if final_keyword_set in dic:
                obj_def = DocumentDefinition.objects.create(text=text, document_id_id=doc_id)
                keywords = dic[final_keyword_set]
                for key in keywords:
                    obj_keyword = ExtractedKeywords(word=key, definition_id=obj_def)
                    self.addResult('Create_List_ExtractedKeywords', obj_keyword, threadNumber)
            else:
                obj_def = DocumentDefinition(text=text, document_id_id=doc_id)
                self.addResult('Create_List_Definitions', obj_def, threadNumber)

    def end(self, res, **arg):
        self.bulk_create_array(ExtractedKeywords, res['Create_List_ExtractedKeywords'])
        self.bulk_create_array(DocumentDefinition, res['Create_List_Definitions'])
