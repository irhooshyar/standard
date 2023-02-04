import re
from scripts.Persian import Preprocessing
from doc.models import Document, DocumentParagraphs, ReferencesParagraphs, Graph, Measure, Slogan, SloganAnalysis, CUBE_SloganAnalysis_ChartData, CUBE_SloganAnalysis_FullData, SloganAnalysisUsingSynonymousWords, SloganSynonymousWords


def LocalPreprocessing(text):
    # Cleaning
    ignoreList = ["!", "@", "$", "%", "^", "&", "*", "_", "+", "*", "'",
                  "{", "}", "[", "]", "<", ">", ".", '"', "\t"]
    for item in ignoreList:
        text = text.replace(item, " ")

    # Delete non-ACII char
    for ch in text:
        if ch != "/" and ord(ch) <= 255 or (ord(ch) > 2000):
            text = text.replace(ch, " ")

    return text

def GetDocumentById_Local(id):
    document = Document.objects.get(id=id)
    document_actors = {}


    approval_ref = "نامشخص"
    if document.approval_reference_id != None:
        approval_ref = document.approval_reference_name

    approval_date = "نامشخص"
    approval_year = "نامشخص"
    if document.approval_date != None:
        approval_date = document.approval_date
        approval_year = approval_date[0:4]

    level_name = "نامشخص"
    if document.level_id != None:
        level_name = document.level_name

    subject_name = "نامشخص"
    if document.subject_id != None:
        subject_name = document.subject_name

    result = {"id": document,
              "name": document.name,
              "country_id": document.country_id_id,
              "country": document.country_id.name,
              "level_id": document.level_id_id,
              "level": level_name,
              "subject_id": document.subject_id_id,
              "subject": subject_name,
              "approval_reference_id": document.approval_reference_id_id,
              "approval_reference": approval_ref,
              "approval_date": approval_date,
              "approval_year": approval_year,
              }
    return result

def apply(folder_name, Country):

    SloganAnalysis.objects.filter(country_id=Country).delete()
    # Graph.objects.filter(src_document_id__country_id=Country).delete()
    slogan_list = Slogan.objects.all()
    create_list =[]
    document_slogan_id_dict = {}
    s_year_doc_year_ids = {}
    for year in range(1375, 1401, 1):
        document_list = Document.objects.filter(country_id=Country, approval_date__icontains=str(year))
        paragraph_list = DocumentParagraphs.objects.filter(document_id__in=document_list)
        print("-------d-------", document_list.__len__())
        print("-------p-------", paragraph_list.__len__())
        slogan_list_keywords = {}
        number_keyword = {}
        text_len_for_year = 0
        for slogan in slogan_list:
            number_keyword[slogan.year] = 0
            slogan_list_keywords[slogan.year] = slogan.keywords.split("-")
        for paragraph in paragraph_list:
            # if
            # document_slogan_id = paragraph.document_id.id
            # print(document_slogan_id)
            text_len_for_year += len(paragraph.text.split(" "))
            for year_s in slogan_list_keywords:
                num = 0

                for word in slogan_list_keywords[year_s]:
                    isin = paragraph.text.find(word)
                    if isin>0:
                        num += isin

                        doc_id = paragraph.document_id.id
                        if year_s not in s_year_doc_year_ids:
                            s_year_doc_year_ids[year_s] = {
                                year : [doc_id]
                            }
                        else:
                            if year not in s_year_doc_year_ids[year_s]:
                                s_year_doc_year_ids[year_s] = {
                                    year: [doc_id]
                                }
                            else:
                                if doc_id not in s_year_doc_year_ids[year_s][year]:
                                    s_year_doc_year_ids[year_s][year].append(doc_id)

                        #new update
                        if year_s not in document_slogan_id_dict:
                            document_slogan_id_dict[year_s] = [paragraph.document_id.id]
                        else:
                            if paragraph.document_id.id not in document_slogan_id_dict[year_s]:
                                document_slogan_id_dict[year_s].append(paragraph.document_id.id)

                number_keyword[year_s] += num


        for i in number_keyword:
            if len(document_list) != 0: # document_list:docs in a year , text_len_for_year : num od words in docs in a year
                number_per_doc= round(number_keyword[i]/len(document_list),2)
                number_per_len= round((number_keyword[i]/text_len_for_year)*100,2)
            else:
                number_per_doc=0
                number_per_len=0

            if i in s_year_doc_year_ids and year in s_year_doc_year_ids[i]:
                doc_id_list = str(s_year_doc_year_ids[i][year])
            else:
                doc_id_list = ""
            slogan_obj = SloganAnalysis(docYear=year, sloganYear=i, number_per_doc=number_per_doc,number_per_len=number_per_len, country_id=Country, doc_ids=doc_id_list)
            create_list.append(slogan_obj)
            # print(f'ASNAD:{year}: slogan:{i} => {meanOfRepeat}')



    # print(document_slogan_id_dict)

    SloganAnalysis.objects.bulk_create(create_list)
    create_ChartData_CUBE(Country, document_slogan_id_dict)
    create_FullData_CUBE(Country, document_slogan_id_dict)
    create_SloganAnalysis_UsingSynonymousWords(Country) # document_slogan_id_dict is different from the one above

