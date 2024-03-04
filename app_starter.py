# Name Jingzhen, USC email jwang977@usc.edu
# ITP 216, Spring 2023
# Section: number
# Final project
# Description:
# website application

from flask import Flask, redirect, render_template, request, session, url_for, Response, send_file
import os
import sqlite3 as sl
import io
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn import preprocessing
label_encoder = preprocessing.LabelEncoder()

app = Flask(__name__)

db = "grad_database/grad.db"
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


# root end point
# the home page that let user select
@app.route("/")
def home():
    #GRE Scores ( out of 340 ) TOEFL Scores ( out of 120 ) University Rating ( out of 5 ) Statement of Purpose and Letter of Recommendation Strength ( out of 5 ) Undergraduate GPA ( out of 10 ) Research Experience ( either 0 or 1 )
    ## grad (`SerialNo` number, `GRE` number, `TOEFL` number, `URating` number, `SOP` number, `LOR` number, `CGPA` number, `Research` number, `Choice` number)
    cri_key = ["GRE Scores (out of 340)","TOEFL Scores (out of 120)","Statement of Purpose (out of 5)","Letter of recommendation (out of 5)" ,"GPA (out of 10)","Research Experience(either 0 or 1)"]
    cri_value = ["GRE", "TOEFL", "SOP", "LOR", "CGPA", "Research"]
    criteria = {k:v for k, v in zip(cri_key,cri_value)}
    options = {i: i for i in range(1, 6)}

    return render_template("home.html", message='This is a website to visualize the factor and rate of graduate school application', criteria=criteria, options=options)

@app.route("/submit_criteria", methods=["POST"])
def submit_criteria():
    print(request.form['criteria'])
    session['criteria'] = request.form["criteria"]
    if 'criteria' not in session or session["criteria"] == "":
        return redirect(url_for("home"))
    if "URating" not in request.form:
        return redirect(url_for("home"))
    session["URating"] = request.form["URating"]
    return redirect(url_for("criteria_current", URating=session["URating"], criteria=session["criteria"]))

@app.route("/Graduate_School_Prediction/<URating>/<criteria>")
def criteria_current(criteria, URating):
    return render_template("criteria.html", criteria=criteria, URating=URating, project=False)

@app.route("/fig/<criteria>/<URating>")
def fig(criteria, URating):
    fig = create_figure(criteria, URating)

    # img = io.BytesIO()
    # fig.savefig(img, format='png')
    # img.seek(0)
    # w = FileWrapper(img)
    # # w = werkzeug.wsgi.wrap_file(img)
    # return Response(w, mimetype="text/plain", direct_passthrough=True)

    img = io.BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)
    return send_file(img, mimetype="image/png")

@app.route("/submit_projection", methods=["POST"])
def submit_projection():
    if 'URating' not in session:
        return redirect(url_for("home"))
    X_test = []
    X_test.append(request.form["GRE"])
    X_test.append(request.form["TOEFL"])
    X_test.append(request.form["SOP"])
    X_test.append(request.form["LOR"])
    X_test.append(request.form["CGPA"])
    X_test.append(request.form["Research"])
    session["DataPredict"] = X_test
    # THESE NEED TO BE BACK IN!
    # if session["locale"] == "" or session["data_request"] == "" or session["date"] == "":
    #     return redirect(url_for("home"))
    return redirect(url_for("Graduate_School_Prediction_Projection", URating=session["URating"], criteria=session["criteria"]))

@app.route("/Graduate_School_Prediction/<URating>/projection/<criteria>")
def Graduate_School_Prediction_Projection(criteria, URating):
    return render_template("criteria.html", criteria=criteria, URating=URating, project=True)

def create_dataframe(criteria, URating):
    # Check if the criteria is valid
    if criteria not in ['GRE', 'TOEFL', 'SOP', 'LOR', 'CGPA', 'Research']:
        raise ValueError("Invalid criteria. Choose a valid column name except 'COA' or 'URating'.")

    # Establish a connection to the database
    conn = sl.connect(db)
    curs = conn.cursor()

    # Query the data with the specified criteria and URating
    query = f"SELECT GRE, TOEFL, SOP, LOR, CGPA, Research, COA FROM grad WHERE URating = ?"
    curs.execute(query, (URating,))

    # Fetch the data and create a DataFrame
    data = curs.fetchall()
    df = pd.DataFrame(data, columns=['GRE', 'TOEFL', 'SOP', 'LOR', 'CGPA', 'Research', 'COA'])

    # Close the cursor and connection
    curs.close()
    conn.close()

    return df

