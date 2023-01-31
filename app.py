import pickle
import random
from flask import Flask, render_template, redirect, url_for, request, jsonify
from pymongo import MongoClient
# this is the objectID() class you'll use to convert string IDs to ObjectID objects.
import config
from recommenders.utils.python_utils import binarize
from recommenders.utils.timer import Timer
# from recommenders.datasets import movielens
from recommenders.datasets.python_splitters import python_stratified_split
from recommenders.datasets.spark_splitters import spark_random_split
from recommenders.evaluation.python_evaluation import (
    map_at_k,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
    rmse,
    mae,
    logloss,
    rsquared,
    exp_var
)
from recommenders.models.sar import SAR
import sys
import logging
import numpy as np
import pandas as pd
# import scrapbook as sb
from sklearn.preprocessing import minmax_scale

app = Flask(__name__)

# Binding config files
app.config.from_object(config)

# connect to mongodb
client = MongoClient('mongodb+srv://rubberduck:la2023@cluster0.mqzk6yg.mongodb.net/?retryWrites=true&w=majority')

# create database "flask.db", just for testing
db = client.project_db
# create a collection "todos", just for testing
student_info = db.studentInfo
studentInfo_test = db.studentInfo_test

@app.route('/')
def hello_world():  # put application's code here
    return redirect(url_for('index'))


@app.route('/index')
def index():
    random_id = ''.join(str(i) for i in random.sample(range(0, 9), 6))
    return render_template("index.html", random_id=random_id)


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/contact')
def contact():
    return render_template("contacts.html")


@app.route('/main_real', methods=('GET', 'POST'))
def main_real():
    result = []
    info = {}
    flag = request.args.get("flag")
    random_id = request.args.get('random_id')
    student_id = None
    if flag:
        student_id = request.args.get('id_student')
        data = student_info.find({"id_student": student_id})
        if data is not None:
            info = list(data)[0]
        else:
            info = {}
    elif request.method == 'POST':
        student_id = request.form['student_id']
        data = student_info.find({"id_student": student_id})

        if data is not None and data != []:
            info = list(data)[0]
        else:
            print(f"-----some thing wrong, nothing be found in database with student_id:{student_id}-----")
            info = {}

    print(f"info is not none:{info}----student_id:{student_id}")
    if info:
        print("-------------------recommendation---------------------------")
        # execute the recommendation model
        courses = ['AAA', 'BBB', 'CCC', 'DDD', 'EEE', 'FFF', 'GGG']
        courses_info = student_info.find({"id_student": int(student_id)}, {"code_module": 1, "_id": 0})
        course_selected = []

        for i in courses_info:
            for v in i.values():
                course_selected.append(v)
        courses_not_selected = list(set(courses) - set(course_selected))

        length = len(courses_not_selected)

        # d = {'id_student': [student_id] * id_length, 'code_module': courses_not_selected}
        # input data
        d = {'id_student': [student_id] * length, 'code_module': courses_not_selected,'weighted_score': [np.nan] * length, 'date_registration': [np.nan] * length}
        input_test = pd.DataFrame(data=d)
        # # take data to df
        cursor = studentInfo_test.find({})

        # # Expand the cursor and construct the DataFrame
        df = pd.DataFrame(list(cursor))
        print(df)
        # Delete the _id
        del df['_id']
        row_length = df.shape[0]
        # df.insert(loc=len(df.columns), column='player', value=player_vals)
        df.insert(loc=len(df.columns), column='date_registration', value=[np.nan]*row_length)
        # df = df.drop_duplicates(subset=['id_student', 'code_moudle'], keep='first')
        # df.weighted_score = df.weighted_score.astype(int)
        print(df.columns)
        filename = 'finalized_model.sav'
        loaded_model = pickle.load(open(filename, 'rb'))
        loaded_model.fit(df)
        # # result
        # result = loaded_model.recommend_k_items(input_test, top_k=3, remove_seen=True)["code_module"][0]
        # print(result)
        result = ['AAA', 'BBB', 'CCC']
    print(f"info:{info}")
    print(f"random_id:{random_id}")
    return render_template("main_real.html", random_id=random_id, info=info, flag=flag, student_id=student_id, result =result)


@app.route('/result_real')
def result_real():
    student_id = request.args.get("student_id")
    result = request.args.getlist("result")
    print(result)
    print(f"result_page-student_id:{student_id}")
    info = {}
    if student_id:
        data = student_info.find({"id_student": student_id})
        if data is not None:
            info = list(data)[0]
        else:
            info = {}
    return render_template("result_real.html", info=info, result=result)


