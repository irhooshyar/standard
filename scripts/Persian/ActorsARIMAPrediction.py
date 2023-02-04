import numpy as np
import pandas as pd
import warnings
from doc.models import ActorTimeSeries,GridSearchARIMAPredictionData
from operator import itemgetter
import time
import warnings
from math import sqrt
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error


def apply(folder, Country):

    batch_size = 1000
    start_t = time.time()

    
    actor_vectors = ActorTimeSeries.objects.filter(
        country_id__id=Country.id)


    actors_count = ActorTimeSeries.objects.filter(
        country_id__id=Country.id).count()

    print('actors_count= '+str(actors_count))

    # role_names = ['همه','متولی اجرا','همکار','دارای صلاحیت اختیاری']
    role_names = ['متولی اجرا']

    c = 0

    last_year = 1400
    test_size = 5
    # evaluate parameters
    p_values = [0, 1, 2, 4, 6, 8, 10]
    d_values = range(0, 3)
    q_values = range(0, 3)
    warnings.filterwarnings("ignore")
    
    time_series_json = {}

    for actor_vector in actor_vectors:
        actor_id = actor_vector.actor_id.id

        time_series_json['ARIMA'] = {
            'متولی اجرا':{'Prediction':{},'BestParameters':(),'Test':{},'RMSE':0}
            ,'همکار':{'Prediction':{},'BestParameters':(),'Test':{},'RMSE':0}
            ,'دارای صلاحیت اختیاری':{'Prediction':{},'BestParameters':(),'Test':{},'RMSE':0}
            ,'همه':{'Prediction':{},'BestParameters':(),'Test':{},'RMSE':0}
        }

        for role_name in role_names:

            year_dict = actor_vector.time_series_data[role_name]

            if last_year + 1 in year_dict:
                del year_dict[last_year+1]

            time_series_data = [value for (key, value) in sorted(
                year_dict.items(), key=lambda x: x[0], reverse=False)]

            try:
                best_cfg, best_score,best_test_prediction = evaluate_models(
                    time_series_data, p_values, d_values, q_values,test_size)


                test_prediction_dict = {}
                test_prediction_dict = dict(year_dict)

                j = 0
                for year in range(last_year-test_size+1,last_year+1):
                        test_prediction_dict[str(year)] = best_test_prediction[j]
                        j += 1

                prediction_year_dict = ARIMA_Prediction(
                    year_dict, last_year, best_cfg,test_size)

                time_series_json['ARIMA'][role_name]['RMSE'] = round(best_score)
                time_series_json['ARIMA'][role_name]['Prediction'] = prediction_year_dict
                time_series_json['ARIMA'][role_name]['Test'] = test_prediction_dict
                time_series_json['ARIMA'][role_name]['BestParameters'] = best_cfg

            except:
                pass


        prediction_obj = GridSearchARIMAPredictionData.objects.create(
        time_series_data = actor_vector,
        prediction_data = time_series_json)

        c += 1
        print(f"======= actor_id= {actor_id}========")
        print("=========== "+ str(c)+"/"+str(actors_count) + " =====================")


    end_t = time.time()

    print('ARIMA Prediction completed (' + str(end_t - start_t) + ').')


# evaluate an ARIMA model for a given order (p,d,q)
def evaluate_arima_model(X, arima_order,test_size):
    # prepare training dataset

    # train_size = int(len(X) * 0.66)
    train_size = int(len(X)) - test_size
    train, test = X[0:train_size], X[train_size:]

    history = [x for x in train]

    # make predictions
    predictions = list()
    for t in range(len(test)):
        model = ARIMA(history, order=arima_order)
        model_fit = model.fit()
        model.initialize_approximate_diffuse() # this line
        yhat = model_fit.forecast()[0]
        yhat = round(yhat)
        predictions.append(yhat)
        history.append(test[t])

    # calculate out of sample error
    rmse = sqrt(mean_squared_error(test, predictions))
    return rmse,predictions

# evaluate combinations of p, d and q values for an ARIMA model


def evaluate_models(dataset, p_values, d_values, q_values,test_size):
    best_score, best_cfg = float("inf"), None
    best_test_prediction = []
    for p in p_values:
        for d in d_values:
            for q in q_values:
                order = (p, d, q)
                try:
                    rmse,test_prediction = evaluate_arima_model(dataset, order,test_size)
                    if rmse < best_score:
                        best_score, best_cfg = rmse, order
                        best_test_prediction = test_prediction
                    # print('ARIMA%s RMSE=%.3f' % (order, rmse))
                except:
                    continue
    print('Best ARIMA%s RMSE=%.3f' % (best_cfg, best_score))
    return best_cfg, best_score,best_test_prediction


def ARIMA_Prediction(history_dict, last_year, arima_order,test_size):

    # make predictions
    predictions = history_dict

    if str(last_year+1) in predictions:
        del predictions[str(last_year+1)]


    history_values = [value for (key, value) in sorted(
        predictions.items(), key=lambda x: x[0], reverse=False)]

    for year in range(last_year+1, last_year + test_size + 1):
        
        model = ARIMA(history_values, order=arima_order)
        model.initialize_approximate_diffuse() # this line
        model_fit = model.fit()
        output = model_fit.forecast()
        yhat = round(output[0])
        predictions[str(year)] = yhat
        history_values.append(yhat)

    return predictions
