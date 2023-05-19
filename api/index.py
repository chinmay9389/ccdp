from flask import Flask, request, render_template
import numpy as np
import pickle
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
from sklearn import linear_model
import os
import os.path



app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
modelD = pickle.load(open('modelD.pkl', 'rb'))


def graph(newb,newf,newsm):
    df = pd.read_csv('dataset.csv')
    X=df[['Builtup area','No of Floors','No of Workers']]
    y=df['Time in months']
    
    
    #sklearn technique
    regr = linear_model.LinearRegression()
    regr.fit(X, y)
    
    newb=int(newb)
    newf=int(newf)
    newsm=int(newsm)
    
    
    features = [newb, newf, newsm]
    final_features = [np.array(features)]
    print(final_features)
    val=modelD.predict(final_features)
    val = int(val)
    
    if(os.path.exists("static/plot1.jpg")):
        os.remove("static/plot1.jpg")
    if(os.path.exists("static/plot2.jpg")):
        os.remove("static/plot2.jpg")
    if(os.path.exists("static/plot3.jpg")):
        os.remove("static/plot3.jpg")
    
    plt.scatter(df['Builtup area'], df['Time in months'], color='black')
    plt.scatter(newb,val,color='blue',marker="^")
    plt.title('Bulitup area vs Time in months', fontsize=14)
    plt.xlabel('Builtup area', fontsize=14)
    plt.ylabel('Time in months', fontsize=14)
    plt.grid(True)
    #plt.show()
    plt.savefig('static/plot1.jpg', dpi=200)
    plt.clf()
    
    plt.scatter(df['No of Floors'], df['Time in months'], color='red')
    plt.scatter(newf,val,color='blue',marker="^")
    plt.title('No of Floors vs Time in months', fontsize=14)
    plt.xlabel('No of Floors', fontsize=14)
    plt.ylabel('Time in months', fontsize=14)
    plt.grid(True)
    #plt.show()
    plt.savefig('static/plot2.jpg', dpi=200)
    plt.clf()
    
    plt.scatter(df['No of Workers'], df['Time in months'], color='green')
    plt.scatter(newsm,val,color='blue',marker="^")
    plt.title('No of Workers vs Time in months', fontsize=14)
    plt.xlabel('No of Workers', fontsize=14)
    plt.ylabel('Time in months', fontsize=14)
    plt.grid(True)
    #plt.show()
    plt.savefig('static/plot3.jpg', dpi=200)
    plt.clf()


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

@app.route('/duration.html/<int:i>', methods=['GET', 'POST'])
def graph_1(i):
    print(i)
    mydb = mysql.connector.connect(
    host = "localhost",
    user = "test",
    password = "admin",
    database = "dataset"
    )

    sql_query = "select * from dataset,breakdown where dataset.ID = breakdown.id"
    cursor = mydb.cursor()
    cursor.execute(sql_query)
    records = cursor.fetchall()
    
    for row in records:
        if (i==row[0]):
            Builtup_area = row[1]
            No_of_Floors = row[2]
            No_of_Workers = row[3]
            
    print(Builtup_area)
    print(No_of_Floors)
    print(No_of_Workers)
    
    graph(Builtup_area, No_of_Floors, No_of_Workers)
    
    
    return render_template('/duration.html', breakdown=records)

@app.route('/works.html', methods=['GET', 'POST'])
def works():
    return render_template('works.html')

@app.route('/about.html', methods=['GET', 'POST'])
def about():
    return render_template('about.html')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/duration.html', methods=['GET', 'POST'])
def duration():
    
    mydb = mysql.connector.connect(
        host = "localhost",
        user = "test",
        password = "admin",
        database = "dataset"
        )

    sql_query = "select * from dataset"
    cursor = mydb.cursor()
    cursor.execute(sql_query)
    records = cursor.fetchall()
    
    sql_query = "select * from dataset,breakdown where dataset.ID = breakdown.id"
    cursor = mydb.cursor()
    cursor.execute(sql_query)
    breakdown = cursor.fetchall()
    
    print(breakdown)
    #graph()
    return render_template('duration.html', records=records, breakdown=breakdown)


