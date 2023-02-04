
from doc.models import Rahbari, RahbariGraph, RahbariGraphType, RahbariLabel
import numpy as np
import after_response

label_node_color = "#009999"
document_node_color = "#00CC66"

@after_response.enable
def apply():
    # CoLabelsGraph()
    # DocumentLabelGraph()
    DocumentDocumentGraph()
    print("Done...")


def CoLabelsGraph():
    graph_name = "گراف باهم‌آیی برچسب‌ها"
    graph_en_name = "CoLabelsGraph"
    RahbariGraph.objects.filter(type__en_name=graph_en_name).delete()
    RahbariGraphType.objects.filter(en_name=graph_en_name).delete()

    graph_type = RahbariGraphType.objects.create(name=graph_name, en_name=graph_en_name)

    rahbari_document_list = Rahbari.objects.all()
    labels_dict = {}
    b = 0
    for doc in rahbari_document_list:
        print("1.1.", b/rahbari_document_list.__len__())
        doc_labels = doc.labels.split("؛ ")
        for label in doc_labels:
            if len(label.replace(" ", "")) > 0:
                label = label.replace('؛', '').replace("ائمه جمعه", "ائمه‌ جمعه").replace("ورزش‌کاران", "ورزشکاران")
                try:
                    label_object = RahbariLabel.objects.get(name=label)
                    label_name = label_object.name
                    label_id = label_object.id
                    label = str(label_id) + "_" + label_name
                    if label not in labels_dict:
                        labels_dict[label] = [doc.id]
                    else:
                        labels_dict[label].append(doc.id)
                except:
                    print(label)
        b+=1


    labels_list = list(labels_dict.keys())

    added_node = []
    nodes_data = []
    added_edge = []
    edges_data = []
    max_weight = 0
    for i in range(labels_list.__len__()):
        print("1.2.", i/labels_list.__len__())
        label1 = labels_list[i]
        label1_id, label1_name = label1.split("_")[0], label1.split("_")[1]
        label1_doc_list = labels_dict[label1]
        for j in range(i+1, labels_list.__len__()):
            label2 = labels_list[j]
            label2_id, label2_name = label2.split("_")[0], label2.split("_")[1]
            label2_doc_list = labels_dict[label2]

            common_doc = list(set(label1_doc_list) & set(label2_doc_list))

            if common_doc.__len__() > 0:
                node1 = {"id": "label_" + label1_id, "name": label1_name, "node_type": "label",  "style": {"fill": label_node_color}}
                node2 = {"id": "label_" + label2_id, "name": label2_name, "node_type": "label", "style": {"fill": label_node_color}}
                weight = common_doc.__len__()
                edge_id = str(label1_id) + "_" + str(label2_id)
                edge = {"id": edge_id, "source": "label_" + label1_id, "source_name": label1_name, "source_type": "label",
                        "target": "label_" + label2_id, "target_name": label2_name, "target_type": "label", "weight": weight}

                if label1_id not in added_node:
                    added_node.append(label1_id)
                    nodes_data.append(node1)

                if label2_id not in added_node:
                    added_node.append(label2_id)
                    nodes_data.append(node2)


                if [label1_id, label2_id] not in added_edge and  [label2_id, label1_id] not in added_edge:
                    added_edge.append([label1_id, label2_id])
                    edges_data.append(edge)


                if weight >= max_weight:
                    max_weight = weight

    RahbariGraph.objects.create(type=graph_type, nodes_data=nodes_data, edges_data=edges_data)

    i = 1
    weight_list = []
    while i < max_weight:
        weight_list.append(str(i))

        if i < 5:
            i += 1
        else:
            i += 10


    histogram_list = []
    for w in weight_list:
        weight = int(w)
        histogram_count = list(filter(lambda x: x["weight"] >= weight, edges_data)).__len__()
        histogram_list.append({"key": w, "count": histogram_count})

    graph_type.max_weight = max_weight
    graph_type.weight_list = ",".join(weight_list)
    graph_type.save()
    graph_type.histogram_data = histogram_list
    graph_type.save()
    graph_type.histogram_title = "توزیع باهم‌آیی برچسب‌ها براساس اسناد مشترک"
    graph_type.save()
    graph_type.is_label = 1
    graph_type.save()


