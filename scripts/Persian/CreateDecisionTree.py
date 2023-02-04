from pathlib import Path
from abdal import config
from sklearn.model_selection import train_test_split
from sklearn import tree
from sklearn.tree import plot_tree

import json
import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier  

from doc.models import FeatureSelectionResults,FeatureSelectionAlgorithm




def generator_1(clf, features, labels,original_features, node_index=0,side=0):
  
    node = {}
    if clf.tree_.children_left[node_index] == -1:  # indicates leaf
        count_labels = zip(clf.tree_.value[node_index, 0], labels)
        node['name'] = ', '.join(('{} of {}'.format(int(count), label)
                                  for count, label in count_labels))
        node['size'] = sum( clf.tree_.value[node_index, 0]  )   
        node['side'] = 'left' if side == 'l' else 'right'                      
    else:

        count_labels = zip(clf.tree_.value[node_index, 0], labels)
        node['pred'] = ', '.join(('{} of {}'.format(int(count), label)
                                  for count, label in count_labels))
                                      
        node['side'] = 'left' if side == 'l' else 'right'                              
        feature = features[clf.tree_.feature[node_index]]
        threshold = clf.tree_.threshold[node_index]
        
        if ('_-_' in feature) and (feature not in original_features):
            node['name'] =  '{} = {}'.format(feature.split('_-_')[0], feature.split('_-_')[1] )
            node['type'] = 'categorical'
        else:
            node['name'] = '{} > {}'.format(feature, round(threshold,2) )
            node['type'] = 'numerical'
        
        left_index = clf.tree_.children_left[node_index]
        right_index = clf.tree_.children_right[node_index]
        
        node['size'] = sum (clf.tree_.value[node_index, 0])
        node['children'] = [generator_1(clf, features, labels, original_features, right_index,'r'),
                            generator_1(clf, features, labels, original_features, left_index,'l')]
                            
        
    return node



def generator_2(clf, features, labels,original_features, node_index=0,side=0,prev_index=0):

    node = {}
    if clf.tree_.children_left[node_index] == -1:  # indicates leaf
        count_labels = zip(clf.tree_.value[node_index, 0], labels)
        node['pred'] = ', '.join(('{} of {}'.format(int(count), label)
                                  for count, label in count_labels))
                                      
        node['side'] = 'left' if side == 'l' else 'right'                              
        feature = features[clf.tree_.feature[prev_index]]
        threshold = clf.tree_.threshold[prev_index]
        
            
        if node_index == 0:
            node["name"] = 'Root >'
        elif ('_-_' in feature) and (feature not in original_features):
            
            node['name'] =  '{} = {}'.format(feature.split('_-_')[0], feature.split('_-_')[1] ) if side == 'r' else '{} != {}'.format(feature.split('_-_')[0], feature.split('_-_')[1] )  
            node['type'] = 'categorical'
        else:
            node['name'] = '{} > {}'.format(feature, round(threshold,2) ) if side == 'r' else '{} <= {}'.format(feature, round(threshold,2) ) 
            node['type'] = 'numerical'
        
        left_index = clf.tree_.children_left[node_index]
        right_index = clf.tree_.children_right[node_index]
        
        node['size'] = sum (clf.tree_.value[node_index, 0])
           
    else:

        count_labels = zip(clf.tree_.value[node_index, 0], labels)
        node['pred'] = ', '.join(('{} of {}'.format(int(count), label)
                                  for count, label in count_labels))
                                      
        node['side'] = 'left' if side == 'l' else 'right'                              
        feature = features[clf.tree_.feature[prev_index]]
        threshold = clf.tree_.threshold[prev_index]
        
            
        if node_index == 0:
            node["name"] = 'Root >'
        elif ('_-_' in feature) and (feature not in original_features):
            
            node['name'] =  '{} = {}'.format(feature.split('_-_')[0], feature.split('_-_')[1] ) if side == 'r' else '{} != {}'.format(feature.split('_-_')[0], feature.split('_-_')[1] )  
            node['type'] = 'categorical'
        else:
            node['name'] = '{} > {}'.format(feature, round(threshold,2) ) if side == 'r' else '{} <= {}'.format(feature, round(threshold,2) ) 
            node['type'] = 'numerical'
        
        left_index = clf.tree_.children_left[node_index]
        right_index = clf.tree_.children_right[node_index]
        
        node['size'] = sum (clf.tree_.value[node_index, 0])
        node['children'] = [generator_2(clf, features, labels, original_features, right_index,'r',node_index),
                            generator_2(clf, features, labels, original_features, left_index,'l',node_index)]
                            
        
    return node
    
    
