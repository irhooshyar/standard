from pathlib import Path
from nltk.util import ngrams
from collections import Counter

from abdal import config
from scripts.Russia import Preprocessing
from en_doc.models import DocumentNgram,Document

def ngram(corpus, n):
    res = {}
    for id in corpus:
        content = corpus[id]
        try:
            ngram = list(ngrams(content, n))
            #         count
            ngram = Counter(ngram)
            #     sort
            ngram = sorted(ngram.items(), key=lambda x: x[1], reverse=True)
            #         change format
            res[id] = ngram
        except:
            continue
    return res


def apply(folder_name, n, Country):
    dataPath = str(Path(config.DATA_PATH, folder_name))
    resultPath = str(Path(config.RESULT_PATH, folder_name))
    input_data = Preprocessing.readFiles(dataPath, preprocessArg={"stem": False})
    dd = ngram(input_data, n)
    for id in dd:
        content = dd[id]
        document = Document.objects.get(name=id,country_id=Country)
        f = open(Path(resultPath, "Ngram", f"{n}gram", f"{id}.txt"), "w", encoding="utf8")
        cntr = 1
        for i in content:
            line = ""
            for x in range(n):
                line = line + f"{i[0][x]} "
            text = line[:-1]
            line = f"{text}\t{i[1]}\n"
            f.write(line)
            # windows-1251
            # text = text.encode('KOI8-R')
            # print(text)
            DocumentNgram.objects.create(text=text, gram=n, count=i[1], document_id=document)

            if cntr % 20 == 0:
                break

            cntr += 1

        f.close()