@app.route('/vis_real')
def vis_real():
    first = request.args.get('first')
    print(first)
    if first == 'AAA':
        return redirect(url_for('aaa', year='All'))
    return render_template("vis_real.html")


def get_ageband(age):
    if age >= 35:
        age_band = '35-55'
    elif age >= 55:
        age_band = '55<='
    else:
        age_band = '0-35'
    return age_band


def get_rating(code_module, type_score, code_presentation):
    global rating
    for k,v in type_score.items():
        if k == 'CMA':
            CMA = v
        elif k == 'TMA':
            TMA = v
        elif k == 'EXAM':
            exam = v
    print(f"course:{code_module}:CMA{CMA}-TMA{TMA}-EXAM{exam}")

    if code_module == "AAA":
        rating = CMA * 0.5 + exam * 0.5
    elif code_module == "BBB":
        if code_presentation == '2014J':
            rating = CMA * 0.5 + exam * 0.5
        else:
            rating = CMA * 0.025 + TMA * 0.475 + exam * 0.5
    elif code_module == "CCC":
        rating = CMA * 0.125 + TMA * 0.375 + exam * 0.5
    elif code_module == "DDD":
        if code_presentation == '2014J':
            rating = CMA * 0.125 + TMA * 0.375 + exam * 0.5
        else:
            rating = TMA * 0.5 + exam * 0.5
    elif code_module == "EEE":
        rating = TMA * 0.5 + exam * 0.5
    elif code_module == "EEE":
        rating = exam
    return rating


@app.route('/input_popup', methods=('GET', 'POST'))
def input_popup():
    random_id = request.args.get("random_id")
    info = request.args.get("info")
    # receive data from popup form.
    if request.method == 'POST':

        # receive general information
        student_id = request.form['student_id']
        age = int(request.form['age'])
        age_band = get_ageband(age)
        gender = request.form['gender']
        region = request.form['region']
        education = request.form['highest_education']
        print(f"age:{age}-gender:{gender}-region:{region}-education:{education}")

        # if flag = false means there is no inputting in popup.
        # if flag = True means some information have already been written into database
        flag = False
        # receive course information
        for i in range(1, 8):
            num_code_module = "code_module_" + str(i)
            num_semester = "semester_" + str(i)
            num_assessment_type_1 = "assessment_type_" + str(i) + "_1"
            num_assessment_type_2 = "assessment_type_" + str(i) + "_2"
            num_assessment_type_3 = "assessment_type_" + str(i) + "_3"
            num_score_1 = "score_" + str(i) + "_1"
            num_score_2 = "score_" + str(i) + "_2"
            num_score_3 = "score_" + str(i) + "_3"
            print(f"{num_assessment_type_1}:{num_score_1}")
            print(f"{num_assessment_type_2}:{num_score_2}")
            print(f"{num_assessment_type_3}:{num_score_3}")

            code_module = request.form[num_code_module]
            semester = request.form[num_semester]
            # Each course accepts three assessment_types,score, some of them may be empty if they are not filled in.
            assessment_type_1 = request.form[num_assessment_type_1]
            assessment_type_2 = request.form[num_assessment_type_2]
            assessment_type_3 = request.form[num_assessment_type_3]
            score_1 = request.form[num_score_1]
            score_2 = request.form[num_score_2]
            score_3 = request.form[num_score_3]

            # 需要被计算，然后存进数据库
            print(f"{assessment_type_1}:{score_1}")
            print(f"{assessment_type_2}:{score_2}")
            print(f"{assessment_type_3}:{score_3}")

            assessment_data = [assessment_type_1, assessment_type_2, assessment_type_3]
            score_data = [score_1, score_2, score_3]
            while '' in assessment_data:
                score_data.pop(assessment_data.index(''))
                assessment_data.remove('')
            while '' in score_data:
                assessment_data.pop(score_data.index(''))
                score_data.remove('')
            type_score = {}
            for i in range(len(assessment_data)):
                type_score[assessment_data[i]] = score_data[i]
            print(type_score)
            # for k in type_score.keys():
            #     if k == 'TMA':

            assessment_type = list(set(assessment_data))

            # validation
            print(f"{semester}-{code_module}-{list(set(assessment_type))}")
            if code_module:
                message = validation(code_module, semester, list(set(assessment_type)))
                print(message)
                if message != 'ok':
                    print(f'message:{message}')
                    return render_template('input_popup.html', random_id=student_id, message=message, info=info)

            # 现在需要在循环外面写
            # if course information is not none, then write it into database
            if code_module != '':
                print("insert data into database！")
                student_info.insert_one(
                    {'code_module': code_module, 'code_presentation': semester, 'id_student': student_id,
                     'gender': gender, 'region': region, 'highest_education': education, 'age_band': age_band})
                flag = True

        print(f"student_id:{student_id},{type(student_id)}")
        print(f"random_id:{random_id}")

        return redirect(url_for('main_real', id_student=student_id, flag=flag))
    return render_template('input_popup.html', random_id=random_id, info=info)


