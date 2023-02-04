from doc.models import Document, DocumentWords, DocumentParagraphs, DocumentActor, CUBE_Principles_FullData, \
    CUBE_Principles_ChartData, CUBE_Principles_TableData
from doc.models import CUBE_Template_FullData, CUBE_Template_ChartData, CUBE_Template_TableData
from doc.models import Template_Panels_Info
import time

def apply(folder_name, Country, host_url):

        create_FullData_CUBE(Country)

        create_ChartData_CUBE(Country)

        create_TableData_CUBE(Country, host_url)

        print("---------------------------------------------")

def create_FullData_CUBE(Country):
    print('')

def create_ChartData_CUBE(Country):
    start_t = time.time()

    batch_size = 1000

    CUBE_Principles_ChartData.objects.filter(country_id=Country).delete()

    text = ' اصل '
    principles = DocumentParagraphs.objects.filter(text__icontains=text, document_id__country_id=Country)
    principle_info = []

    for p in principles:
        if (text in p.text):
            start = p.text.index(text)
            end = len(p.text)
            for j, c in enumerate(p.text[start:]):
                if c == '؛' or c == '،' or c == '\n' or c == '.':
                    end = j + start
                    break


            principle_info.append(
                {'principle': p, 'name': p.text[start:end]})

    unique_principles = {}

    for p in principle_info:
        doc_id = p['principle'].document_id.id
        if p['name'] in unique_principles and not doc_id in unique_principles[p['name']]:
            unique_principles[p['name']][doc_id] = p
        else:
            unique_principles[p['name']] = {}
            unique_principles[p['name']][doc_id] = p


    cubes = []
    for name, item in unique_principles.items():

        approval_references_data = {}
        level_data = {}
        approval_year_data = {}
        type_data = {}
        subject_data = {}
        principles_information_result = []

        for doc_id, p in item.items():

            # Generate Document List Table Data
            document_id = p['principle'].document_id.id
            document_information = GetDocumentById_Local(document_id)

            document_information['principle_name'] = name
            principles_information_result.append(document_information)

            # Generate chart Data
            subject_id = document_information["subject_id"]
            subject_name = document_information["subject"]
            approval_references_id = document_information["approval_reference_id"]
            approval_references_name = document_information["approval_reference"]
            level_id = document_information["level_id"]
            level_name = document_information["level"]
            type_id = document_information["type_id"]
            type_name = document_information["type"]
            doc_approval_year = document_information["approval_date"]

            # ---------- Generate Data -------------

            if doc_approval_year != "نامشخص":
                doc_approval_year = document_information["approval_date"][0:4]

            if subject_id not in subject_data:
                subject_data[subject_id] = {"name": subject_name, "count": [doc_id]}
            else:
                subject_data[subject_id]["count"].append(doc_id)

            if approval_references_id not in approval_references_data:
                approval_references_data[approval_references_id] = {
                    "name": approval_references_name, "count": [doc_id]}
            else:
                approval_references_data[approval_references_id]["count"].append(doc_id)

            if level_id not in level_data:
                level_data[level_id] = {"name": level_name, "count":[doc_id]}
            else:
                level_data[level_id]["count"].append(doc_id)

            if type_id not in type_data:
                type_data[type_id] = {"name": type_name, "count":[doc_id]}
            else:
                type_data[type_id]["count"].append(doc_id)

            if doc_approval_year not in approval_year_data:
                approval_year_data[doc_approval_year] = {
                    "name": doc_approval_year, "count":[doc_id]}
            else:
                approval_year_data[doc_approval_year]["count"].append(doc_id)

        subject_chart_data = []
        approval_reference_chart_data = []
        level_chart_data = []
        approval_year_chart_data = []
        type_chart_data = []

        for key, value in subject_data.items():
            subject_chart_data.append([key, value])

        for key, value in approval_references_data.items():
            approval_reference_chart_data.append([key, value])

        for key, value in level_data.items():
            level_chart_data.append([key, value])

        for key, value in approval_year_data.items():
            approval_year_chart_data.append([key, value])

        for key, value in type_data.items():
            type_chart_data.append([key, value])

        subject_chart_data_json = {"data": subject_chart_data}
        level_chart_data_json = {"data": level_chart_data}
        type_chart_data_json = {"data": type_chart_data}
        approval_reference_chart_data_json = {"data": approval_reference_chart_data}
        approval_year_chart_data_json = {"data": approval_year_chart_data}
        documents_information_result_json = {"data": principles_information_result}
        cube_obj = CUBE_Principles_ChartData(
            country_id=Country,
            principle_name = name,
            subject_chart_data=subject_chart_data_json,
            level_chart_data=level_chart_data_json,
            type_chart_data=type_chart_data_json,
            approval_reference_chart_data=approval_reference_chart_data_json,
            approval_year_chart_data=approval_year_chart_data_json,
            documents_information_result_data = documents_information_result_json
        )

        cubes.append(cube_obj)

        if cubes.__len__() > batch_size:
            CUBE_Principles_ChartData.objects.bulk_create(cubes)
            cubes = []
    CUBE_Principles_ChartData.objects.bulk_create(cubes)

    end_t = time.time()
    print('CUBE_ChartData added (' + str(end_t - start_t) + ').')

