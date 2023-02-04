import numpy as np
import pandas as pd
import warnings
from doc.models import ActorTimeSeries,AdvancedARIMAPredictionData
from operator import itemgetter
import time
from math import sqrt
import os
from scripts.Persian import FolderCreator
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.stattools import acf, pacf
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.graphics.tsaplots import plot_pacf
from statsmodels.tsa.arima.model import ARIMA
from matplotlib import pyplot as plt
from abdal import config
from pathlib import Path
from math import sqrt
from sklearn.metrics import mean_squared_error


def apply(folder, Country):
    batch_size = 1000
    Create_List = []

    start_t = time.time()
    AdvancedARIMAPredictionData.objects.filter(time_series_data__country_id__id = Country.id).delete()

    actor_vectors = ActorTimeSeries.objects.filter(
        country_id__id=Country.id)

    actors_count = ActorTimeSeries.objects.filter(
        country_id__id=Country.id).count()

    print('actors_count= '+str(actors_count))
    country_id = Country.id
    print("country id: ", country_id)
    role_names = ['همه','متولی اجرا','همکار','دارای صلاحیت اختیاری']
    c = 0
    acf_c = 0
    pacf_c = 0
    last_year = 1400
    # evaluate parameters
    p_value = 0
    d_value = 0
    q_value = 0

    PValue = 0

    eval_size = 3 
    time_series_json = {}
    for actor_vector in actor_vectors:
        acf_actor_id = actor_vector.actor_id_id
        pacf_actor_id = actor_vector.actor_id_id 
        print("actor id: ",actor_vector.actor_id_id)

        time_series_json['ARIMA'] = {
            'متولی اجرا':{'PredictionAdvance':[],'BestNewParameters':[]}
            ,'همکار':{'PredictionAdvance':[],'BestNewParameters':[]}
            ,'دارای صلاحیت اختیاری':{'PredictionAdvance':[],'BestNewParameters':[]}
            ,'همه':{'PredictionAdvance':[],'BestNewParameters':[]}
        }
        acf_c+=1
        pacf_c+=1
        for role_name in role_names:
            year_dict = actor_vector.time_series_data[role_name]           
            if last_year + 1 in year_dict:
                del year_dict[last_year+1]
            time_series_data = [value for (key, value) in sorted(
                year_dict.items(), key=lambda x: x[0], reverse=False)]
            history_key=[]
            history_value=[]
            for i in year_dict:
                history_key.append(i)
                history_value.append(year_dict[i])
            history_dict={"year":[],"count":[]}
            for i in range(len(history_key)):
                if int(history_key[i]) < 1401:
                    history_dict["year"].append(history_key[i]) 
                    history_dict["count"].append(history_value[i])         
            df=pd.DataFrame.from_dict(history_dict)
            df.set_index("year")
            for i in range(len(df["year"])):
                df["diff"] = 0
            df=df.dropna()
            d=0

            #first pvalue calculation
            PValue_f = pvalue_cal(df["count"])
            if np.isnan(PValue_f):
                PValue_f = 0.000
            PValue_f = round(PValue_f,3)
            print("p-value-first:", PValue_f)

            d_value , PValue= test_stationary(df,df["count"],d)
            if np.isnan(PValue):
                PValue = 0.000
            PValue = round(PValue,3)
            print("p-value:", PValue)
            count_variance = df['count'].var()
            part=0
            for i in range(len(df["diff"])):
                if np.isnan(float(df["diff"][i])):
                    part=part+1
                    #print("dff in: ",df["diff"][i])
                 
            if count_variance !=0:
                if d_value == 0:
                    ACF_plt(df["count"],acf_actor_id,role_name,country_id)
                    PACF_plt(df["count"],pacf_actor_id,role_name,country_id)
                    q_value=ACF(df["count"],acf_c)
                    p_value=PACF(df["count"],pacf_c)
                else:
                    ACF_plt(df["diff"][part:],acf_actor_id,role_name,country_id)
                    PACF_plt(df["diff"][part:],pacf_actor_id,role_name,country_id)
                    q_value=ACF(df["diff"][part:],acf_c)
                    p_value=PACF(df["diff"][part:],pacf_c)
            else:
                q_value=0
                p_value=0

            print("Order of ARIMA: (",p_value,",",d_value,",",q_value,")")
            order=[]
            order=[p_value,d_value,q_value]
            df_data_list = []
            for i in range(len(df["count"])):
                df_data_list.append(df["count"][i])

            rsme,best_eval_prediction = evaluate_models(
                df_data_list, p_value, d_value, q_value,eval_size)

            eval_prediction_dict = {}
            for i in dict(year_dict):
                if int(i) < 1401:
                    eval_prediction_dict[i] = dict(year_dict)[i]
            j = 0
            for year in range(last_year-eval_size+1,last_year+1):
                eval_prediction_dict[str(year)] = best_eval_prediction[j]
                j += 1

            prediction_year_dict_advance = ARIMA_Prediction_Advance(
                year_dict, p_value, d_value, q_value, last_year)

            time_series_json['ARIMA'][role_name]['PredictionAdvance'] = prediction_year_dict_advance
            time_series_json['ARIMA'][role_name]['BestNewParameters'] = order
            time_series_json['ARIMA'][role_name]['RMSE'] = round(rsme)
            time_series_json['ARIMA'][role_name]['P_VALUE_First'] = PValue_f
            time_series_json['ARIMA'][role_name]['P_VALUE_Last'] = PValue
            time_series_json['ARIMA'][role_name]['Eval'] = eval_prediction_dict

            # print("result1: ",time_series_json['ARIMA'][role_name]['PredictionAdvance'])
            # print("result2: ",time_series_json['ARIMA'][role_name]['BestNewParameters'])
            # print("result3: ",time_series_json['ARIMA'][role_name]['RMSE'])
            # print("result4: ",time_series_json['ARIMA'][role_name]['Eval'])


        prediction_obj = AdvancedARIMAPredictionData.objects.create(
        time_series_data = actor_vector,
        prediction_data = time_series_json)

        Create_List.append(prediction_obj)

        c += 1
        print("===================== " + str(c)+"/"+str(actors_count) + "===================")

        
    
    end_t = time.time() 


    print('ARIMA Prediction completed (' + str(end_t - start_t) + ').')

