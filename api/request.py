import requests

url = 'http://localhost:5000/predict_api'
r = requests.post(url,json={'Builtup area':2, 'No of Floors':9})

print(r.json())
