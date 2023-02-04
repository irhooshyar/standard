
from doc.models import Rahbari, RahbariLabelsGraph,RahbariLabel
import numpy as np
import after_response

@after_response.enable
def apply(folder_name, Country):
    RahbariLabelsGraph.objects.all().delete()

    rahbari_document_list = Rahbari.objects.all().exclude(labels = "نامشخص")
    labels_dict = {}
    for doc in rahbari_document_list:
        doc_labels = doc.labels
        
        if doc_labels[-1] == "؛":
            doc_labels = doc_labels[:-1]

        doc_labels = doc_labels.split("؛")

        if '' in doc_labels:
            doc_labels.remove('')

        if ' ' in doc_labels:
            doc_labels.remove(' ')

        for label in doc_labels:
            if len(label.replace(" ", "")) > 0:
                label = label.strip().replace('؛', '').replace("ائمه جمعه", "ائمه‌ جمعه").replace("ورزش‌کاران", "ورزشکاران")
                try:
                    label_object = RahbariLabel.objects.get(name=label)
                    label = label_object.name
                    if label not in labels_dict:
                        labels_dict[label] = [doc.id]
                    else:
                        labels_dict[label].append(doc.id)
                except:
                    print(label)


    labels_list = list(labels_dict.keys())
    print(len(labels_list))
    for i in range(labels_list.__len__()):
        print(i/labels_list.__len__())
        label1 = labels_list[i]
        label1_doc_list = labels_dict[label1]
        for j in range(i+1, labels_list.__len__()):
            label2 = labels_list[j]
            label2_doc_list = labels_dict[label2]

            common_doc = list(set(label1_doc_list) & set(label2_doc_list))

            if common_doc.__len__() > 0:
                node1 = {"id": label1, "name": label1,  "style": {"fill": "0080FF"}}
                node2 = {"id": label2, "name": label2,  "style": {"fill": "0080FF"}}
                common_document_count = common_doc.__len__()
                common_document_list = ",".join(np.array(common_doc).astype("str"))

                label_graph_obj = RahbariLabelsGraph.objects.create(source_label=label1, target_label=label2,
                                                  source_node=node1, target_node=node2,
                                                  common_document_count=common_document_count,
                                                  common_document_list=common_document_list)

                edge = {"id": str(label_graph_obj.id), "source": label1, "source_name": label1,
                        "target": label2, "target_name": label2, "weight": common_doc.__len__()}
                label_graph_obj.edge = edge
                label_graph_obj.save()