@app.route('/cost.html', methods=['GET', 'POST'])
def cost():
    mydb = mysql.connector.connect(
        host = "localhost",
        user = "test",
        password = "admin",
        database = "dataset"
        )

    sql_query = "select * from cost"
    cursor = mydb.cursor()
    cursor.execute(sql_query)
    records = cursor.fetchall()
    mydb.commit()


    return render_template('cost.html', location1 = records)

@app.route('/predictD', methods=['GET','POST'])
def predictD():
    

    features = [int(x) for x in request.form.values()]
    final_features = [np.array(features)]
    
    prediction = modelD.predict(final_features)


    output = round(int(prediction[0]), 0)
    mydb = mysql.connector.connect(
        host = "localhost",
        user = "test",
        password = "admin",
        database = "dataset"
        )

    mycursor = mydb.cursor()

    sql = "INSERT INTO dataset (Builtup_area, No_of_Floors, No_of_Workers, Months) VALUES (%s, %s, %s, %s)"
    val = [(int(features[0]), int(features[1]), int(features[2]), int(output))]

    mycursor.executemany(sql, val)
    mydb.commit()
    
    mycursor = mydb.cursor()
    sql = "INSERT INTO breakdown (location, typework, cost, avg, good, best) VALUES (%s, %s, %s, %s, %s, %s)"
    val = ("none", "none", "TBC", "none", "none", "none")
    mycursor.execute(sql, val)
    mydb.commit()

    sql_query = "select * from dataset,breakdown where dataset.ID = breakdown.id"
    cursor = mydb.cursor()
    cursor.execute(sql_query)
    records = cursor.fetchall()
    mydb.commit()

    for row in records:
        ID= row[0]
        Builtup_area=row[1]
        No_of_Floors=row[2]
        No_of_Workers=row[3]

    return render_template('duration.html', prediction_text='It will take approximately {} months to complete'.format(output),
                           ID = '{}'.format(ID),
                           Builtup_area = '{}'.format(Builtup_area),
                           No_of_Floors = '{}'.format(No_of_Floors),
                           No_of_Workers = '{}'.format(No_of_Workers),
                           breakdown = records)

@app.route('/submitD', methods=['GET', 'POST'])
def submitD():
    mydb = mysql.connector.connect(
        host = "localhost",
        user = "test",
        password = "admin",
        database = "dataset"
        )

    sql_query = "select * from dataset,breakdown where dataset.ID = breakdown.id"
    cursor = mydb.cursor()
    cursor.execute(sql_query)
    records = cursor.fetchall()
    mydb.commit()


    mydb1 = mysql.connector.connect(
            host = "localhost",
            user = "test",
            password = "admin",
            database = "dataset"
        )

    mycursor = mydb1.cursor()

    for i in records:
        sql = "INSERT INTO traindata (Builtup_area, No_of_Floors, No_of_Workers, Months) VALUES (%s, %s, %s, %s)"
        val = [(int(i[1]), int(i[2]), int(i[3]), int(i[4]))]
        mycursor.executemany(sql, val)
        mydb1.commit()

    sql_query = "truncate table dataset"
    cursor = mydb.cursor()
    cursor.execute(sql_query)
    mydb.commit()

    return render_template('duration.html',text = 'The database has been updated!')

@app.route('/clear', methods=['GET', 'POST'])
def clear():

        mydb = mysql.connector.connect(
        host = "localhost",
        user = "test",
        password = "admin",
        database = "dataset"
        )

        sql_query = "select * from dataset"
        cursor = mydb.cursor()
        cursor.execute(sql_query)
        records = cursor.fetchall()

        if(len(records) == 0):
            return render_template('duration.html',text= 'The database is empty!')

        else:
            sql_query = "truncate table dataset"
            cursor = mydb.cursor()
            cursor.execute(sql_query)
            mydb.commit()
            
            sql_query = "truncate table breakdown"
            cursor = mydb.cursor()
            cursor.execute(sql_query)
            mydb.commit()
            return render_template('duration.html',text = 'The database has been cleared!')

