from html import entities
from en_doc.models import Country
import spacy
from en_doc.models import Document, DocumentParagraphs, AINamedEntities

nlp = spacy.load("en_core_web_sm")

def apply(folder_name, Country):
    AINamedEntities.objects.filter(paragraph_id__document_id__country_id=Country).delete()
    paragraphs = DocumentParagraphs.objects.filter(document_id__country_id = Country)


    Create_List = []
    batch_size = 5

    for each in paragraphs:
        ents_map = {}
        doc = nlp(each.text)
        for ent in doc.ents:
            ents_map[ent.text] = ent.label_
        if ents_map:
            obj = AINamedEntities(document_id = each.document_id, paragraph_id = each, entities = ents_map)
            Create_List.append(obj)
        if Create_List.__len__() > batch_size:
            AINamedEntities.objects.bulk_create(Create_List)
            Create_List = []
    AINamedEntities.objects.bulk_create(Create_List)
        
