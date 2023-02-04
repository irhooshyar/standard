from doc.models import DocumentWords
from scripts.Persian.Preprocessing import Preprocessing


class searchClass():

    def __init__(self, Country):
        self.Country = Country
        self.cache = {}

    def searchText(self, text):
        words = Preprocessing(text, stem=False)
        word2doc = {}
        query_words = []
        for word in words:
            if word in self.cache:
                word2doc[word] = self.cache[word]
            else:
                word2doc[word] = set({})
                query_words.append(word)
        query_res = DocumentWords.objects.filter(country_id=self.Country, word__in=query_words, place= 'متن')
        for row in query_res:
            doc_id = row.document_id_id
            word2doc[row.word].add(doc_id)

        res = list(word2doc.values())[0]
        for word in word2doc:
            if word not in self.cache:
                self.cache[word] = word2doc[word]
            res = res & word2doc[word]

        return res

    def searchWords(self, words):
        word2doc = {}
        query_words = []
        for word in words:
            if word in self.cache:
                word2doc[word] = self.cache[word]
            else:
                word2doc[word] = set({})
                query_words.append(word)

        if len(query_words) > 0:
            query_res = DocumentWords.objects.filter(country_id=self.Country, word__in=query_words, place= 'متن')

            for row in query_res:
                doc_id = row.document_id_id
                word2doc[row.word].add(doc_id)

        if len(word2doc) == 0: return set({})
        res = list(word2doc.values())[0]
        for word in word2doc:
            if word not in self.cache:
                self.cache[word] = word2doc[word]
            res = res & word2doc[word]

        return res

    def loadCache(self, wordList):

        word2doc = {}
        query_words = []
        for word in set(wordList):
            if word in self.cache:
                word2doc[word] = self.cache[word]
            else:
                word2doc[word] = set({})
                query_words.append(word)
        print(self.Country)
        query_res = DocumentWords.objects.filter(country_id=self.Country, word__in=query_words, place= 'متن')

        for row in query_res:
            doc_id = row.document_id_id
            word2doc[row.word].add(doc_id)

        for word in word2doc:
            if word not in self.cache:
                self.cache[word] = word2doc[word]