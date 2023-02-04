# import math
# import operator
# import sys
# from scripts.parallel import Parallel
#
# from en_doc.models import DocumentSubject, SubjectKeyWords, Subject, Document, DocumentSubjectKeywords, DocumentParagraphs, \
#     Level, Country as CountryTBL
# from django.db.models import Count, Q
# import time
#
# def normalize_dict(subject_dict):
#     if (sum(subject_dict.values())) == 0:
#         factor = 0
#     else:
#         factor = 1.0 / sum(subject_dict.values())
#
#     for k in subject_dict:
#         subject_dict[k] = round(subject_dict[k] * factor, 2)
#
#     return subject_dict
#
#
# class DocsSubjectExtractor(Parallel):
#     result_key = ['create_list_subject_keyword', 'create_list_document_subject']
#     documents_text_cache = {}
#     searchClass = None
#
#     def __init__(self):
#         super(DocsSubjectExtractor, self).__init__()
#         self.registerParallelPhase((self.middle, self.parallelPhase2))
#         self.progressSC = self.Progress(text='Search in content')
#
#     def clearModel(self, Country):
#         Document.objects.filter(country_id=Country).update(subject_id=None)
#         DocumentSubjectKeywords.objects.filter(document_id__country_id=Country).delete()
#         DocumentSubject.objects.filter(document_id__country_id=Country).delete()
#
#     def start(self, folderName, Country, **arg):
#         # si_level = Level.objects.filter(name__in=["Order", "Regulations", "Rules", "Scheme", "Direction", "Declaration"])
#         subject_list = Subject.objects.filter(language="انگلیسی")
#         keyword_list = SubjectKeyWords.objects.all()
#         document_list = list(Document.objects.filter(country_id=Country))
#         self.argument = {'keyword_list': keyword_list, 'subject_list':subject_list, 'document_list':document_list}
#         # DocumentParagraphs_List = DocumentParagraphs.objects.filter(document_id__country_id=Country)
#
#         return document_list
#
#     def parallelPhase(self, li, threadNumber, keyword_list, subject_list, document_list):
#
#         # search in Title and add
#         for document in li:
#             document_name = document.name
#             for keyword in keyword_list:
#                 subject_name = keyword.word
#                 keyword_id = keyword.id
#                 if subject_name in document_name:
#                     doc_docsubject_obj = DocumentSubjectKeywords(document_id_id=document.id, subject_keyword_id_id=keyword_id, count=1, place="Title")
#                     self.addResult('create_list_subject_keyword', doc_docsubject_obj, threadNumber)
#
#         # search in Content
#         DocumentParagraphs_List = DocumentParagraphs.objects.filter(document_id__in=li)
#
#         topic_count_keyword = {}
#         for keyword in keyword_list:
#             topic_count_keyword[keyword.id] = {}
#
#         self.progressSC.addLen(len(DocumentParagraphs_List))
#         for paragraph in DocumentParagraphs_List:
#             self.progressSC.progress()
#             doc_id = paragraph.document_id_id
#             paragraph_text = paragraph.text
#             for subject in keyword_list:
#                 subject_name = subject.word
#                 subject_id = subject.id
#                 if subject_name in paragraph_text:
#                     keyword_count = paragraph_text.count(subject_name)
#                     if doc_id in topic_count_keyword[subject_id]:
#                         topic_count_keyword[subject_id][doc_id] += keyword_count
#                     else:
#                         topic_count_keyword[subject_id][doc_id] = keyword_count
#
#         # add keyword count in Content
#         for keyword_id in topic_count_keyword:
#             for doc_id in topic_count_keyword[keyword_id]:
#                 count = topic_count_keyword[keyword_id][doc_id]
#
#                 doc_docsubject_obj = DocumentSubjectKeywords(document_id_id=doc_id, subject_keyword_id_id=keyword_id, count=count, place="Text")
#                 self.addResult('create_list_subject_keyword', doc_docsubject_obj, threadNumber)
#
#
#     def middle(self, folderName, Country, **arg):
#         self.statusProgress.setText('Calculate Score')
#         create_list = self.getResult('create_list_subject_keyword')
#         self.bulk_create_array(DocumentSubjectKeywords, create_list)
#
#         si_level = Level.objects.filter(
#             name__in=["Order", "Regulations", "Rules", "Scheme", "Direction", "Declaration"])
#         self.argument['si_level'] = si_level
#         document_list = arg['document_list']
#         del self.argument['keyword_list']
#         del self.argument['document_list']
#         return document_list
#
#     def parallelPhase2(self, li, threadNumber, subject_list, si_level):
#         # Calculate Score
#         for doc in li:
#             self.statusProgress.progress()
#             subject_score = {}
#             for subject in subject_list:
#                 DocSubjectKeywords = DocumentSubjectKeywords.objects.filter(document_id=doc,
#                                                                             subject_keyword_id__subject_id=subject)
#                 score = 0
#                 for keyword in DocSubjectKeywords:
#                     if keyword.place == "Text":
#                         score += 1 * keyword.count
#                     elif keyword.place == "Title":
#                         score += 20 * keyword.count
#                 subject_score[subject.id] = score
#
#             if doc.level_id in si_level:
#                 level_para = DocumentParagraphs.objects.get(text="STATUTORY INSTRUMENTS", document_id=doc)
#                 found_subject = DocumentParagraphs.objects.filter(document_id=doc, number__gt=level_para.number,
#                                                                   number__lte=level_para.number + 5)
#                 sub_id = None
#                 for fs in found_subject:
#                     temp = Subject.objects.filter(name__iexact=fs.text)
#                     if temp.count() > 0:
#                         sub_id = temp
#                         break
#                 if sub_id is None:
#                     pass
#                     # print(f'can not find subject: {doc.name}')
#                     # print(f'paras:{"".join([x.text+newline for x in found_subject])}')
#                 else:
#                     DocumentSubject.objects.create(document_id=doc, subject_id=sub_id[0], measure_id_id=1, weight=1)
#                     Document.objects.filter(id=doc.id).update(subject_id=sub_id[0])
#                     subject_score[sub_id[0].id] = 0
#                     sub_keyword = SubjectKeyWords.objects.get(word=sub_id[0].name)
#                     DocumentSubjectKeywords.objects.create(document_id=doc, subject_keyword_id=sub_keyword, count=1,
#                                                            place="Specified by document")
#
#             subject_score = normalize_dict(subject_score)
#             subject_score = dict(sorted(subject_score.items(), key=operator.itemgetter(1), reverse=True))
#             doc_sub_id = list(subject_score.keys())[0]
#             if subject_score[doc_sub_id] > 0:
#                 Document.objects.filter(id=doc.id, subject_id_id=None).update(subject_id_id=doc_sub_id)
#
#             for subject_id, score in subject_score.items():
#                 if score > 0:
#                     doc_docsubject_obj = DocumentSubject(document_id=doc, subject_id_id=subject_id, measure_id_id=1,
#                                                          weight=score)
#                     self.addResult('create_list_document_subject', doc_docsubject_obj, threadNumber)
#
#
#     def end(self, res, **arg):
#         self.bulk_create_array(DocumentSubject, res['create_list_document_subject'])
#
#
#
# def apply(folder_name, Country):
#
#     Document.objects.filter(country_id=Country).update(subject_id=None)
#     si_level = Level.objects.filter(name__in=["Order", "Regulations", "Rules", "Scheme", "Direction", "Declaration"])
#     DocumentSubjectKeywords.objects.filter(document_id__country_id=Country).delete()
#     DocumentSubject.objects.filter(document_id__country_id=Country).delete()
#
#     subject_list = Subject.objects.filter(language="انگلیسی")
#     batch_size = 10000
#
#     DocumentParagraphs_List = DocumentParagraphs.objects.filter(document_id__country_id=Country)
#
#     total = subject_list.count()
#     counter = 1
#
#     Create_List = []
#
#     for subject in subject_list:
#         print("\033[A                                        \033[A")
#         print(f'detecting subjects in paragraphs: {counter}/{total}')
#         counter += 1
#         keyword_list = SubjectKeyWords.objects.filter(subject_id=subject)
#         # print()
#         for key in keyword_list:
#             keyword = key.word
#             # Keyword in Text
#             docs_list = DocumentParagraphs_List.filter((Q(text__icontains= " " + keyword + " ") | Q(text__startswith=keyword) | Q(text__endswith=keyword)))
#             docs_list = docs_list.values("document_id_id").annotate(count=Count('document_id_id'))
#
#             # t = time.time()
#             for doc in docs_list:
#                 # r = time.time()
#                 doc_id = doc["document_id_id"]
#                 count = doc["count"]
#                 doc_docsubject_obj = DocumentSubjectKeywords(document_id_id=doc_id, subject_keyword_id=key, count=count, place="Text")
#                 Create_List.append(doc_docsubject_obj)
#                 # print("\t", time.time() - r)
#
#             # print("time1", time.time() - t)
#
#             #keyword in Title
#             docs_list = Document.objects.filter(Q(country_id=Country) & (Q(name__icontains=" " + keyword + " ") | Q(name__startswith=keyword) | Q(name__endswith=keyword)))
#             # t = time.time()
#             for doc in docs_list:
#                 doc_id = doc.id
#                 count = 1
#                 doc_docsubject_obj = DocumentSubjectKeywords(document_id_id=doc_id, subject_keyword_id=key, count=count,
#                                                    place="Title")
#                 Create_List.append(doc_docsubject_obj)
#             # print("time2", time.time()-t)
#
#
#             if Create_List.__len__() > batch_size:
#                 DocumentSubjectKeywords.objects.bulk_create(Create_List)
#                 Create_List = []
#
#     DocumentSubjectKeywords.objects.bulk_create(Create_List)
#
#     #Calculate Score
#     docs_list = Document.objects.filter(country_id=Country)
#     total = docs_list.count()
#     counter = 1
#     Create_List = []
#     for doc in docs_list:
#         print("\033[A                                                       \033[A")
#         print(f'calculating subjects\' weight for each document: {counter}/{total}')
#         counter+=1
#         subject_score = {}
#         for subject in subject_list:
#             DocSubjectKeywords = DocumentSubjectKeywords.objects.filter(document_id=doc, subject_keyword_id__subject_id=subject)
#             score = 0
#             for keyword in DocSubjectKeywords:
#                 if keyword.place == "Text":
#                     score += 1*keyword.count
#                 elif keyword.place == "Title":
#                     score += 20*keyword.count
#             subject_score[subject.id] = score
#
#
#         if doc.level_id in si_level:
#             level_para = DocumentParagraphs.objects.get(text="STATUTORY INSTRUMENTS",document_id=doc)
#             found_subject = DocumentParagraphs.objects.filter(document_id=doc, number__gt=level_para.number,number__lte=level_para.number + 5)
#             sub_id = None
#             for fs in found_subject:
#                 temp = Subject.objects.filter(name__iexact=fs.text)
#                 if temp.count() > 0:
#                     sub_id = temp
#                     break
#             if sub_id is None:
#                 pass
#                 # print(f'can not find subject: {doc.name}')
#                 # print(f'paras:{"".join([x.text+newline for x in found_subject])}')
#             else:
#                 DocumentSubject.objects.create(document_id=doc, subject_id=sub_id[0], measure_id_id=1, weight=1)
#                 Document.objects.filter(id=doc.id).update(subject_id=sub_id[0])
#                 subject_score[sub_id[0].id] = 0
#                 sub_keyword = SubjectKeyWords.objects.get(word=sub_id[0].name)
#                 DocumentSubjectKeywords.objects.create(document_id=doc, subject_keyword_id=sub_keyword, count=1,
#                                                        place="Specified by document")
#
#         subject_score = normalize_dict(subject_score)
#         subject_score = dict(sorted(subject_score.items(), key=operator.itemgetter(1), reverse=True))
#         doc_sub_id = list(subject_score.keys())[0]
#         if subject_score[doc_sub_id] > 0:
#             Document.objects.filter(id=doc.id,subject_id_id=None).update(subject_id_id=doc_sub_id)
#
#         for subject_id, score in subject_score.items():
#             if score > 0:
#                 doc_docsubject_obj = DocumentSubject(document_id=doc, subject_id_id=subject_id, measure_id_id=1, weight=score)
#                 Create_List.append(doc_docsubject_obj)
#
#         if Create_List.__len__() > batch_size:
#             DocumentSubject.objects.bulk_create(Create_List)
#             Create_List = []
#
#     DocumentSubject.objects.bulk_create(Create_List)
#
#
#
#
#
