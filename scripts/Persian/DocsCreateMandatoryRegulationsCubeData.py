from doc.models import Document, DocumentParagraphs, CUBE_MandatoryRegulations_TableData, DocumentClause, Actor, \
    DocumentGeneralDefinition, CUBE_MandatoryRegulations_ChartData, ActorCategory
import time

from functools import reduce
from django.db.models import Q
import operator



def apply(folder_name, Country, host_url):
    create_TableData_CUBE(Country, host_url)


def create_TableData_CUBE(Country, host_url):
    batch_size = 10000
    start_t = time.time()
    # clause_types = ['ماده', 'تبصره', 'بند', 'جزء']
    result_list = []

    CUBE_MandatoryRegulations_TableData.objects.filter(country_id=Country).delete()
    CUBE_MandatoryRegulations_ChartData.objects.filter(country_id=Country).delete()

    regulation_documents = Document.objects.filter(country_id=Country)

    regulation_forms = [
        'ایین نامه',
        'ائین نامه',
        'ایین‌نامه',
        'ائین‌نامه',
        'ایین­نامه',
    ]
    result_patterns = [form + (' ' + 'اجرایی') for form in regulation_forms]

    regulation_documents = regulation_documents.filter(
        reduce(operator.or_, (Q(name__istartswith=pt) for pt in result_patterns)))


    non_collective_actors = Actor.objects.exclude(actor_category_id__name='کنشگران جمعی')
    # collective_actors = Actor.objects.filter(actor_category_id__name='کنشگران جمعی')
    category_list = ActorCategory.objects.all().exclude(name='سایر').exclude(name='اشخاص').exclude(name='کنشگران جمعی')


    subject_data = {}
    approval_references_data = {}
    approval_year_data = {}
    documents_information_result = []


    for doc in regulation_documents:
        # print(index/regulation_documents.__len__())
        # clauses_indices = []
        # clauses = []
        # matter = ''
        # paras = []
        # law_name = ''
        # law_id = ''
        # law_tag = ''
        # detail = ''
        regulator_id = str(doc.id)
        regulator_name = str(doc.name)
        regulator_link = 'http://' + host_url + "/information/?id=" + regulator_id
        regulator_tag = '<a ' + 'target="to_blank" href="' + regulator_link + '">' + regulator_name + "</a>"

        # # detect Law
        # document_name = doc.name
        # temp = document_name.split('قانون')
        # if len(temp) == 1:
        #     # print(f'doc {doc.id} (id) doesn\'t contain word "قانون"')
        #     unknown = True
        # elif len(temp) > 2:
        #     # print(f'doc {doc.id} (id) contains more than one "قانون"')
        #     unknown = True
        # else:
        #     law_doc = Document.objects.filter(name='قانون' + temp[1])
        #     unknown = law_doc.count() < 1

        # if not unknown:
        #     law_doc = law_doc[0]
        #     doc_clause = DocumentClause.objects.filter(document_id=law_doc)
        #
        #     # detect clauses
        #     clause = temp[0].split("اجرایی")[1].strip()
        #     for clause_type in clause_types:
        #         clauses_indices += [m.start() for m in re.finditer(clause_type, clause)]
        #     clauses_indices.sort()
        #     for index, clauses_index in enumerate(clauses_indices):
        #         if index == len(clauses_indices) - 1:
        #             clauses.append(clause[clauses_index:])
        #             break
        #         clauses.append(clause[clauses_index:clauses_indices[index + 1]])
        #
        #     # detect paragraphs
        #     paras = set(DocumentCompleteParagraphs.objects.filter(document_id=law_doc).values_list('id', flat=True))
        #     old_paras = paras
        #     if len(paras) == 0:
        #         continue
        #     max_para_id = max(paras)
        #     last_found_clause = None
        #
        #
        #     for i in range(len(clauses) - 1, -1, -1):
        #         clause = clauses[i].strip()
        #         # print(clause)
        #         if has_madeh(clause + "-"):
        #             same_as_old = last_found_clause is not None and last_found_clause.clause_type == 'ماده'
        #             num = detect_num_or_num(clause, 'ماده')
        #             matter = 'ماده ' + (num if num is not None else '') + " ," + matter
        #
        #             stop = (max(old_paras) if same_as_old else max(paras)) + 2
        #             start = (min(old_paras) if same_as_old else min(paras))
        #             made = doc_clause.filter(Q(stop_paragraph_id_id__lt=stop) | Q(stop_paragraph_id__isnull=True),
        #                                      clause_type='ماده',
        #                                      start_paragraph_id_id__gte=start,
        #                                      clause_number=num)
        #
        #             if made.count() != 1:
        #                 continue
        #
        #             new_paras = get_clause_paragraphs(made[0], max_para_id)
        #             if len(new_paras) == 0:
        #                 continue
        #
        #             if same_as_old:
        #                 if new_paras.issubset(old_paras):
        #                     paras |= new_paras
        #             else:
        #                 if new_paras.issubset(paras):
        #                     old_paras = paras
        #                     paras = new_paras
        #             last_found_clause = made[0]
        #
        #
        #         elif has_tabsare(clause + "-"):
        #             same_as_old = last_found_clause is not None and last_found_clause.clause_type == 'تبصره'
        #             num = detect_num_or_num(clause, 'تبصره')
        #             if doc.id == 565:
        #                 print(matter)
        #             matter = 'تبصره ' + (num if num is not None else '') + " ," + matter
        #             if doc.id == 565:
        #                 print(matter)
        #             stop = (max(old_paras) if same_as_old else max(paras)) + 2
        #             start = (min(old_paras) if same_as_old else min(paras))
        #             tabsare = doc_clause.filter(Q(stop_paragraph_id_id__lt=stop) | Q(stop_paragraph_id__isnull=True),
        #                                         clause_type='تبصره',
        #                                         start_paragraph_id_id__gte=start,
        #                                         clause_number=num)
        #
        #             if tabsare.count() != 1:
        #                 continue
        #             new_paras = get_clause_paragraphs(tabsare[0], max_para_id)
        #             if len(new_paras) == 0:
        #                 continue
        #             if same_as_old:
        #                 if new_paras.issubset(old_paras):
        #                     paras |= new_paras
        #             else:
        #                 if new_paras.issubset(paras):
        #                     old_paras = paras
        #                     paras = new_paras
        #             last_found_clause = tabsare[0]
        #
        #         elif has_joze(clause + "-"):
        #             same_as_old = last_found_clause is not None and last_found_clause.clause_type == 'جزء'
        #             num = detect_num_or_num(clause, 'جزء')
        #             matter = 'جزء ' + (num if num is not None else '') + " ," + matter
        #             # print(matter)
        #             stop = (max(old_paras) if same_as_old else max(paras)) + 2
        #             start = (min(old_paras) if same_as_old else min(paras))
        #             joze = doc_clause.filter(Q(stop_paragraph_id_id__lt=stop) | Q(stop_paragraph_id__isnull=True),
        #                                      clause_type='جزء',
        #                                      start_paragraph_id_id__gte=start,
        #                                      clause_number=num)
        #
        #             if joze.count() != 1:
        #                 continue
        #
        #             new_paras = get_clause_paragraphs(joze[0], max_para_id)
        #             if len(new_paras) == 0:
        #                 continue
        #             if same_as_old:
        #                 if new_paras.issubset(old_paras):
        #                     paras |= new_paras
        #             else:
        #                 if new_paras.issubset(paras):
        #                     old_paras = paras
        #                     paras = new_paras
        #             last_found_clause = joze[0]
        #
        #
        #         elif has_band(clause + "-"):
        #             same_as_old = last_found_clause is not None and last_found_clause.clause_type == 'بند'
        #             num = detect_num_or_num(clause, 'بند')
        #             matter = 'بند ' + (num if num is not None else '') + " ," + matter
        #             # print(matter)
        #             stop = (max(old_paras) if same_as_old else max(paras)) + 2
        #             start = (min(old_paras) if same_as_old else min(paras))
        #             band = doc_clause.filter(Q(stop_paragraph_id_id__lt=stop) | Q(stop_paragraph_id__isnull=True),
        #                                      clause_type='بند',
        #                                      start_paragraph_id_id__gte=start,
        #                                      clause_number=num)
        #
        #             if band.count() != 1:
        #                 continue
        #             new_paras = get_clause_paragraphs(band[0], max_para_id)
        #             if len(new_paras) == 0:
        #                 continue
        #             if same_as_old:
        #                 if new_paras.issubset(old_paras):
        #                     paras |= new_paras
        #             else:
        #                 if new_paras.issubset(paras):
        #                     old_paras = paras
        #                     paras = new_paras
        #             last_found_clause = band[0]
        #
        #     # print("______________________________")
        #
        #     law_id = str(law_doc.id)
        #     law_name = str(law_doc.name)
        #     law_link = 'http://' + host_url + "/information/?id=" + law_id
        #     law_tag = '<a ' + 'target="to_blank" href="' + law_link + '">' + law_name + "</a>"
        #
        #     detail_function = "DetailFunction(" + regulator_id + ")"
        #     detail = '<button type="button" class="btn modal_btn" data-bs-toggle="modal" onclick="' + detail_function + '" data-bs-target="#myModal">جزئیات</button> '


        # paras = list(paras)
        # paras.sort()

        supervision_paragraphs,supervisions = getSupervision(doc.id,non_collective_actors,category_list,host_url,str(Country.id))

        detail_function = "DetailFunction(" + regulator_id + ")"
        detail = f'<button {("" if len(supervision_paragraphs)>0 else "disabled")} type="button" class="btn modal_btn" data-bs-toggle="modal" onclick="' + detail_function + '" data-bs-target="#myModal">جزئیات</button> '

        json_value = {
            'supervision_paragraphs':supervision_paragraphs,
            'supervisions':supervisions,
            "detail": detail,
            "regulator": regulator_tag,
            "id": regulator_id,
            "name": regulator_name,
            # "law": law_tag,
            # "law_id": law_id,
            # "law_name": law_name,
            # "matter": matter[:-2] if len(matter) > 1 else matter,
            # "paragraphs": paras,
            # 'is_unknown': unknown,
        }
        cube_obj = CUBE_MandatoryRegulations_TableData(
            country_id=Country,
            document_id=doc,
            table_data=json_value)
        result_list.append(cube_obj)

        if len(result_list) > batch_size:
            CUBE_MandatoryRegulations_TableData.objects.bulk_create(result_list)
            result_list = []

        # Generate chart Data
        document_information = GetDocumentById_Local(regulator_id)
        documents_information_result.append(document_information)
        subject_id = document_information["subject_id"]
        subject_name = document_information["subject"]
        approval_references_id = document_information["approval_reference_id"]
        approval_references_name = document_information["approval_reference"]
        doc_approval_year = document_information["approval_date"]
        if doc_approval_year != "نامشخص":
            doc_approval_year = document_information["approval_date"][0:4]

        if subject_id not in subject_data:
            subject_data[subject_id] = {"name": subject_name, "count": 1}
        else:
            subject_data[subject_id]["count"] += 1

        if approval_references_id not in approval_references_data:
            approval_references_data[approval_references_id] = {
                "name": approval_references_name, "count": 1}
        else:
            approval_references_data[approval_references_id]["count"] += 1

        if doc_approval_year not in approval_year_data:
            approval_year_data[doc_approval_year] = {
                "name": doc_approval_year, "count": 1}
        else:
            approval_year_data[doc_approval_year]["count"] += 1

    CUBE_MandatoryRegulations_TableData.objects.bulk_create(result_list)

    json_value = {
        'documents_information_result': documents_information_result,
        'subject_chart_data': subject_data,
        'approval_references_chart_data': approval_references_data,
        'approval_year_chart_data': approval_year_data,
    }
    CUBE_MandatoryRegulations_ChartData.objects.create(country_id=Country,chart_data=json_value)

    end_t = time.time()
    print('CUBE_TableData and CUBE_ChartData added (' + str(end_t - start_t) + ')')


