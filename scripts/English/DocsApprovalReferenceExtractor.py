from en_doc.models import Document, Level, ApprovalReference, DocumentParagraphs


def apply(folder_name, Country):
    all_docs = Document.objects.filter(country_id=Country)

    all_docs.update(approval_reference_id=None)

    #--------------------- act's approval reference ---------------------#
    levels = Level.objects.filter(name__in=['Public General Acts','Local Acts'])
    approval_reference = ApprovalReference.objects.get(name="UK Parliament")
    all_docs.filter(level_id__in=levels).update(approval_reference_id=approval_reference)

    # --------------------- SI's approval reference ---------------------#
    levels = Level.objects.filter(name__in=['Order', 'Regulations','Rules','Scheme','Direction','Declaration'])
    stop_words_for_the = [
        'makes',
        'make',
        'has before making',
        'has decided to',
        'is satisfied',
        'acting jointly, in exercise',
        '(',
        ',',
        'has consulted',
        'in exercise',
        'has published',
        'have made',
        'in accordance',
        'has carried out',
        'has determined to',


        # ', in exercise of',
        # ', with the consent of',
        # ', acting as',


        "’s most excellent majesty in council",
        "'s most excellent majesty in council",
    ]
    filtered_doc = all_docs.filter(level_id__in=levels)
    for index_, doc in enumerate(filtered_doc):
        paragraphs = DocumentParagraphs.objects.filter(document_id=doc)
        for index,para in enumerate(paragraphs):
            para_text = para.text.lower()
            para_text = para_text.replace(doc.name.lower(), "").strip()

            para_text = extra_pre_words(para_text)

            if para_text.startswith("the "):
                # print("-------found The-------")
                # print(para.text)
                para_len = len(para_text)
                indices = []
                for word in stop_words_for_the:
                    i = para_text.find(word)
                    indices.append(i if i>-1 else para_len)
                min_ = min(indices)
                if min_ != para_len:
                    approval_reference_name = para_text.split(stop_words_for_the[indices.index(min_)])[0].strip().capitalize()
                    result_count = ApprovalReference.objects.filter(name__iexact=approval_reference_name).count()
                    if result_count != 0:
                        approval_reference = ApprovalReference.objects.get(name__iexact=approval_reference_name)
                        doc.approval_reference_id = approval_reference
                        doc.save()
                        break

def extra_pre_words(text:str):
    extras = ['accordingly','these regulations are made by','the scheme has been','regulations made by']
    for extra in extras:
        text = text.replace(extra,"")
        if extra == "these regulations are made by":
            text = text.replace("."," has consulted")
    return text.strip()