#first pvalue calculation
def pvalue_cal(ts):
    stats = ['Test Statistic','p-value','Lags','Observations']
    df_test = adfuller(ts, autolag='AIC')
    df_results = pd.Series(df_test[0:4], index=stats)
    for key,value in df_test[4].items():
        df_results['Critical Value (%s)'%key] = value
    p_value = df_results[1]
    print (df_results)
    return p_value  

#Test stationary
def test_stationary(df,ts,d):
    stats = ['Test Statistic','p-value','Lags','Observations']
    df_test = adfuller(ts, autolag='AIC')
    df_results = pd.Series(df_test[0:4], index=stats)
    for key,value in df_test[4].items():
        df_results['Critical Value (%s)'%key] = value
    p_value = df_results[1]
    print (df_results)     
    if df_results[1] > 0.05:
        df["diff"] = ts - ts.shift(1)
        return test_stationary(df,df["diff"].dropna(inplace=False),d+1)
    else:
        return d,p_value
            
def ACF_PACF_Create_Folder(source_path, folder_name=None):  
    if not os.path.isdir(source_path):
        os.mkdir(source_path)
    if folder_name is not None:
        folder_path = str(Path(source_path, folder_name))
        FolderCreator.apply(folder_path)

def ACF_plt(ts,actor_id,role_name,country_id):
    fig = plt.figure()
    ax1 = fig.add_subplot(212)
    fig = sm.graphics.tsa.plot_acf(ts, lags=7, ax=ax1)
    ACF_PACF_Create_Folder(config.ACF_PATH)
    acf_file_name = str(country_id)+'-'+str(actor_id)+'-'+role_name+'.png'
    acf_file_path = str(Path(config.ACF_PATH,acf_file_name))
    fig.savefig(acf_file_path,dpi=100,bbox_inches='tight')

def PACF_plt(ts,actor_id,role_name,country_id):
    fig = plt.figure()
    ax2 = fig.add_subplot(212)
    fig = sm.graphics.tsa.plot_pacf(ts, lags=3, ax=ax2)
    fig.set_size_inches(18.5, 10.5)
    fig.set_size_inches(13.6, 6.5)
    ACF_PACF_Create_Folder(config.PACF_PATH)
    pacf_file_name = str(country_id)+'-'+str(actor_id)+'-'+role_name+'.png'
    pacf_file_path = str(Path(config.PACF_PATH,pacf_file_name))
    fig.savefig(pacf_file_path,dpi=100,bbox_inches='tight')

def ACF(ts,c):
    acf_list=[]
    m=0
    acf_values = acf(ts)
    acf_list = np.round(acf_values,2)
    m=max(abs(acf_list[1:]))
    for i in range(len(acf_list)):
        if abs(acf_list[i]) == m:
            return i

def PACF(ts,c):
    pacf_list=[]
    m=0
    pacf_values = pacf(ts)
    pacf_list = np.round(pacf_values,2)
    m=max(abs(pacf_list[1:]))
    for i in range(len(pacf_list)):
        if abs(pacf_list[i]) == m:
            return i

# evaluate an ARIMA model for a given order (p,d,q)
def evaluate_arima_model(X, arima_order,eval_size):
    train_size = int(len(X)) - eval_size
    train, evaluate = X[0:train_size], X[train_size:]
    history = [x for x in train]
    predictions = list()
    for t in range(len(evaluate)):
        model = ARIMA(history, order=arima_order)
        model.initialize_approximate_diffuse(variance=None)
        model_fit = model.fit() 
        yhat = model_fit.forecast()[0]
        if np.isnan(float(yhat)):
            yhat = 0
        yhat = round(yhat,2)
        predictions.append(yhat)
        history.append(evaluate[t])

    rmse = sqrt(mean_squared_error(evaluate, predictions))
    return rmse,predictions

# evaluate combinations of p, d and q values for an ARIMA model
def evaluate_models(dataset, p_value, d_value, q_value,eval_size):
    order = (p_value, d_value, q_value)
    rmse,eval_prediction = evaluate_arima_model(dataset, order,eval_size)    
    return rmse,eval_prediction

def ARIMA_Prediction_Advance(history_dict, p, d, q, last_year):
    # make predictions
    predictions = history_dict
    others=[]
    for i in predictions:
        if int(i) > 1400:
            others.append(i)

    for j in range(len(others)):
        if str(others[j]) in predictions:
            del predictions[str(others[j])]

    history_values = [value for (key, value) in sorted(
        predictions.items(), key=lambda x: x[0], reverse=False)]

    # print("history_dict=================")
    # print(history_dict)
    # print("predictions==============")
    # print(predictions)
    # print("others===================")
    # print(others)
    for year in range(last_year+1, last_year + 6):

        model = ARIMA(history_values, order=(p, d, q))
        model.initialize_approximate_diffuse(variance=None)
        model_fit = model.fit()
        output = model_fit.forecast()
        if np.isnan(float(output[0])):
            output[0] = 0
        yhat = round(output[0],2)  

        # negative prediction -> 0: only in ui chart
        if yhat < 0:
            predictions[str(year)] = 0
        else:
            predictions[str(year)] = yhat
   
        history_values.append(yhat)

    return predictions


    