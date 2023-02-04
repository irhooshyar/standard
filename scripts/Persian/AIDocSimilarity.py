import re
from scripts.Persian import Preprocessing
from doc.models import Document, DocumentParagraphs, AISimilarityDoc
import torch
import tensorflow as tf
# from transformers import BertTokenizer, TFBertModel
from transformers import AutoConfig, AutoTokenizer, AutoModel
from hazm import sent_tokenize, Normalizer
import numpy as np
from scipy import spatial

normalizer = Normalizer()

model_name = "HooshvareLab/bert-base-parsbert-uncased"


# model = TFBertModel.from_pretrained(model_name)

#loading parsbert pre-trained model and tokenizer
config = AutoConfig.from_pretrained(model_name)
bert_tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

# import nltk.data
# nltk_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')


# bert_tokenizer = BertTokenizer.from_pretrained(model_name)

def tokenize_text(text):
    text = normalizer.normalize(text)
    sentences = sent_tokenize(text)
    res = []
    sub_res = [bert_tokenizer.cls_token_id]
    for s in sentences:

        ids = bert_tokenizer(s, add_special_tokens = False, truncation = True, return_attention_mask = False,  return_token_type_ids=False)['input_ids']
        if len(ids)>500:
            ids= ids[0:498]

        ids.append(bert_tokenizer.sep_token_id )

        if len(sub_res) + len(ids)>500:
            res.append(sub_res)
            sub_res = [bert_tokenizer.cls_token_id] + ids
        else:
            sub_res = sub_res + ids

    res.append(sub_res)
    return res

def text_to_bert(text):
    encoded_inputs = tokenize_text(text)
    results = []

    for i in encoded_inputs:
        i_tensor = torch.Tensor( np.array([i]) ).to(torch.int64)
        output = model(input_ids = i_tensor )
        results.append(output[0][0][0])

    if len(results) == 1 :
        return results[0]
    else:
        return tf.keras.layers.Average()(results)


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


def apply(folder_name, Country):

    AISimilarityDoc.objects.filter(document_id1__country_id=Country).delete()
    document_list = Document.objects.filter(country_id=Country)

    bach_size = 1000
    bert_res = {}
    for d in document_list:
        paragraph_list = DocumentParagraphs.objects.filter(document_id=d)
        text = ""
        for p in paragraph_list:
            text += LocalPreprocessing(p.text)
        vec = text_to_bert(text)
        bert_res[d.id] = tf.convert_to_tensor(vec.detach().numpy())

    doc_li = [i.id for i in document_list ]
    create_list = []
    for docID1 in bert_res:
        doc_li.remove(docID1)
        for docID2 in doc_li:
            v1 = bert_res[docID1]
            v2 = bert_res[docID2]
            cosine_sim = 1 - spatial.distance.cosine(v1, v2)
            sim_obj = AISimilarityDoc(document_id1_id=docID1, document_id2_id=docID2, sim=round(cosine_sim*100,2) )
            create_list.append(sim_obj)

            if bach_size < len(create_list):
                AISimilarityDoc.objects.bulk_create(create_list)
                create_list = []

    AISimilarityDoc.objects.bulk_create(create_list)


    # AISimilarityDoc.objects.filter(document_id__country_id=Country).delete()
    # document_list = Document.objects.filter(country_id=Country)
    # paragraph_list = DocumentParagraphs.objects.filter(document_id__in=document_list)

    # bert_res = {}
    # print(len(paragraph_list))
    # for p in paragraph_list:
    #     text = LocalPreprocessing(p.text)
    #     id = p.id
    #     vec = text_to_bert(text)
    #     # bert_res[id] = {"vec":vec, 'doc_id':p.document_id}
    #     print(len(bert_res))
    # print("sucsses to bert")
    #
    # doc_li = [i.id for i in document_list ]
    # create_list = []
    # for pId1 in bert_res:
    #     doc_id1 = bert_res[pId1]['doc_id']
    #     if doc_id1 in doc_li:
    #         doc_li.remove(doc_id1)
    #     for pId2 in bert_res:
    #         doc_id2 = bert_res[pId2]['doc_id']
    #         if doc_id2 not in doc_li:
    #             v1 = bert_res[pId1]
    #             v2 = bert_res[pId2]
    #             cosine_sim = 1 - spatial.distance.cosine(v1, v2)
    #             sim_obj = AISimilarityParagraph(paragraph_id1=pId1, paragraph_id2=pId2, sim=round(cosine_sim*100,2) )
    #             create_list.append(sim_obj)
    #
    #         if bach_size < len(create_list):
    #             AISimilarityParagraph.objects.bulk_create(create_list)
    #             create_list = []
    #
    # AISimilarityParagraph.objects.bulk_create(create_list)













    #
    # slogan_list = Slogan.objects.all()
    # create_list =[]
    # for year in range(1375, 1401, 1):
    #     document_list = Document.objects.filter(country_id=Country, approval_date__startswith=str(year))
    #     paragraph_list = DocumentParagraphs.objects.filter(document_id__in=document_list)
    #     slogan_list_keywords = {}
    #     number_keyword = {}
    #     for slogan in slogan_list:
    #         number_keyword[slogan.year] = 0
    #         slogan_list_keywords[slogan.year] = slogan.keywords.split("-")
    #     for paragraph in paragraph_list:
    #         for year_s in slogan_list_keywords:
    #             num = 0
    #             for word in slogan_list_keywords[year_s]:
    #                 isin = paragraph.text.find(word)
    #                 if isin>0:
    #                     num += isin
    #             number_keyword[year_s] += num
    #
    #     for i in number_keyword:
    #         if len(document_list) != 0:
    #             meanOfRepeat= round(number_keyword[i]/len(document_list),2)
    #         else:
    #             meanOfRepeat=0
    #         slogan_obj = SloganAnalysis(docYear=year, sloganYear=i, number=meanOfRepeat, country_id=Country)
    #         create_list.append(slogan_obj)
    #         # print(f'ASNAD:{year}: slogan:{i} => {meanOfRepeat}')
    #
    # SloganAnalysis.objects.bulk_create(create_list)

