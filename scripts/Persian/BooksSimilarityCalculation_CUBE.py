from doc.models import DocumentSimilarity, SimilarityType, DocumentSimilarityCube, DocumentSimilarity_Distribution_Cube
from django.db.models import Count, Max, Min
import math

def apply(folder, Country):

    DocumentSimilarityCube.objects.filter(country_id=Country).delete()
    DocumentSimilarity_Distribution_Cube.objects.filter(country_id=Country).delete()

    indices_dict = {
        "book_bm25_index": "BM25",
        "book_dfr_index": "DFR",
        "book_dfi_index": "DFI",
    }

    for index, measure in indices_dict.items():
        calculate_cube(Country, measure)


def calculate_threshold_list(min_weight, max_weight):
    min_weight = int(math.floor(min_weight / 10.0)) * 10
    max_weight = int(math.ceil(max_weight / 10.0)) * 10

    step = (max_weight - min_weight) / 10
    threshold_list = []
    for i in range(10):
        threshold_list.append(int(min_weight + i * step))

    return threshold_list

def calculate_cube(Country, sim_measure):
    similarity_type = SimilarityType.objects.get(name=sim_measure)

    graph_list = DocumentSimilarity.objects.filter(doc1__country_id_id=Country, similarity_type=similarity_type)

    min_weight = graph_list.aggregate(Min('similarity'))["similarity__min"]
    max_weight = graph_list.aggregate(Max('similarity'))["similarity__max"]

    threshold_list = calculate_threshold_list(min_weight, max_weight)

    nodes_dictionary = {}
    edges_dictionary = {}

    added_nodes_dictionary = {}
    added_edges_dictionary = {}

    for threshold in threshold_list:
        nodes_dictionary[threshold] = []
        edges_dictionary[threshold] = []
        added_nodes_dictionary[threshold] = []
        added_edges_dictionary[threshold] = []

    i = 1
    for edge in graph_list:
        print(i / graph_list.count())
        i += 1

        src_id = str(edge.doc1.id)
        src_name = edge.doc1.name
        src_color = str(edge.doc1.type_id.color) if edge.doc1.type_id is not None else "#000000"
        dest_id = str(edge.doc2.id)
        dest_name = edge.doc2.name
        dest_color = str(edge.doc2.type_id.color) if edge.doc2.type_id is not None else "#000000"
        weight = edge.similarity

        for threshold in threshold_list:
            if weight >= threshold and weight > 0:

                if src_id not in added_nodes_dictionary[threshold]:
                    node1 = {"id": src_id, "name": src_name, "style": {"fill": src_color}}
                    nodes_dictionary[threshold].append(node1)
                    added_nodes_dictionary[threshold].append(src_id)

                if dest_id not in added_nodes_dictionary[threshold]:
                    node2 = {"id": dest_id, "name": dest_name, "style": {"fill": dest_color}}
                    nodes_dictionary[threshold].append(node2)
                    added_nodes_dictionary[threshold].append(dest_id)

                if dest_id + src_id not in added_edges_dictionary[threshold]:
                    edge_size = 5
                    if max_weight > min_weight:
                        norm_sim = (weight - min_weight) / (max_weight - min_weight)
                        edge_size = 1 + norm_sim * 4

                    edge_obj = {"source": src_id, "source_name": src_name,
                                "target": dest_id, "target_name": dest_name,
                                "weight": weight, 'size': edge_size}

                    edges_dictionary[threshold].append(edge_obj)

                    added_edges_dictionary[threshold].append(src_id+dest_id)

    for threshold in threshold_list:
        DocumentSimilarityCube.objects.create(country_id=Country, similarity_type=similarity_type, threshold=threshold,
                                  edge_count=edges_dictionary[threshold].__len__(),
                                  nodes_data=nodes_dictionary[threshold], edges_data=edges_dictionary[threshold])

    Graph_Cube_Data = DocumentSimilarityCube.objects.filter(country_id=Country, similarity_type=similarity_type)
    for row in Graph_Cube_Data:
        DocumentSimilarity_Distribution_Cube.objects.create(country_id=Country, similarity_type=row.similarity_type, threshold=row.threshold,
                                               edge_count=row.edge_count)

