# from doc.models import FullProfileAnalysis, DocumentParagraphs, AnalysisKnowledgeGraph
# from collections import defaultdict
# from hazm import *
# from flair.data import Sentence
# from flair.models import SequenceTagger

# tagger = SequenceTagger.load("hamedkhaledi/persain-flair-upos")


# def arabicCharConvert(text):
#     arabic_char_dict = {"ى": "ی", "ئ": "ی", "ك": "ک", "آ": "ا", "أ": "ا", "إ": "ا", "ي": "ی", "ة": "ه", "ۀ": "ه",
#                         "\n\n": "\n", "\n ": "\n", }
#     for key, value in arabic_char_dict.items():
#         text = text.replace(key, value)

#     return text


# def preprocessing(text):
#     ignoreList = ["!", "@", "$", "%", "^", "&", "*", "_", "+", "-", "–", "/", "*", "'", "،", "؛", ",", "{", ",", ";",
#                   "!", "#", ":", "^", "‌", "(", ")",
#                   "}", '\xad', '­', "[", "]", "«", "»", "<", ">", ".", "?", "؟", "\n", "\t", '"']
#     for item in ignoreList:
#         text = text.replace(item, " ")

#     while "  " in text:
#         text = text.replace("  ", " ")

#     normalizer = Normalizer()
#     text = normalizer.normalize(text)

#     text = arabicCharConvert(text)

#     text = text.strip()

#     return text


# def apply(folder_name, Country):

#     AnalysisKnowledgeGraph.objects.filter(country_id=Country).delete()
#     analysis = []
#     print('paragraphs is going to select')
#     selected_paragraphs = FullProfileAnalysis.objects.filter(country_id=Country.id)
#     # x = []
#     # i = 0
#     counter = 0

#     for paragraph in selected_paragraphs:
#         counter += 1
#         approval_date = paragraph.document_paragraph.document_id.approval_date
#         try:
#             if approval_date != None and len(approval_date) > 4 and int(approval_date[:4]) >= 1360:

#                 para_text = paragraph.document_paragraph.text.replace("?", "."). \
#                     replace("؟", ".").replace("!", ".").replace("؛", ".").replace(";", ".") \
#                     .replace("ند،", "ند.").replace("رد،", "رد.").replace("ید،", "ید.").replace("یم،", "یم.")

#                 sentence_list = para_text.split(".")

#                 words = []
#                 person_list = paragraph.persons.split(";")
#                 locations_list = paragraph.locations.split(";")
#                 organizations_list = paragraph.organizations.split(";")
#                 for person in person_list:
#                     if person != '':
#                         words.append(person)
#                 for location in locations_list:
#                     if location != '':
#                         words.append(location)
#                 for organization in organizations_list:
#                     if organization != '' and organization != 'و':
#                         words.append(organization)

#                 if len(words) != 0:
#                     for sentence in sentence_list:
#                         '''para = sentence.split(" ")
#                         if '' in para:
#                             para.remove('')
#                         print(para)'''
#                         sentence1 = Sentence(sentence)
#                         tagger.predict(sentence1)
#                         POStaged = sentence1.to_tagged_string().split(" ")
#                         # print(POStaged)

#                         if POStaged[0] != '':
#                             posDic = {}
#                             para = []
#                             for i in range(len(POStaged)):
#                                 if (i % 2) == 0:
#                                     posDic[int(i / 2)] = POStaged[i + 1]
#                                     para.append(POStaged[i])
#                             # print(para)

#                             nouns = []
#                             for q in posDic.keys():
#                                 if posDic[q] == '<NOUN>':
#                                     nouns.append(q)

#                             pos_map = defaultdict(list)

#                             for pos, ele in enumerate(para):
#                                 pos_map[ele].append(pos)
#                             pos_map_dict = dict(pos_map)

#                             # words = [paragraph.organizations, paragraph.locations, paragraph.persons]
#                             # print(words)
#                             reduced_d = defaultdict(list, {k: v for k, v in pos_map.items() if k in words})
#                             reduced_d_dict = dict(reduced_d)

#                             dic2 = {}
#                             for element in reduced_d_dict.keys():
#                                 for element2 in reduced_d_dict.keys():
#                                     for x in reduced_d_dict[element]:
#                                         for y in reduced_d_dict[element2]:
#                                             var = (element, element2)
#                                             if var in dic2:
#                                                 dic2[element, element2].append(x - y)
#                                             else:
#                                                 dic2[element, element2] = []
#                                                 dic2[element, element2].append(x - y)