def create_ChartData_CUBE(Country, document_slogan_id_dict):
    batch_size = 10000
    Create_List = []

    CUBE_SloganAnalysis_ChartData.objects.filter(country_id=Country).delete()

    for year, document_slogan_id_list in document_slogan_id_dict.items():
        subject_data = {}
        approval_references_data = {}
        level_data = {}
        for document_slogan_id in document_slogan_id_list:
            document_details = GetDocumentById_Local(document_slogan_id)

            subject_name = document_details["subject"]
            approval_reference_name = document_details["approval_reference"]
            level_name = document_details['level']


            if subject_name not in subject_data:
                subject_data[subject_name] = 1
            else:
                subject_data[subject_name] += 1

            if approval_reference_name not in approval_references_data:
                approval_references_data[approval_reference_name] = 1
            else:
                approval_references_data[approval_reference_name] += 1

            if level_name not in level_data:
                level_data[level_name] = 1
            else:
                level_data[level_name] += 1

        # ---------------------------------------------------
        subject_chart_data = []
        approval_reference_chart_data = []
        level_chart_data = []

        for key, value in subject_data.items():
            subject_chart_data.append([key, value])

        for key, value in approval_references_data.items():
            approval_reference_chart_data.append([key, value])

        for key, value in level_data.items():
            level_chart_data.append([key, value])


        subject_chart_data_json = {"data": subject_chart_data}
        level_chart_data_json = {"data": level_chart_data}
        approval_reference_chart_data_json = {"data": approval_reference_chart_data}

        cube_obj = CUBE_SloganAnalysis_ChartData(
            country_id=Country,
            sloganYear=year,
            subject_chart_data=subject_chart_data_json,
            level_chart_data=level_chart_data_json,
            approval_reference_chart_data=approval_reference_chart_data_json,
        )

        Create_List.append(cube_obj)

        if Create_List.__len__() > batch_size:
            CUBE_SloganAnalysis_ChartData.objects.bulk_create(Create_List)
            Create_List = []

    CUBE_SloganAnalysis_ChartData.objects.bulk_create(Create_List)

def create_FullData_CUBE(Country, document_slogan_id_dict):
    batch_size = 10000
    Create_List = []

    CUBE_SloganAnalysis_FullData.objects.filter(country_id=Country).delete()

    for year, document_slogan_id_list in document_slogan_id_dict.items():
        for document_slogan_id in document_slogan_id_list:
            document_details = GetDocumentById_Local(document_slogan_id)

            cube_obj = CUBE_SloganAnalysis_FullData(
                country_id=Country,
                sloganYear = year,
                document_id = document_details["id"],
                document_name = document_details["name"],
                subject_name = document_details["subject"],
                level_name =document_details['level'],
                approval_reference_name = document_details["approval_reference"],
                approval_date = document_details["approval_date"],
            )

            Create_List.append(cube_obj)

            if Create_List.__len__() > batch_size:
                CUBE_SloganAnalysis_FullData.objects.bulk_create(Create_List)
                Create_List = []

    CUBE_SloganAnalysis_FullData.objects.bulk_create(Create_List)

