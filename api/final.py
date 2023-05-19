#importing libraries
#ref : https://towardsdatascience.com/multiple-linear-regression-model-using-python-machine-learning-d00c78f1172a
#red2 : https://medium.com/@manjabogicevic/multiple-linear-regression-using-python-b99754591ac0
#ref3 : https://heartbeat.fritz.ai/implementing-multiple-linear-regression-using-sklearn-43b3d3f2fe8b
import pandas as pd
from sklearn import linear_model
import pickle


#reading dataset
dataset = pd.read_csv('dataset.csv')
X=dataset[['Builtup area','No of Floors','No of Workers']]
y=dataset['Time in months']

#sklearn technique
regr = linear_model.LinearRegression()
regr.fit(X, y)


pickle.dump(regr, open('modelD.pkl', 'wb'))