#                             dic3 = {}
#                             for d in dic2.keys():
#                                 for x in dic2[d]:
#                                     if 0 > x >= -3:
#                                         if d in dic3:
#                                             dic3[d].append(x)
#                                         else:
#                                             dic3[d] = []
#                                             dic3[d].append(x)

#                             resultDic = {}
#                             tempDic = {}
#                             resultDiccntx1 = {}
#                             resultDiccntx2 = {}
#                             tempDiccntx1 = {}
#                             tempDiccntx2 = {}
#                             for (x, y) in dic3.keys():
#                                 resultDic[(x, y)] = []
#                                 resultDiccntx1[(x, y)] = []
#                                 resultDiccntx2[(x, y)] = []
#                                 for c in pos_map_dict[x]:
#                                     for t in pos_map_dict[y]:
#                                         if 0 > c - t >= -8:
#                                             betlist = list(range(c + 1, t))
#                                             afterlist = list(range(t + 1, t + 9))
#                                             beforelist = list(range(c - 8, c))
#                                             intersecbetlist = list(set(betlist) & set(nouns))
#                                             intersecafterlist = list(set(afterlist) & set(nouns))
#                                             intersecbeforelist = list(set(beforelist) & set(nouns))
#                                             if len(intersecbetlist) != 0:
#                                                 maxbet = max(intersecbetlist)
#                                                 minbet = min(intersecbetlist)
#                                             if len(intersecafterlist) != 0:
#                                                 maxafter = max(intersecafterlist)
#                                                 minafter = min(intersecafterlist)
#                                             if len(intersecbeforelist) != 0:
#                                                 maxbefore = max(intersecbeforelist)
#                                                 minbefore = min(intersecbeforelist)
#                                             tempDic[(x, y)] = []
#                                             tempDiccntx1[(x, y)] = []
#                                             tempDiccntx2[(x, y)] = []
#                                             for d in pos_map_dict.keys():
#                                                 for h in pos_map_dict[d]:
#                                                     if len(intersecbetlist) != 0 and minbet <= h <= maxbet:
#                                                         tempDic[(x, y)].append(d)
#                                                     if len(intersecbeforelist) != 0 and minbefore <= h <= maxbefore:
#                                                         tempDiccntx1[(x, y)].append(d)
#                                                     if len(intersecafterlist) != 0 and minafter <= h <= maxafter:
#                                                         tempDiccntx2[(x, y)].append(d)
#                                             resultDic[(x, y)].append(tempDic[(x, y)])
#                                             resultDiccntx1[(x, y)].append(tempDiccntx1[(x, y)])
#                                             resultDiccntx2[(x, y)].append(tempDiccntx2[(x, y)])

#                             # x[i] = reduced_d
#                             # x[i] = paragraph('persons', 'locations', 'organizations')
#                             # i += 1
#                             # print(paragraph.id)
#                             print(len(resultDic))

#                             for (x, y) in resultDic:
#                                 k = 0
#                                 for z in resultDic[(x, y)]:
#                                     t = resultDiccntx1[(x, y)][k]
#                                     n = resultDiccntx2[(x, y)][k]
#                                     k += 1
#                                     Label_string = preprocessing(listToString(z))
#                                     cntx1_string = preprocessing(listToString(t))
#                                     cntx2_string = preprocessing(listToString(n))
#                                     ner1 = preprocessing(x)
#                                     ner2 = preprocessing(y)
#                                     if len(Label_string) > 0 and len(ner1) > 0 and len(ner2) > 0:
#                                         AnalysisKnowledgeGraph.objects.create(country=Country, side1ner=ner1,
#                                                                               side2ner=ner2,
#                                                                               Label=Label_string,
#                                                                               beforecontext=cntx1_string,
#                                                                               aftercontext=cntx2_string,
#                                                                               FullProfileAnalysis_id=paragraph)
#         except Exception as e:
#             pass

#         print('row of FullProfileAnalysis table done=', counter, 'P=%', round(counter/len(selected_paragraphs), 4))

#     print('finished successfully')


# def listToString(s):
#     # initialize an empty string
#     str1 = " "

#     # return string
#     return str1.join(s)
