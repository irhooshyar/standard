# import numpy as np
# import tensorflow as tf
# from tensorflow.keras.models import Sequential
# from tensorflow.keras.layers import LSTM
# from tensorflow.keras.layers import Dense
# from tensorflow.keras.layers import Flatten
# from doc.models import ActorTimeSeries,LSTMPredictionData
# from operator import itemgetter
# import time

# def apply(folder,Country):
#     Create_List = []
#     batch_size = 50
#     start_t = time.time()

#     # LSTMPredictionData.objects.filter(
#     # time_series_data__country_id__id = Country.id
#     # # ,time_series_data__actor_id__name ="قوه مجریه"
#     # ).delete()


#     saved_record_ids = LSTMPredictionData.objects.filter(
#     time_series_data__country_id__id = Country.id
#     # ,time_series_data__actor_id__name ="قوه مجریه"
#     ).values_list("time_series_data__id",flat=True)

#     actor_vectors = ActorTimeSeries.objects.filter(
#         country_id__id = Country.id
#         # ,actor_id__name ="قوه مجریه"
#         ).exclude(id__in = saved_record_ids)

#     actors_count = ActorTimeSeries.objects.filter(
#         country_id__id = Country.id
#         # ,actor_id__name ="قوه مجریه"
#         ).exclude(id__in = saved_record_ids).count()

#     print('actors_count= '+str(actors_count))
    
#     # role_names = ['همه','متولی اجرا','همکار','دارای صلاحیت اختیاری']
#     role_names = ['همه']
#     last_year = 1400
#     c = 0
#     for actor_vector in actor_vectors:
#         time_series_json = {'همه':{}, 'متولی اجرا':{}, 'همکار':{}, 'دارای صلاحیت اختیاری':{}} 
        
#         for role_name in role_names:

#             year_dict = actor_vector.time_series_data[role_name]
            
#             if last_year + 1 in year_dict:
#                 del year_dict[last_year+1]

#             time_series_data =  [value for (key, value) in sorted(year_dict.items(), key=lambda x: x[0],reverse=False)]

#             prediction_year_dict =  LSTM_Prediction(time_series_data,year_dict,last_year)
            
#             time_series_json[role_name] = prediction_year_dict


#         prediction_obj = LSTMPredictionData.objects.create(
#         time_series_data = actor_vector,
#         prediction_data = time_series_json)
#         c += 1
#         print("================" + str(c)+"/"+str(actors_count)+" ====================")
        
#     #     Create_List.append(prediction_obj)

#     #     if Create_List.__len__() > batch_size:
#     #         LSTMPredictionData.objects.bulk_create(Create_List)
#     #         Create_List = []

#     # LSTMPredictionData.objects.bulk_create(Create_List)

    
#     end_t = time.time()        

#     print('LSTM Prediction completed (' + str(end_t - start_t) + ').')



# # preparing independent and dependent features
# def prepare_data(timeseries_data, n_features):
# 	X, y =[],[]
# 	for i in range(len(timeseries_data)):
# 		# find the end of this pattern
# 		end_ix = i + n_features
# 		# check if we are beyond the sequence
# 		if end_ix > len(timeseries_data)-1:
# 			break
# 		# gather input and output parts of the pattern
# 		seq_x, seq_y = timeseries_data[i:end_ix], timeseries_data[end_ix]
# 		X.append(seq_x)
# 		y.append(seq_y)
# 	return np.array(X), np.array(y)

# def LSTM_Prediction(timeseries_data,year_dict,last_year):
#     # define input sequence
    
#     np.random.seed(37)
#     tf.random.set_seed(1234)

#     # choose a number of time steps
#     n_steps = 5

#     # split into samples
#     X, y = prepare_data(timeseries_data, n_steps)

#     # print(X),print(y)

#     # reshape from [samples, timesteps] into [samples, timesteps, features]
#     n_features = 1
#     X = X.reshape((X.shape[0], X.shape[1], n_features))

#     # define model
#     model = Sequential()
#     model.add(LSTM(50, activation='relu', return_sequences=True, input_shape=(n_steps, n_features)))
#     model.add(LSTM(50, activation='relu'))
#     model.add(Dense(1))
#     model.compile(optimizer='adam', loss='mse')
#     # fit model
#     model.fit(X, y, epochs=100, verbose=1)


#     # demonstrate prediction for next 10 days
#     x_input = np.array(timeseries_data[-5:])
#     # print('x_input= '+str(x_input))
#     temp_input=list(x_input)
#     lst_output=[]
#     i=0
#     while(i<2):

#         if(len(temp_input)>5):
#             x_input=np.array(temp_input[1:])
#             # print("{} day input {}".format(i,x_input))
#             #print(x_input)
#             x_input = x_input.reshape((1, n_steps, n_features))
#             #print(x_input)
#             yhat = model.predict(x_input, verbose=0)
#             # print("{} day output {}".format(i,yhat))
#             temp_input.append(yhat[0][0])
#             temp_input=temp_input[1:]
#             #print(temp_input)
#             lst_output.append(round(yhat[0][0]))
#             i=i+1
#         else:
#             x_input = x_input.reshape((1, n_steps, n_features))
#             yhat = model.predict(x_input, verbose=0)
#             temp_input.append(yhat[0][0])
#             lst_output.append(round(yhat[0][0]))
#             i=i+1


#     new_time_series = timeseries_data + lst_output

#     # print('timeseries_data= '+str(timeseries_data))
#     # print('lst_output= '+str(lst_output))
#     # print('new time series= '+str(new_time_series))

#     prediction_year_dict = year_dict
#     # last_year = int(list(year_dict.keys())[-1])
    
#     for i in range(1,3):
#         new_year = last_year + i
#         prediction_year_dict[new_year] = new_time_series[(-3+i)]
    

#     return prediction_year_dict

    


