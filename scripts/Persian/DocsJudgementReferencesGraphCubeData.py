
from doc.models import *
from django.db.models import Count, Max, Q


def apply(folder_name, Country):
    JudgmentReferencesGraphCube.objects.filter(country_id=Country).delete()
    judgement_doc_list = Judgment.objects.all().values_list("document_id")
    edges_list = Graph.objects.filter(Q(src_document_id__country_id=Country) | Q(dest_document_id__country_id=Country))

    print(edges_list)

    nodes_list = []
    added_node = []
    edges_list = []
    added_edge = []

    i = 1
    for edge in edges_list:
        print(i, edges_list.count())
        i+=1

        src_id = str(edge.src_document_id_id)
        src_name = edge.src_document_id.name
        src_color = "Green" if src_id in judgement_doc_list else "Blue"

        src_node = {"id": src_id, "name": src_name, "style": {"fill": src_color}}

        dest_id = str(edge.dest_document_id_id)
        dest_name = edge.dest_document_id.name
        dest_color = "Green" if dest_id in judgement_doc_list else "Blue"

        dest_node = {"id": dest_id, "name": dest_name, "style": {"fill": dest_color}}

        weight = edge.weight

        if src_id not in added_node:
            nodes_list.append(src_node)
            added_node.append(src_id)

        if dest_id not in added_node:
            nodes_list.append(dest_node)
            added_node.append(dest_id)

        edge_obj = {"source": src_id, "source_name": src_name,
                    "target": dest_id, "target_name": dest_name,
                    "weight": weight}

        if [dest_id, src_id] not in added_edge:
            edges_list.append(edge_obj)
            added_edge.append([src_id, dest_id])

    JudgmentReferencesGraphCube.objects.create(country_id=Country, nodes=nodes_list, edges=edges_list)
