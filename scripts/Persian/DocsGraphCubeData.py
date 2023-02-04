
from doc.models import *
from django.db.models import Count, Max


def Calculate_distributions(max_weight):
    step = []
    for i in range(1, 11):
        if max_weight <= 5:
            if i <= max_weight:
                step.append(i)
        else:
            if i < max_weight and i <= 5:
                step.append(i)
            if max_weight - 5 <= 5 and i > 5:
                if step[-1] >= max_weight:
                    break
                step.append(i)
            if max_weight - 5 > 5 and i > 5:
                temp = round((max_weight - 5) / 5)
                new_step = step[-1] + temp
                if new_step > max_weight:
                    break
                step.append(new_step)
    return step

def apply(folder_name, Country, host_url):
    Graph_Cube.objects.filter(country_id=Country).delete()
    Graph_Distribution_Cube.objects.filter(country_id=Country).delete()

    measure = Measure.objects.get(english_name="ReferenceSimilarity")
    graph_list = Graph.objects.filter(src_document_id__country_id=Country, measure_id=measure)

    max_weight = graph_list.aggregate(Max('weight'))["weight__max"]

    threshold_list = [1,2,5,10,15,20,40,60,80,100]

    nodes_dictionary = {}
    edges_dictionary = {}

    added_nodes_dictionary = {}

    for threshold in threshold_list:
        nodes_dictionary[threshold] = []
        edges_dictionary[threshold] = []
        added_nodes_dictionary[threshold] = []

    i = 1
    for edge in graph_list:
        print(i/graph_list.count())
        i+=1

        src_id = str(edge.src_document_id_id)
        src_name = edge.src_document_id.name
        src_color = str(edge.src_document_id.type_id.color) if edge.src_document_id.type_id is not None else "#000000"

        src_type_id = edge.src_document_id.type_id.id if edge.src_document_id.type_id is not None else -1
        src_subject_id = edge.src_document_id.subject_id.id if edge.src_document_id.subject_id is not None else -1
        src_type_subject = str(src_type_id) + "_" + str(src_subject_id)

        dest_id = str(edge.dest_document_id_id)
        dest_name = edge.dest_document_id.name
        dest_color = str(edge.dest_document_id.type_id.color) if edge.dest_document_id.type_id is not None else "#000000"

        dest_type_id = edge.dest_document_id.type_id.id if edge.dest_document_id.type_id is not None else -1
        dest_subject_id = edge.dest_document_id.subject_id.id if edge.dest_document_id.subject_id is not None else -1
        dest_type_subject = str(dest_type_id) + "_" + str(dest_subject_id)

        weight = edge.weight

        for threshold in threshold_list:
            if weight >= threshold:
                if src_id not in added_nodes_dictionary[threshold]:
                    node1 = {"id": src_id, "name": src_name, "ts": src_type_subject, "style": {"fill": src_color}}
                    nodes_dictionary[threshold].append(node1)
                    added_nodes_dictionary[threshold].append(src_id)

                if dest_id not in added_nodes_dictionary[threshold]:
                    node2 = {"id": dest_id, "name": dest_name, "ts": dest_type_subject, "style": {"fill": dest_color}}
                    nodes_dictionary[threshold].append(node2)
                    added_nodes_dictionary[threshold].append(dest_id)

                edge_obj = {"source": src_id, "source_name": src_name,
                            "target": dest_id, "target_name": dest_name,
                            "weight": weight}

                edges_dictionary[threshold].append(edge_obj)

    for threshold in threshold_list:
        Graph_Cube.objects.create(country_id=Country, measure_id=measure, threshold=threshold,
                                  edge_count=edges_dictionary[threshold].__len__(),
                                  nodes_data=nodes_dictionary[threshold], edges_data=edges_dictionary[threshold])

    Graph_Cube_Data = Graph_Cube.objects.filter(country_id=Country)
    for row in Graph_Cube_Data:
        Graph_Distribution_Cube.objects.create(country_id=Country, measure_id=row.measure_id, threshold=row.threshold, edge_count=row.edge_count)