def DocumentLabelGraph():
    graph_name = "گراف میان سند و برچسب"
    graph_en_name = "DocumentLabelGraph"
    RahbariGraph.objects.filter(type__en_name=graph_en_name).delete()
    RahbariGraphType.objects.filter(en_name=graph_en_name).delete()

    graph_type = RahbariGraphType.objects.create(name=graph_name, en_name=graph_en_name)

    rahbari_document_list = Rahbari.objects.all()

    added_node = []
    nodes_data = []
    added_edge = []
    edges_data = []
    b = 0
    for doc in rahbari_document_list:
        print("2.", b/rahbari_document_list.__len__())
        document_name = doc.document_name
        document_id = str(doc.document_id.id)
        document_shape = "rect"

        node1 = {"id": "document_" + document_id, "name": document_name, "node_type": "document", "type": document_shape, "size": 20,
                 "style": {"fill": document_node_color}}
        nodes_data.append(node1)

        doc_labels = doc.labels.split("؛ ")
        for label in doc_labels:
            if len(label.replace(" ", "")) > 0:
                label = label.replace('؛', '').replace("ائمه جمعه", "ائمه‌ جمعه").replace("ورزش‌کاران", "ورزشکاران")
                try:
                    label_object = RahbariLabel.objects.get(name=label)
                    label_name = label_object.name
                    label_id = str(label_object.id)

                    node2 = {"id": "label_" + label_id, "name": label_name, "node_type": "label", "style": {"fill": label_node_color}}

                    if label_id not in added_node:
                        added_node.append(label_id)
                        nodes_data.append(node2)

                    weight = 1
                    edge_id = str(document_id) + "_" + str(label_id)
                    edge = {"id": edge_id, "source": "document_" + document_id, "source_name": document_name, "source_type": "document",
                            "target": "label_" + label_id, "target_name": label_name, "target_type": "label", "weight": weight}

                    if [document_id, label_id] not in added_edge and [label_id, document_id] not in added_edge:
                        added_edge.append([document_id, label_id])
                        edges_data.append(edge)

                except:
                    print(label)
        b += 1

    RahbariGraph.objects.create(type=graph_type, nodes_data=nodes_data, edges_data=edges_data)

    graph_type.max_weight = 1
    graph_type.weight_list = "1"
    graph_type.save()
    graph_type.histogram_data = [{"key": 1, "count": edges_data.__len__()}]
    graph_type.save()
    graph_type.histogram_title = "توزیع میان اسناد و برچسب‌ها"
    graph_type.save()
    graph_type.is_label = 1
    graph_type.save()
    graph_type.is_document = 1
    graph_type.save()


def DocumentDocumentGraph():
    graph_name = "گراف برچسب‌های میان اسناد"
    graph_en_name = "DocumentDocumentGraph"
    RahbariGraph.objects.filter(type__en_name=graph_en_name).delete()
    RahbariGraphType.objects.filter(en_name=graph_en_name).delete()

    graph_type = RahbariGraphType.objects.create(name=graph_name, en_name=graph_en_name)


    rahbari_labels = RahbariLabel.objects.all()
    rahbari_labels_name_dict = {}
    rahbari_labels_id_dict = {}

    for row in rahbari_labels:
        rahbari_labels_name_dict[row.name] = str(row.id)
        rahbari_labels_id_dict[str(row.id)] = row.name

    rahbari_document_list = Rahbari.objects.all()
    rahbari_document_labels = {}
    rahbari_document_names = {}
    for i in range(rahbari_document_list.__len__()):
        print("3.1", i/rahbari_document_list.__len__())
        document_id = str(rahbari_document_list[i].document_id.id)
        document_name = str(rahbari_document_list[i].document_id.name)
        rahbari_document_names[document_id] = document_name
        doc1_labels = rahbari_document_list[i].labels.split("؛ ")
        doc1_labels_ids = []
        for lbl in doc1_labels:
            try:
                lbl = lbl.replace('؛', '').replace("ائمه جمعه", "ائمه‌ جمعه").replace("ورزش‌کاران", "ورزشکاران")
                lbl_id = rahbari_labels_name_dict[lbl]
                doc1_labels_ids.append(lbl_id)
            except Exception as e:
                pass

        rahbari_document_labels[document_id] = doc1_labels_ids


    nodes_data = []
    added_edge = []
    edges_data = []
    max_weight = 0


    doc_id_list = list(rahbari_document_labels.keys())

    for i in range(doc_id_list.__len__()):
        print("3.2", i / doc_id_list.__len__())
        document1_id = doc_id_list[i]
        document1_name = rahbari_document_names[document1_id]
        document1_labels = rahbari_document_labels[document1_id]
        document1_shape = "rect"
        node1 = {"id": "document_" + document1_id, "name": document1_name, "node_type": "document", "type": document1_shape, "size": 20,
                 "style": {"fill": document_node_color}}
        nodes_data.append(node1)

        for j in range(i+1, doc_id_list.__len__()):
            document2_id = doc_id_list[j]
            document2_name = rahbari_document_names[document2_id]
            document2_labels = rahbari_document_labels[document2_id]

            common_labels = list(set(document1_labels) & set(document2_labels))

            weight = common_labels.__len__()

            if weight > 0:
                edge_id = str(document1_id) + "_" + str(document2_id)
                edge = {"id": edge_id, "source": "document_" + document1_id, "source_name": document1_name, "source_type": "document",
                        "target": "document_" + document2_id, "target_name": document2_name, "target_type": "document",
                        "weight": weight}

                if [document1_id, document2_id] not in added_edge and [document2_id, document1_id] not in added_edge:
                    added_edge.append([document1_id, document2_id])
                    edges_data.append(edge)

                if weight >= max_weight:
                    max_weight = weight

    RahbariGraph.objects.create(type=graph_type, nodes_data=nodes_data, edges_data=edges_data)

    step = 2
    weight_list = []
    histogram_list = []
    for i in range(1, max_weight, step):
        inc = i
        weight_list.append(str(inc))
        histogram_count = list(filter(lambda x: x["weight"] >= inc, edges_data)).__len__()
        histogram_list.append({"key": inc, "count": histogram_count})

    graph_type.max_weight = max_weight
    graph_type.weight_list = ",".join(weight_list)
    graph_type.save()
    graph_type.histogram_data = histogram_list
    graph_type.save()
    graph_type.histogram_title = "توزیع اسناد براساس باهم‌آیی برچسب‌ها"
    graph_type.save()
    graph_type.is_document = 1
    graph_type.save()
