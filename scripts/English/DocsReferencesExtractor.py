from scripts.English import Preprocessing
from en_doc.models import Document, DocumentParagraphs, ReferencesParagraphs, Graph, Measure
from scripts.parallel import Parallel
from tools.en_search import searchClass
import numpy as np

class DocsReferencesExtractor(Parallel):
    result_key = ['Create_List_Ref_Paragraph', 'Create_List_Graph']
    documents_text_cache = {}
    searchClass = None

    def clearModel(self, Country):
        ReferencesParagraphs.objects.filter(document_id__country_id=Country).delete()
        Graph.objects.filter(src_document_id__country_id=Country).delete()

    def start(self, folderName, Country, **arg):
        document_list = Document.objects.filter(country_id=Country).values('id','name')
        documents_name = {}
        for doc in document_list:
            doc_name_words = Preprocessing.Preprocessing(doc['name'], stem=False)
            documents_name[doc['id'], doc['name']] = doc_name_words
        word_list = np.concatenate(list(documents_name.values()), axis=None)
        self.searchClass = searchClass(Country)
        self.searchClass.loadCache(word_list)
        measure = Measure.objects.get(english_name="ReferenceSimilarity")
        self.argument = {'measure': measure}
        return documents_name

    def parallelPhase(self, li, threadNumber, measure):
        for (doc_id, doc_name), doc_name_words in li.items():
            self.statusProgress.progress()
            doc_ids = self.searchClass.searchWords(doc_name_words)
            print(doc_ids)
            for target_doc_id in doc_ids:
                if doc_id != target_doc_id:
                    ref_count = 0
                    target_doc_text = self.getDocumentParagraph(target_doc_id)
                    for paragraph_id, paragraph_text in target_doc_text.items():
                        if doc_name in paragraph_text:
                            references_count = paragraph_text.count(doc_name)
                            ref_count += references_count
                            ref_paragraph_obj = ReferencesParagraphs(document_id_id=doc_id, paragraph_id_id=paragraph_id)
                            self.addResult('Create_List_Ref_Paragraph', ref_paragraph_obj, threadNumber)

                    if ref_count > 0:
                        doc_ref_obj = Graph(src_document_id_id=target_doc_id, dest_document_id_id=doc_id, measure_id=measure, weight=ref_count)
                        self.addResult('Create_List_Graph', doc_ref_obj, threadNumber)

    def getDocumentParagraph(self, doc_id):
        if doc_id not in self.documents_text_cache:
            document_paragraph_list = DocumentParagraphs.objects.filter(document_id_id=doc_id).values("document_id","text", "id")
            document_text = {}
            for paragraph in document_paragraph_list:
                paragraph_id = paragraph["id"]
                document_text[paragraph_id] = paragraph["text"]
            self.documents_text_cache[doc_id] = document_text

        return self.documents_text_cache[doc_id]

    def end(self, res, **arg):
        self.bulk_create_array(ReferencesParagraphs, res['Create_List_Ref_Paragraph'])
        self.bulk_create_array(Graph, res['Create_List_Graph'])