@app.route('/calC', methods=['GET', 'POST'])
def calC():

    location = 0
    val1= 0
    features = [int(x) for x in request.form.values()]
    print(features)
    mydb = mysql.connector.connect(
        host = "localhost",
        user = "test",
        password = "admin",
        database = "dataset"
        )

    sql_query = "select * from cost"
    cursor = mydb.cursor()
    cursor.execute(sql_query)
    records = cursor.fetchall()
    mydb.commit()


    if(features[3]==1):
        build= "Commercial"
    else:
        build  = "Residential"

    if(features[4]==2):
        wrk = "labour only"
    else:
        wrk  = "materials + labour-outsourced"

    if(features[5]==1):
        qlty = "Average Quality"
    elif(features[5]==3):
        qlty = "Best Quality"
    else:
        qlty = "Good Quality"

    for i in records:
        if(i[0]==features[2]):
            location = i[1]
            if(features[3]==2):
                if(features[4]==1):
                    if(features[5]==1):
                        val1 = i[4]
                    elif(features[5]==2):
                        val1 = i[5]
                    else:
                        val1 = i[6]
                else:
                    val1 = i[3]
                    qlty = "not selected"
            else:
                val1 = i[2]
                wrk= "not selected"
                qlty = "not selected"
        elif(features[2]==0):
            location=records[-1][1]
            val1 = i[5]

    output = val1*int(features[0])*int(features[1])
    output = output + (0.2*output)
    output = '{:,.0f}'.format(output)

    sql_query = "select * from material"
    cursor = mydb.cursor()
    cursor.execute(sql_query)
    materials = cursor.fetchall()
    mydb.commit()

    j=[]
    for i in materials:
        mul = i[2]*features[0]*features[1]
        j.append(int(mul))

    return render_template('cost.html', calc_text='It will take approximately Rs. {} as budget to complete'.format(output),
                           Builtup_area = '{}'.format(int(features[0])),
                           No_of_Floors = '{}'.format(int(features[1])),
                           location = '{}'.format(location),
                           location1 = records,
                           records = materials,
                           values = j,
                           build = build,
                           wrk = wrk,
                           qlty = qlty)

@app.route('/cost_dur/<int:i>', methods=['GET', 'POST'])
def cost_dur(i):
    mydb = mysql.connector.connect(
        host = "localhost",
        user = "test",
        password = "admin",
        database = "dataset"
        )

    sql_query = "select * from dataset"
    cursor = mydb.cursor()
    cursor.execute(sql_query)
    records = cursor.fetchall()
    mydb.commit()
    
    #print(i)
    
    
    for row in records:
        #print(row[0])
        if(row[0]==i):
            Builtup_area=row[1]
            No_of_Floors=row[2]
            No_of_Workers=row[3]
            months = row[4]
            break;

    #print(Builtup_area)
    sql_query = "select * from cost"
    cursor = mydb.cursor()
    cursor.execute(sql_query)
    records = cursor.fetchall()
    mydb.commit()

    return render_template('/cost_dur.html', Builtup_area = '{}'.format(Builtup_area),
                           No_of_Floors = '{}'.format(No_of_Floors),
                           No_of_Workers = '{}'.format(No_of_Workers),
                           location1=records,
                           months=months,
                           i = i)

