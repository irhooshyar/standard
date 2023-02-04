from doc.models import Document, Graph
from django.db.models import Count

def apply(Country):
    documents = Document.objects.filter(country_id=Country)
    annotate_reference_count = Graph.objects.filter(dest_document_id__country_id=Country, measure_id_id=2).filter(src_document_id__type_id__name='نظر مشورتی').values('dest_document_id_id').annotate(count=Count('dest_document_id_id')).values_list('dest_document_id_id', 'count')
    advisory_opinion_count_dict = {}
    for reference_count in annotate_reference_count:
        advisory_opinion_count_dict[reference_count[0]] = reference_count[1]

    for document in documents:
        if document.id in advisory_opinion_count_dict:
            document.advisory_opinion_count = advisory_opinion_count_dict[document.id]
        else:
            document.advisory_opinion_count = 0
    documents.bulk_update(documents, ['advisory_opinion_count'])
    
    