from doc.models import *
import time

def apply(folder_name, Country):

    t = time.time()

    SubjectAreaGraphCube.objects.filter(country_id=Country).delete()

    color_list = ["#E52B50", "#9966CC", "#0000FF", "#993300", "#960018", "#6F4E37", "#008001",
                  "#4B0082", "#808000", "#C71585", "#FF2400", "#708090","#483C32", "#FFFF00",
                  "#00FFFF", "#DE5D83", "#702963", "#D2B48C", "#3FFF00", "#FBCEB1"]

    subject_area_list = SubjectArea.objects.all()

    for area in subject_area_list:
        subject_sub_area_list = SubjectSubArea.objects.filter(subject_area_id=area)
        i = 0
        for sub_area in subject_sub_area_list:
            if sub_area.color is None or sub_area.color == "":
                SubjectSubArea.objects.filter(id=sub_area.id).update(color=color_list[i])
                i += 1
                if i == color_list.__len__():
                    i = 0

    measure = Measure.objects.get(english_name="ReferenceSimilarity")
    for subject_area in subject_area_list:
        document_list = Document.objects.filter(subject_area_id=subject_area)
        graph_list = Graph.objects.filter(src_document_id__in=document_list, dest_document_id__in=document_list, measure_id=measure)

        Node_list = []
        Edges_list = []
        Added_node = []

        for edge in graph_list:

            src_id = str(edge.src_document_id_id)
            src_name = edge.src_document_id.name
            src_color = edge.src_document_id.subject_sub_area_id.color
            src_sub_area_id = edge.src_document_id.subject_sub_area_id.id if edge.src_document_id.subject_sub_area_id is not None else -1

            dest_id = str(edge.dest_document_id_id)
            dest_name = edge.dest_document_id.name
            dest_color = edge.dest_document_id.subject_sub_area_id.color
            dest_subject_id = edge.dest_document_id.subject_sub_area_id.id if edge.dest_document_id.subject_sub_area_id is not None else -1

            weight = edge.weight

            if src_id not in Added_node:
                node1 = {"id": src_id, "name": src_name, "sub_area": src_sub_area_id, "style": {"fill": src_color}}
                Node_list.append(node1)
                Added_node.append(src_id)

            if dest_id not in Added_node:
                node2 = {"id": dest_id, "name": dest_name, "sub_area": dest_subject_id, "style": {"fill": dest_color}}
                Node_list.append(node2)
                Added_node.append(dest_id)

            edge_obj = {"source": src_id, "source_name": src_name,
                        "target": dest_id, "target_name": dest_name,
                        "weight": weight}

            Edges_list.append(edge_obj)

        SubjectAreaGraphCube.objects.create(country_id=Country, subject_area_id=subject_area, edges=Edges_list, nodes=Node_list)

    print("time ", time.time() - t)


