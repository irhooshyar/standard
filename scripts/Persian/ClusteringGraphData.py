from doc.models import ClusteringAlorithm, ClusteringResults, ClusterTopic, ClusteringGraphData
def apply(Country):
    CreateCentroidsGraph()
    CreateSubjectKeywordsGraph()


def CreateCentroidsGraph():
    ClusteringGraphData.objects.all().delete()

    data = ClusteringResults.objects.all()

    for row in data:

        country = row.country
        algorithm = row.algorithm

        Nodes_data = []
        Edges_data = []
        addedNode = []
        addedEdge = []
        for edge in dict(row.similarity_chart_data)["data"]:

            src_id = ClusterTopic.objects.get(country=country, algorithm=algorithm, name=edge["x"]).id
            src_name = edge["x"]

            dest_id = ClusterTopic.objects.get(country=country, algorithm=algorithm, name=edge["y"]).id
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

        ClusteringGraphData.objects.create(country=country, algorithm=algorithm, centroids_nodes_data=Nodes_data, centroids_edges_data=Edges_data)


def CreateSubjectKeywordsGraph():


    data = ClusteringGraphData.objects.all().values("country_id", "algorithm_id").distinct()

    for item in data:
        print(item)
        country_id, algorithm_id = item["country_id"], item["algorithm_id"]
        print(country_id, algorithm_id)

        Graph_Data = ClusterTopic.objects.filter(country_id=country_id, algorithm_id=algorithm_id)

        Nodes_data = []
        Edges_data = []
        addedNode = []
        addedEdge = []

        for row in Graph_Data:



            src_id = row.id
            src_name = row.name
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


        ClusteringGraphData.objects.filter(country_id=country_id, algorithm_id=algorithm_id).update(subject_keywords_nodes_data=Nodes_data, subject_keywords_edges_data=Edges_data)
