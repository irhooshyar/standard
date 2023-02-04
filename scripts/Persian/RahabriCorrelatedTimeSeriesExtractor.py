
from doc.models import Rahbari, RahbariLabelsTimeSeriesGraph,RahbariLabel,RahbariLabelsTimeSeries
import numpy as np
import pandas as pd
import math
from django.db.models import Q,F
import after_response


def apply(Country):
    RahbariLabelsTimeSeriesGraph.objects.all().delete()

    rahbari_trends_data = RahbariLabelsTimeSeries.objects.all().annotate(
        label_name = F('rahbari_label__name')).values()

    trends_dict = {}
    CreateList = []
    batch_size = 100000

    for trend in rahbari_trends_data:
        time_series_data = trend['time_series_data']
        label_id = trend['rahbari_label_id']
        trends_dict[label_id] = time_series_data

    trends_list = list(trends_dict.keys())

    print(len(trends_list))
    
    for i in range(trends_list.__len__()):
        print(i/trends_list.__len__())
        label1_id = trends_list[i]
        trend_dict_1 = trends_dict[label1_id]

        for j in range(i+1, trends_list.__len__()):
            label2_id = trends_list[j]
            trend_dict_2 = trends_dict[label2_id]

            year_vector_1 = pd.Series(list(trend_dict_1.values()))
            year_vector_2 = pd.Series(list(trend_dict_2.values()))
            correlation_value = round(year_vector_1.corr(year_vector_2), 2)

            if not math.isnan(correlation_value):
                new_obj = RahbariLabelsTimeSeriesGraph(
                    source_label_id = label1_id,
                    target_label_id = label2_id,
                    correlation_score = correlation_value
                )

                CreateList.append(new_obj)

                if CreateList.__len__() > batch_size:
                    RahbariLabelsTimeSeriesGraph.objects.bulk_create(CreateList)
                    CreateList = [] 


    RahbariLabelsTimeSeriesGraph.objects.bulk_create(CreateList)