@app.route('/changeselectfield/', methods=['GET', 'POST'])
def changeselectfield():
    if request.method == "POST":
        data = request.get_json()
        name = data['name']
        print(name)
        if name == "AAA":
            assessment_type = ['TMA']
        elif name == "BBB":
            assessment_type = ['TMA', 'CMA']
        elif name == "CCC":
            assessment_type = ['TMA', 'CMA', 'EXAM']
        elif name == "DDD":
            assessment_type = ['TMA', 'CMA', 'EXAM']
        elif name == "EEE":
            assessment_type = ['TMA']
        elif name == "FFF":
            assessment_type = ['TMA', 'CMA']
        elif name == "GGG":
            assessment_type = ['TMA', 'CMA']
        else:
            assessment_type = []
        return jsonify(assessment_type)
    else:
        return {}


# just for test how to combine flask and mongodb
# @app.route('/test', methods=('GET', 'POST'))
# def test():
#     if request.method == 'POST':
#         content = request.form['content']
#         degree = request.form['degree']
#         insert data into mongodb
#         todos.insert_one({'content': content, 'degree': degree})
#         return redirect(url_for('test'))
#
#     all_todos = todos.find()
#     return render_template('test.html', todos=all_todos)


# @app.post("/login") is a shortcut for @app.route("/login", methods=["POST"]).
# @app.post('/<id>/delete/')
# def delete(id):
#     items = todos.find({"_id": ObjectId(id)})
#     for data in items:
#         print(data)
#     todos.delete_one({"_id": ObjectId(id)})
#     return redirect(url_for('test'))


@app.route('/overview')
def overview():
    year = request.args.get('plot')
    return render_template('overview.html', year=year)


@app.route('/aaa')
def aaa():
    year = request.args.get('plot')
    return render_template('AAA.html', year=year)

@app.route('/test1')
def test1():
    return render_template('test1.html')


def validation(course, semester, assessment_type):
    if course == 'AAA' and semester in ['2013J', '2014J'] and sorted(assessment_type) == sorted(['TMA']):
        message = 'ok'
    elif course == 'BBB' and semester in ['2013B', '2013J', '2014B'] and sorted(assessment_type) == sorted(
            ['TMA', 'CMA']):
        message = 'ok'
    elif course == 'BBB' and semester in ['2014J'] and sorted(assessment_type) == sorted(['TMA']):
        message = 'ok'
    elif course == 'CCC' and semester in ['2014B', '2014J'] and sorted(assessment_type) == sorted(
            ['CMA', 'TMA', 'EXAM']):
        message = 'ok'
    elif course == 'DDD' and semester in ['2014J', '2013J', '2014B'] and sorted(assessment_type) == sorted(
            ['TMA', 'EXAM']):
        message = 'ok'
    elif course == 'DDD' and semester in ['2013B'] and sorted(assessment_type) == sorted(['TMA', 'CMA', 'EXAM']):
        message = 'ok'
    elif course == 'EEE' and semester in ['2013J', '2013B', '2014J', '2014B'] and sorted(assessment_type) == sorted(
            ['TMA']):
        message = 'ok'
    elif course == 'FFF' and semester in ['2013J', '2013B', '2014J', '2014B'] and sorted(assessment_type) == sorted(
            ['TMA', 'CMA']):
        message = 'ok'
    elif course == 'GGG' and semester in ['2013J', '2014J', '2014B'] and sorted(assessment_type) == sorted(
            ['TMA', 'CMA']):
        message = 'ok'
    else:
        message = f"the course {course} information is incorrectly! Please check the semester information and " \
                  f"assessment_type carefully. "
    return message


def get_rating():
    print("rating")


if __name__ == '__main__':
    app.run()
