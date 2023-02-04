from doc.models import Document, Graph


def apply(Country):
    documents = Document.objects.filter(country_id=Country)
    for doc in documents:
        ir_count = Graph.objects.filter(dest_document_id_id=doc.id, measure_id_id=2).filter(src_document_id__type_id__name='استفساریه').count()
        doc.interpretation_rules_count = ir_count
        doc.save()