def GetDocumentById_Local(id):
    document = Document.objects.get(id=id)

    approval_ref = "نامشخص"
    if document.approval_reference_id != None:
        approval_ref = document.approval_reference_name

    approval_date = "نامشخص"
    if document.approval_date != None:
        approval_date = document.approval_date

    subject_name = "نامشخص"
    if document.subject_id != None:
        subject_name = document.subject_name

    level_name = "نامشخص"
    if document.level_id != None:
        level_name = document.level_name

    type_name = "نامشخص"
    if document.type_id != None:
        type_name = document.type_name

    result = {
              "subject_id": document.subject_id_id,
              "subject": subject_name,
              "approval_reference_id": document.approval_reference_id_id,
              "approval_reference": approval_ref,
              "approval_date": approval_date,
              "level": level_name,
              "level_id": document.level_id_id,
              "type_id": document.type_id_id,
              "type": type_name,
              "name": document.name,
              "id": document.id,
              "country": document.country_id.name
    }
    return result

def create_TableData_CUBE(Country, host_url):
    start_t = time.time()

    batch_size = 250

    CUBE_Principles_TableData.objects.filter(country_id=Country).delete()

    text = ' اصل '
    principles = DocumentParagraphs.objects.filter(text__icontains=text, document_id__country_id=Country)

    principle_info = []
    document_information_dict = {}
    for p in principles:
        if (text in p.text):
            start = p.text.index(text)
            end = len(p.text)
            for j, c in enumerate(p.text[start:]):
                if c == '؛' or c == '،' or c == '\n' or c == '.':
                    end = j+start
                    break
            doc_id = p.document_id.id


            doc_info = GetDocumentById_Local(doc_id)
            principle_name = p.text[start:end]
            principle_info.append({'id': p.document_id.id, 'name': principle_name, 'document_name': p.document_id.name,
                           'subject': doc_info['subject'], 'approval_references': doc_info['approval_reference'],
                           'approval_date': doc_info['approval_date'], 'text': p.text})

    unique_principles = {}

    for p in principle_info:
        if p['name'] in unique_principles:
            unique_principles[p['name']].append(p)
        else:
            unique_principles[p['name']] = [p]

    index = 1
    cubes = []
    for name, item in unique_principles.items():
        result_list = []

        for p in item:
            id = p['id']
            name = p['name']
            document_name = p['document_name']
            subject = p['subject']
            approval_reference = p['approval_references']
            approval_date = p['approval_date']

            detail_function = "DetailFunction('{0}', '{1}', '{2}')".format(name, p['text'], document_name)
            detail = '<button type="button" class="btn modal_btn" data-bs-toggle="modal" ' + ' onclick="' + detail_function + '" data-bs-target="#myModal">جزئیات</button>'

            document_link = 'http://' + host_url + "/information/?id=" + str(id)

            document_tag = '<a target="to_blank" href="' + document_link + '">' + document_name + "</a>"



            json_value = {"id": index, "name": name, "document_name": document_name,"document_tag":document_tag, "subject": subject, "approval_reference": approval_reference, "approval_date": approval_date, "detail": detail}

            result_list.append(json_value)
            index += 1

        table_data_json = {
            "data": result_list
        }

        cube_obj = CUBE_Principles_TableData(
            country_id=Country,
            text = name,
            table_data=table_data_json)

        cubes.append(cube_obj)

        if cubes.__len__() > batch_size:
            CUBE_Principles_TableData.objects.bulk_create(cubes)
            cubes = []

    CUBE_Principles_TableData.objects.bulk_create(cubes)

    end_t = time.time()
    print('CUBE_TableData added (' + str(end_t - start_t) + ').')