def create_figure(criteria, URating):
    df = create_dataframe(criteria, URating)

    #drop the null
    df = df[df[criteria].notnull()]
    df.sort_values(inplace=True, by=criteria)
    # print(session)

    # print the projection if exist
    preduction = -1
    print(session)
    if "DataPredict" in session:
        preduction = KnnFit(df)




    fig, ax = plt.subplots(1,1)
    # ax = fig.add_subplot(1, 1, 1)
    fig.suptitle(criteria + " cases in " + str(URating) + " level of university")
    # fig, ax = plt.subplots(1, 1)
    ax.scatter(df[criteria], df["COA"], alpha=0.7, color='lightsalmon')
    if preduction != -1:
        ax.axhline(y=preduction, color='r')
    # ax.hist(df["COA"])
    ax.set(xlabel=criteria, ylabel="chance of admission")  # , xticks=range(0, len(df), 31))
    # fig.show()
    return fig

def KnnFit(df):
    print(df)
    # df.drop(columns=[])

    coa = df['COA']
    df_train = df.drop(columns='COA')

    # print(type(coa))
    # print(type(df_train))
    # print(coa.shape)
    # print(df_train.shape)

    X_train, X_test, y_train, y_test = \
        train_test_split(df_train, coa,
                     test_size=0.1)

    # print(type(X_train))
    # print(type(y_train))
    # print(X_train.shape)
    # print(y_train.shape)



    knn = KNeighborsClassifier(n_neighbors=1)
    # training data, training target

    X_train = X_train.to_numpy()
    y_train = y_train.to_numpy()

    y_train = (y_train*100).astype(int)


    print("y_train:",y_train)
    print("y_train:",type(y_train))
    knn.fit(X_train, y_train)

    # test=[[330,110,5,5,10,1]]
    # prediction = knn.predict(test)


    prediction = knn.predict([list(map(int, session['DataPredict']))])
    print(session['DataPredict'])
    print("prediction:", prediction/100)
    return prediction/100
    # if 'date' not in session:
    #     fig = Figure()
    #     ax = fig.add_subplot(1, 1, 1)
    #     fig.suptitle(URating.capitalize() + " cases in " + URating + "level of university")
    #     # fig, ax = plt.subplots(1, 1)
    #     ax.plot(df[criteria], df["COA"])
    #     ax.set(xlabel=criteria, ylabel="choice of admission")#, xticks=range(0, len(df), 31))
    #     return fig
    # else:
    #     df['datemod'] = df['date'].map(datetime.datetime.toordinal)
    #     y = df['cases'][-30:].values
    #     X = df['datemod'][-30:].values.reshape(-1, 1)
    #     # session['date'] = '11/11/20'  # REMOVE THIS LATER
    #     dt = [[datetime.datetime.strptime(session['date'], '%m/%d/%y')]]
    #     print('dt:', dt)
    #     draw = datetime.datetime.toordinal(dt[0][0])
    #     dord = datetime.datetime.fromordinal(int(draw))
    #     regr = LinearRegression(fit_intercept=True, normalize=True, copy_X=True, n_jobs=2)
    #     regr.fit(X, y)
    #     pred = int(regr.predict([[draw]])[0])
    #     df = df.append({'date': dord,
    #                     'cases': pred,
    #                     'datemod': draw}, ignore_index=True)
    #     fig = Figure()
    #     ax = fig.add_subplot(1, 1, 1)
    #     fig.suptitle('By ' + session['date'] + ', there will be ' + str(pred) + ' ' + data_request.capitalize() + " cases in " + locale)
    #     ax.plot(df["date"], df["cases"])
    #     ax.set(xlabel="date", ylabel="cases")  # , xticks=range(0, len(df), 31))
    #     return fig


# main entrypoint
# runs app
if __name__ == "__main__":
    # DB function unit testing:

    # print(f'{create_dataframe("CGPA", 1)}')

    # df = create_dataframe("CGPA", 5)
    # KnnFit(df)



    app.secret_key = os.urandom(12)
    app.run(debug=True)

