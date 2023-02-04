from doc.models import ClusteringAlorithm, ClusteringResults, ClusterTopic, ClusteringGraphData
from doc.models import AILDAResults,AIParagraphLDATopic,LDAGraphData

def apply(Country):
    CreateCentroidsGraph()
    CreateSubjectKeywordsGraph()


def CreateCentroidsGraph():
    LDAGraphData.objects.all().delete()

    data = AILDAResults.objects.all()

    for row in data:

        country = row.country
        number_of_topic = row.number_of_topic

        Nodes_data = []
        Edges_data = []
        addedNode = []
        addedEdge = []
        for edge in dict(row.similarity_chart_data)["data"]:

            src_id = AIParagraphLDATopic.objects.get(country=country, number_of_topic=number_of_topic, topic_name=edge["x"]).id
            src_id = str(src_id)
            src_name = edge["x"]

            dest_id = AIParagraphLDATopic.objects.get(country=country, number_of_topic=number_of_topic, topic_name=edge["y"]).id
            dest_id = str(dest_id)
            dest_name = edge["y"]

            weight = edge["heat"]

            node1 = {"id": src_id, "name": src_name, "label": src_name}
            if src_id not in addedNode:
                Nodes_data.append(node1)
                addedNode.append(src_id)

            node2 = {"id": dest_id, "name": dest_name, "label": dest_name}
            if dest_id not in addedNode:
                Nodes_data.append(node2)
                addedNode.append(dest_id)

            if [dest_id, src_id] not in addedEdge and src_id != dest_id:
                edge_dict = {
                    "source": src_id,
                    "source_name": src_name,
                    "target": dest_id,
                    "target_name": dest_name,
                    "weight": weight,
                }
                addedEdge.append([src_id, dest_id])
                Edges_data.append(edge_dict)

        LDAGraphData.objects.create(country=country, number_of_topic=number_of_topic, centroids_nodes_data=Nodes_data, centroids_edges_data=Edges_data)


def CreateSubjectKeywordsGraph():


    data = LDAGraphData.objects.all().values("country_id", "number_of_topic").distinct()

    for item in data:
        print(item)
        country_id, number_of_topic = item["country_id"], item["number_of_topic"]
        print(country_id, number_of_topic)

        Graph_Data = AIParagraphLDATopic.objects.filter(country_id=country_id, number_of_topic=number_of_topic)

        Nodes_data = []
        Edges_data = []
        addedNode = []
        addedEdge = []

        for row in Graph_Data:



            src_id = str(row.id)
            src_name = row.topic_name
            src_type = "cluster"

            node1 = {"id": src_id, "name": src_name, "label": src_name, "node_type": src_type, "size": 20, "type": "rect",
                     "style": {"fill": "#5C5CD5"}}

            if src_id not in addedNode:
                Nodes_data.append(node1)
                addedNode.append(src_id)

            keywords = dict(row.words)

            for word, score in keywords.items():
                dest_id = word
                dest_name = word
                dest_type = "keyword"

                weight = score

                node2 = {"id": dest_id, "name": dest_name, "node_type": dest_type, "style": {"fill": "#33C77D"}}
                if dest_id not in addedNode:
                    Nodes_data.append(node2)
                    addedNode.append(dest_id)

                if [dest_id, src_id] not in addedEdge and [src_id, dest_id] not in addedEdge:
                    edge_dict = {
                        "source": src_id,
                        "source_name": src_name,
                        "source_node_type": src_type,
                        "target": dest_id,
                        "target_name": dest_name,
                        "target_node_type": src_type,
                        "weight": float(weight),
                    }
                    addedEdge.append([src_id, dest_id])
                    Edges_data.append(edge_dict)


        LDAGraphData.objects.filter(country_id=country_id, number_of_topic=number_of_topic).update(subject_keywords_nodes_data=Nodes_data, subject_keywords_edges_data=Edges_data)
