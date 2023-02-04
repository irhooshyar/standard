from en_doc.models import Document, ApprovalReference, DocumentParagraphs


def apply(folder_name, Country):
    all_docs = Document.objects.filter(country_id=Country)

    mosco = 'Москва'
    for doc in all_docs:
        document_paragraphs = DocumentParagraphs.objects.filter(document_id_id=doc.id, text__icontains=mosco).order_by('-number')[0]
        date_paragraph_index = document_paragraphs.number + 1

        Reference_index = document_paragraphs.text.find(mosco)
        start_index = Reference_index + len(mosco) + 1
        Reference = document_paragraphs.text[start_index:-1]


        ApprovalReference_key = ApprovalReference.objects.create(name=Reference)
        Document.objects.filter(id = doc.id).update(approval_reference_id=ApprovalReference_key)

        Date_text = DocumentParagraphs.objects.get(document_id_id=doc.id, number=date_paragraph_index).text
        Document.objects.filter(id = doc.id).update(approval_date=Date_text)