def create_SloganAnalysis_UsingSynonymousWords(Country):
    SloganAnalysisUsingSynonymousWords.objects.filter(country_id=Country).delete()
    # Graph.objects.filter(src_document_id__country_id=Country).delete()
    slogan_list = Slogan.objects.all()
    create_list =[]
    document_slogan_id_dict = {}
    s_year_doc_year_ids = {}
    for year in range(1375, 1401, 1):
        document_list = Document.objects.filter(country_id=Country, approval_date__icontains=str(year))
        paragraph_list = DocumentParagraphs.objects.filter(document_id__in=document_list)
        # print("-------d-------", document_list.__len__())
        # print("-------p-------", paragraph_list.__len__())
        slogan_list_synonyms = {} #### synonyms
        number_synonym = {}
        text_len_for_year = 0
        for slogan in slogan_list:
            sloganYear = slogan.year
            number_synonym[sloganYear] = 0
            # print(sloganYear)
            if(SloganSynonymousWords.objects.filter(year = sloganYear).count() > 0):
                slogan_list_synonyms[sloganYear] = SloganSynonymousWords.objects.filter(year = sloganYear).first().words.split("-")
        for paragraph in paragraph_list:
            # if
            # document_slogan_id = paragraph.document_id.id
            # print(document_slogan_id)
            text_len_for_year += len(paragraph.text.split(" "))
            for year_s in slogan_list_synonyms:
                num = 0

                for word in slogan_list_synonyms[year_s]:
                    isin = paragraph.text.find(word)
                    if isin>0:
                        num += isin

                        doc_id = paragraph.document_id.id
                        if year_s not in s_year_doc_year_ids:
                            s_year_doc_year_ids[year_s] = {
                                year : [doc_id]
                            }
                        else:
                            if year not in s_year_doc_year_ids[year_s]:
                                s_year_doc_year_ids[year_s] = {
                                    year: [doc_id]
                                }
                            else:
                                if doc_id not in s_year_doc_year_ids[year_s][year]:
                                    s_year_doc_year_ids[year_s][year].append(doc_id)

                        #new update
                        if year_s not in document_slogan_id_dict:
                            document_slogan_id_dict[year_s] = [paragraph.document_id.id]
                        else:
                            if paragraph.document_id.id not in document_slogan_id_dict[year_s]:
                                document_slogan_id_dict[year_s].append(paragraph.document_id.id)

                number_synonym[year_s] += num


        for i in number_synonym:
            if len(document_list) != 0: # document_list:docs in a year , text_len_for_year : num od words in docs in a year
                number_per_doc= round(number_synonym[i]/len(document_list),2)
                # number_per_doc= round(number_synonym[i],2)
                number_per_len= round((number_synonym[i]/text_len_for_year)*100,2)
            else:
                number_per_doc=0
                number_per_len=0

            if i in s_year_doc_year_ids and year in s_year_doc_year_ids[i]:
                doc_id_list = str(s_year_doc_year_ids[i][year])
            else:
                doc_id_list = ""
            slogan_obj = SloganAnalysisUsingSynonymousWords(docYear=year, sloganYear=i, number_per_doc=number_per_doc,number_per_len=number_per_len, country_id=Country, doc_ids=doc_id_list)
            create_list.append(slogan_obj)
            # print(f'ASNAD:{year}: slogan:{i} => {meanOfRepeat}')



    # print(document_slogan_id_dict)
    SloganAnalysisUsingSynonymousWords.objects.bulk_create(create_list)
