import numpy as np
import pickle

modelD = pickle.load(open('modelD.pkl', 'rb'))
Builtup_area = 3000
No_of_Floors = 3
No_of_Workers = 50
features = [Builtup_area, No_of_Floors, No_of_Workers]
final_features = [np.array(features)]
prediction = modelD.predict(final_features)  
output = round(int(prediction[0]), 0)
print(output)