def getSupervision(doc_id,actors,category_list,host_url,country_id):
    supervisions = []
    supervision_paragraphs = []

    # get all paragraphs whit pattern
    paragraphs = DocumentParagraphs.objects.filter(document_id=doc_id)
    patterns = 'حسن اجرای این'
    paragraphs = paragraphs.filter(text__icontains=patterns)



    for paragraph in paragraphs:
        text = paragraph.text.strip()



        # remove irrelevant sentences
        text = '.' + text + ('' if text.endswith('.') else '.')
        sentences_start = []
        index = text.find('.')
        while index != -1:
            sentences_start.append(index)
            index = text.find('.', index + 1)
        index = text.find(patterns)
        sentence_start_index = max([k for k in sentences_start if k < index])
        sentence_stop_index = min([k for k in sentences_start if index < k])
        text = text[sentence_start_index:sentence_stop_index].strip()


        if 'نظارت' not in text:
            continue
        supervision_paragraphs.append(paragraph.text)

        # detect general definition supervisions
        for category in category_list:
            category_name = category.name
            if category_name not in text:
                continue
            general_def_obj = DocumentGeneralDefinition.objects.filter(
                document_id=doc_id,
                keyword__icontains=category_name)

            special_underline = 'ـ'
            if general_def_obj.count() == 0:
                continue

            for general_def_obj_ in general_def_obj:

                if general_def_obj_.keyword.replace(special_underline,'-').replace(')','-').\
                        split('-')[-1].strip() != category_name:
                    continue

                ref_actor = general_def_obj_.text.strip()

                if ref_actor[-1] == '.':
                    ref_actor = ref_actor[:-1]

                ref_actor = ref_actor.replace(' جمهوری اسلامی ایران', '').replace(' ایران', '').replace(' کشور', '')

                actor_obj = Actor.objects.filter(actor_category_id=category,
                                                 forms__icontains=ref_actor)

                if actor_obj.count() == 0:
                    continue

                actor_obj = actor_obj[0]

                supervision = {'form': category_name}
                popover_title = category_name
                popover_content = ref_actor
                actor_tag_form = '<a style="color: inherit;" dir="rtl" tabindex="0" class="d-inline-block text-right bold"  data-bs-placement="bottom" role="button" data-bs-toggle="popover" data-bs-trigger="focus" title="' + popover_title + '" data-bs-content="' + popover_content + '">' + popover_title + '</a>'
                supervision['tag_form'] = actor_tag_form
                supervisions.append(supervision)

                supervision = {'name': actor_obj.name, 'form': '%#'}
                actor_link = 'http://' + host_url + "/actors_information/?country_id=" + country_id + "/?actor_id=" + \
                             str(actor_obj.id)
                actor_tag = '<a class="mb-2 mt-2" target="to_blank" href="' + actor_link + '">' + actor_obj.name + "</a>"
                supervision['tag_name'] = actor_tag
                supervisions.append(supervision)


        # detect actor supervisions
        for actor in actors:
            forms = actor.forms.split('/')
            for form in forms:
                form = form.strip()
                if form not in text:
                    continue
                old_supervision = None
                for supervision in supervisions:
                    if 'name' in supervision.keys() and supervision['name'] == actor.name:
                        old_supervision = supervision
                if old_supervision is not None:
                    supervisions.remove(old_supervision)

                supervision = {'name':actor.name,'form':form}
                actor_link = 'http://' + host_url + "/actors_information/?country_id=" + country_id + "/?actor_id=" + str(actor.id)
                actor_tag = '<a class="mb-2 mt-2" target="to_blank" href="' + actor_link + '">' + actor.name + "</a>"
                actor_tag_form = '<a style="display: inline;color: inherit;" target="to_blank" href="' + actor_link + '">' + form + "</a>"
                supervision['tag_name'] = actor_tag
                supervision['tag_form'] = actor_tag_form
                supervisions.append(supervision)
                break




    return supervision_paragraphs,supervisions