def apply(folder_name,Country, configs,c_algorithm_id,final_df = None):

    fs_algorithm_obj = FeatureSelectionAlgorithm.objects.get(name = "DecisionTree")
    
    FeatureSelectionResults.objects.filter(
        country = Country,
        c_algorithm__id = c_algorithm_id,
        f_algorithm = fs_algorithm_obj
    ).delete()

    df = final_df


    #load data from flat file
    if df is None:
        final_df_file_name = 'final_df_' + str(c_algorithm_id) + '.csv'
        final_df_file = str(Path(config.DECISION_TREE_PATH, folder_name,final_df_file_name))
        df=pd.read_csv(final_df_file,sep=';',encoding='utf32')

    df.dropna(inplace=True)


    #set the label column
    label_name = 'y'
    df.sort_values([label_name], ascending=[True], inplace=True)
    df= df.sort_index( ascending=[True])

    features = (df.drop(label_name,axis=1).columns.values)

    is_number = np.vectorize(lambda x: np.issubdtype(x, np.number))
    boolfeatures= is_number(df.drop(label_name,axis=1).dtypes)

    # df_dummy = pd.get_dummies(df.drop(label_name,axis=1),prefix_sep='_-_')
    
    x  = df.drop("y", axis='columns')
    y = df[label_name]

    # x_training_data, x_test_data, y_training_data, y_test_data = train_test_split(
    #     x, y, test_size = 0.3,random_state=1)

    print(f"max_depth= {configs['max_depth']}")

    clf = DecisionTreeClassifier(
        max_depth=100,
        # max_depth=configs['max_depth'],
        min_samples_leaf=0.02
    )

        
    clf.fit(x, y)
    # print(clf.feature_importances_)

    # feat_importance = clf.tree_.compute_feature_importances(normalize=True)
    # print("feat importance = " + str(feat_importance))
    important_features_chart_data = []
    

    for importance, name in sorted(zip(clf.feature_importances_, x.columns),reverse=True)[:10]:
        importance = round(importance*100,2)
        important_features_chart_data.append([name,importance])

    FeatureSelectionResults.objects.create(
        country = Country,
        c_algorithm_id = c_algorithm_id,
        f_algorithm = fs_algorithm_obj,
        important_words_chart_data = {"data":important_features_chart_data}
    )

    # predictions = clf.predict(x_test_data)
    # text_representation = tree.export_text(clf,feature_names = x.columns.tolist())
    # print(text_representation)

    if configs['generate_structure_1']:

        io=generator_1(clf, x.columns,np.unique(df[label_name]),features)
        # print(json.dumps(io, indent=4))
        structureC1_file_name = 'structureC1_' + str(c_algorithm_id) + '.json'
        structureC1_path = str(Path(config.DECISION_TREE_PATH, folder_name,structureC1_file_name))

        with open(structureC1_path, 'w') as outfile:
            json.dump(io, outfile, indent=4)
            
    if configs['generate_structure_2']:
        io=generator_2(clf, x.columns,np.unique(df[label_name]),features)
        
        structureC2_file_name = 'structureC2_' + str(c_algorithm_id) + '.json'

        structureC2_path = str(Path(config.DECISION_TREE_PATH, folder_name, structureC2_file_name))

        with open(structureC2_path, 'w') as outfile:
            json.dump(io, outfile, indent=4)

    print('============= DT Created ===================')