@app.route('/calC_D', methods=['POST'])
def calC_D():
    
    avg = 0
    good = 0
    best = 0
    val1= 0
    No_of_Workers_def = 50
    features1 = [int(x) for x in request.form.values()]
    id1 = features1[0]
    features = features1[1:]
    #print(id1)
    #print(features)
    
    mydb = mysql.connector.connect(
        host = "localhost",
        user = "test",
        password = "admin",
        database = "dataset"
        )

    sql_query = "select * from dataset"
    cursor = mydb.cursor()
    cursor.execute(sql_query)
    rec = cursor.fetchall()
    mydb.commit()


    mon = rec[id1-1][4]
    mon = int(mon)
    #print("month:{}".format(mon))

    sql_query = "select * from cost"
    cursor = mydb.cursor()
    cursor.execute(sql_query)
    records = cursor.fetchall()
    mydb.commit()
    

     
    #print(features)
    

    
    if(features[4]==2):
        build = "Residential"
    elif(features[4]==1):
        build= "Commercial"
    else:
        build  = "Residential"

    if(features[5]==1):
        wrk = "materials + labour-outsourced"
    elif(features[5]==2):
        wrk = "labour only"
    else:
        wrk = "materials + labour-outsourced"

    if(features[6]==1):
        qlty = "Average Quality"
    elif(features[6]==2):
        qlty = "Good Quality"
    elif(features[6]==3):
        qlty = "Best Quality"
    else:
        qlty = "Good Quality"

    for i in records:
        if(i[0]==features[3]):
            location = i[1]
            if(features[4]==2):
                if(features[5]==1):
                    avg = i[4]
                    good = i[5]
                    best = i[6]
                    if(features[6]==1):
                        val1 = i[4]
                    elif(features[6]==2):
                        val1 = i[5]
                    else:
                        val1 = i[6]
                else:
                    val1 = i[3]
                    qlty = "not selected"
            else:
                val1 = i[2]
                wrk= "not selected"
                qlty = "not selected"
        elif(features[3]==0):
            location=records[-1][1]
            val1 = i[5]
    
    #print("printing avg, good and best:")
    #print(avg, good, best)
    #print(features)
    sql_query = "select * from material"
    cursor = mydb.cursor()
    cursor.execute(sql_query)
    materials = cursor.fetchall()
    mydb.commit()

    j=[]
    for i in materials:
        mul = i[2]*features[0]*features[1]
        j.append(int(mul))

    features2 = [features[0], features[1], No_of_Workers_def]
    final_features = [np.array(features2)]
    prediction = modelD.predict(final_features)
    dur_output = round(int(prediction[0]), 0)

    output = val1*int(features[0])*int(features[1])
    output = output + (0.2*output)
    
    avg_output = avg*int(features[0])*int(features[1])
    avg_output = avg_output + (0.2*avg_output)
    good_output = good*int(features[0])*int(features[1])
    good_output = good_output + (0.2*good_output)
    best_output = best*int(features[0])*int(features[1])
    best_output = best_output + (0.2*best_output)

    mon_def = dur_output
    new_val = 0

    #print(output)

    if (mon>=mon_def):
        new_val = mon - mon_def
        new_val = new_val/mon_def
        new_val = new_val/4
        new_val = 1 + new_val
        final = output * new_val
        f_avg = avg_output * new_val
        f_good = good_output * new_val
        f_best = best_output * new_val

    elif(mon_def>mon):
        new_val = mon_def - mon
        new_val = new_val/mon_def
        new_val = new_val/4
        new_val = 1 - new_val
        final = output * new_val
        f_avg = avg_output * new_val
        f_good = good_output * new_val
        f_best = best_output * new_val

    final = '{:,.0f}'.format(final)
    f_avg = '{:,.0f}'.format(f_avg)
    f_good = '{:,.0f}'.format(f_good)
    f_best = '{:,.0f}'.format(f_best)
    
    
    print("printing final avg, good and best:")
    print(f_avg, f_good, f_best)
    #print(type(location))
    #print(type(wrk))
    mycursor = mydb.cursor()
    sql = "UPDATE breakdown set location= %s, typework=%s, cost=%s, avg=%s, good=%s, best=%s WHERE id=%s"
    val = (location, wrk, str(final), f_avg, f_good, f_best, id1)
    mycursor.execute(sql, val)
    mydb.commit()

    return render_template('cost_dur.html', calc_text='It will take approximately Rs. {} as budget to complete'.format(final),
                           Builtup_area = '{}'.format(int(features[0])),
                           No_of_Floors = '{}'.format(int(features[1])),
                           No_of_Workers = '{}'.format(int(features[2])),
                           location1 = records,
                           location = location,
                           records = materials,
                           months = mon,
                           values = j,
                           build = build,
                           wrk = wrk,
                           qlty = qlty,
                           i = id1)

if __name__ == "__main__":
    app.run(debug=True)