def get_doc_clause_types(document_name, clause_types):
    result_clauses = []

    for clause_type in clause_types:
        if clause_type in document_name:
            result_clauses.append(clause_type)

    return result_clauses


def get_clause_paragraphs(clause: DocumentClause, max_para_id: int):
    start = clause.start_paragraph_id.id
    stop = clause.stop_paragraph_id
    if stop is not None:
        stop = stop.id - 1
    else:
        stop = max_para_id
    result = []
    for i in range(start, stop + 1):
        result.append(i)
    return set(result)


def GetDocumentById_Local(id):
    document = Document.objects.get(id=id)

    approval_ref = "نامشخص"
    if document.approval_reference_id != None:
        approval_ref = document.approval_reference_name

    approval_date = "نامشخص"
    approval_year = "نامشخص"
    if document.approval_date != None:
        approval_date = document.approval_date
        approval_year = approval_date[0:4]


    subject_name = "نامشخص"
    if document.subject_id != None:
        subject_name = document.subject_name


    type_name = "سایر"
    if document.type_id != None:
        type_name = document.type_name


    level_name = "نامشخص"
    if document.level_id != None:
        level_name = document.level_name

    result = {
        "id": document.id,
        "name": document.name,
        "country_id": document.country_id_id,
        "country": document.country_id.name,
        "subject_id": document.subject_id_id,
        "subject": subject_name,
        "level_id": document.level_id_id,
        "level": level_name,
        "type_id": document.type_id_id,
        "type": type_name,
        "approval_reference_id": document.approval_reference_id_id,
        "approval_reference": approval_ref,
        "approval_date": approval_date,
        "approval_year": approval_year,
    }
    return result
