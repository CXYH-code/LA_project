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
student_info = db.studentInfo_testv3


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

    # print(f"info is not none:{info}----student_id:{student_id}")
    # if info:
        # print("-------------------recommendation---------------------------")
        # # execute the recommendation model
        # courses = ['AAA', 'BBB', 'CCC', 'DDD', 'EEE', 'FFF', 'GGG']
        # courses_info = student_info.find({"id_student": student_id}, {"code_module": 1, "_id": 0})
        #
        # course_selected = list()
        # print(f"selectd:{courses_info}")
        # for i in courses_info:
        #     for v in i.values():
        #         if type(v) == list:
        #             course_selected = v
        #         else:
        #             v = v[1:-1].replace("'", "").replace("[", "").replace("]", "")
        #             course_selected.append(v)
        # #print(f"course_selected:{course_selected}")
        # courses_not_selected = [x for x in courses if x not in course_selected]
        # #print(f"courses_not_selected:{courses_not_selected}")
        # length = len(courses_not_selected)
        # d = {'id_student': [str(student_id)] * length, 'code_module': courses_not_selected,
        #      'weighted_score': [np.nan] * length, 'date_registration': [0] * length}
        #
        # input_test = pd.DataFrame(data=d)
        #
        # # # take data to df
        # cursor = studentInfo_test.find({})
        # # # Expand the cursor and construct the DataFrame
        # df = pd.DataFrame(list(cursor))
        # # Delete the _id
        # del df['_id']
        # row_length = df.shape[0]
        # df = df[["id_student", "code_module", "weighted_score", "date_registration"]]
        #
        # # clean df file
        # print(df.code_module)
        # print(df.id_student)
        # df.code_module = df.code_module.apply(lambda x: x[1:-1].replace("'", "").split(","))
        # df.weighted_score = df.weighted_score.apply(lambda x: x[1:-1].replace("'", "").split(","))
        # df = df.explode("code_module")
        # df = df.explode("weighted_score")
        # df = df.drop_duplicates(subset=['id_student', 'code_module'], keep='first')
        # df.weighted_score = df.weighted_score.apply(lambda x: int(float(x)))
        # df.date_registration = df.date_registration.apply(lambda x: int(float(x)))
        # df = df[df["weighted_score"]!=0].dropna(subset = ["weighted_score"])
        #
        #
        # model = SAR(
        #     col_user="id_student",
        #     col_item="code_module",
        #     col_rating="weighted_score",
        #     col_timestamp="date_registration",
        #     similarity_type="jaccard",
        #     time_decay_coefficient=30,
        #     timedecay_formula=True,
        #     normalize=True
        # )
        #
        # model.fit(df)
        #
        # result = model.recommend_k_items(pd.DataFrame(d), remove_seen=True)
        # print("kkkkk")
        # print(result)
        # result = result[result.code_module.isin(courses_not_selected) ]
        # print(result)
        # result = result["code_module"].tolist()
        # print(result)
        # print(f"===============result:{result}")

    print(f"random_id:{random_id}")
    return render_template("main_real.html", random_id=random_id, info=info, flag=flag, student_id=student_id,
                           result=result)


@app.route('/result_real')
def result_real():
    result = ''
    student_id = request.args.get("student_id")

    print(request.args.get('info'))
    print(f"result_page-student_id:{student_id}")
    info = {}
    if student_id:
        data = student_info.find({"id_student": student_id})
        if data is not None:
            info = list(data)[0]
        else:
            info = {}
    if info:
        print("-------------------recommendation---------------------------")
        # execute the recommendation model
        courses = ['AAA', 'BBB', 'CCC', 'DDD', 'EEE', 'FFF', 'GGG']
        courses_info = student_info.find({"id_student": student_id}, {"code_module": 1, "_id": 0})

        course_selected = list()
        print(f"selectd:{courses_info}")
        for i in courses_info:
            for v in i.values():
                if type(v) == list:
                    course_selected = v
                else:
                    v = v[1:-1].replace("'", "").replace("[", "").replace("]", "")
                    course_selected.append(v)
        #print(f"course_selected:{course_selected}")
        courses_not_selected = [x for x in courses if x not in course_selected]
        #print(f"courses_not_selected:{courses_not_selected}")
        length = len(courses_not_selected)
        d = {'id_student': [str(student_id)] * length, 'code_module': courses_not_selected,
             'weighted_score': [np.nan] * length, 'date_registration': [0] * length}

        input_test = pd.DataFrame(data=d)

        # # take data to df
        cursor = student_info.find({})
        # # Expand the cursor and construct the DataFrame
        df = pd.DataFrame(list(cursor))
        print( df[df["id_student"]==student_id])
        # Delete the _id
        del df['_id']
        row_length = df.shape[0]
        df = df[["id_student", "code_module", "weighted_score", "date_registration"]]

        # clean df file
        print(df.code_module)
        print(df.id_student)
        df.code_module = df.code_module.apply(lambda x: x[1:-1].replace("'", "").split(","))
        df.weighted_score = df.weighted_score.apply(lambda x: x[1:-1].replace("'", "").split(","))
        df = df.explode("code_module")
        df = df.explode("weighted_score")
        df = df.drop_duplicates(subset=['id_student', 'code_module'], keep='first')
        df.weighted_score = df.weighted_score.apply(lambda x: int(float(x)))
        df.date_registration = df.date_registration.fillna(0)
        df.date_registration = df.date_registration.apply(lambda x: int(float(x)))
        df = df[df["weighted_score"]!=0].dropna(subset = ["weighted_score"])
        print(df)
        model = SAR(
            col_user="id_student",
            col_item="code_module",
            col_rating="weighted_score",
            col_timestamp="date_registration",
            similarity_type="jaccard",
            time_decay_coefficient=30,
            timedecay_formula=True,
            normalize=True
        )

        model.fit(df)

        result = model.recommend_k_items(pd.DataFrame(d), remove_seen=True)
        print("kkkkk")
        print(result)
        result = result[result.code_module.isin(courses_not_selected) ]
        print(result)
        result = result["code_module"].tolist()
        print(result)
        print(f"===============result:{result}")
    return render_template("result_real.html", info=info, result=result)


@app.route('/vis_real')
def vis_real():
    first = request.args.get('first')
    print(first)
    if first == 'AAA':
        return redirect(url_for('aaa', year='All'))
    elif first == 'BBB':
        return redirect(url_for('bbb', year='All'))
    elif first == 'CCC':
        return redirect(url_for('ccc', year='All'))
    elif first == 'DDD':
        return redirect(url_for('ddd', year='All'))
    elif first == 'EEE':
        return redirect(url_for('eee', year='All'))
    elif first == 'FFF':
        return redirect(url_for('fff', year='All'))
    else:
        return redirect(url_for('ggg', year='All'))


def get_ageband(age):
    if age >= 35:
        age_band = '35-55'
    elif age >= 55:
        age_band = '55<='
    else:
        age_band = '0-35'
    return age_band


def get_rating(code_module, type_score, code_presentation):
    global rating, CMA, TMA, exam
    for k, v in type_score.items():
        if k == 'CMA':
            print(f"CMA{v}")
            CMA = int(v)
        elif k == 'TMA':
            print(f"TMA:{v}")
            TMA = int(v)
        elif k == 'EXAM':
            print(f"EXAM:{v}")
            exam = int(v)

    if code_module == "AAA":
        rating = TMA * 0.5 + exam * 0.5
    elif code_module == "BBB":
        if code_presentation == '2014J':
            rating = TMA * 0.5 + exam * 0.5
        else:
            rating = CMA * 0.025 + TMA * 0.475 + exam * 0.5
    elif code_module == "CCC":
        rating = (CMA * 0.125 + TMA * 0.375) * 2 / 3 + exam * 0.66
    elif code_module == "DDD":
        if code_presentation == '2013B':
            rating = CMA * 0.125 + TMA * 0.375 + exam * 0.5
        else:
            rating = TMA * 0.5 + exam * 0.5
    elif code_module == "EEE":
        rating = TMA * 0.5 + exam * 0.5
    elif code_module == "FFF":
        rating = TMA * 0.5 + exam * 0.5
    elif code_module == "GGG":
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
        courses = []
        ratings = []
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
            assessment_data = [assessment_type_1, assessment_type_2, assessment_type_3]
            score_data = [score_1, score_2, score_3]
            if code_module:
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
                rating = get_rating(code_module, type_score, semester)
                print(f"course:{code_module}-rating:{rating}")
                courses.append(code_module)
                ratings.append(rating)
            # validation
            assessment_type = list(set(assessment_data))
            if code_module:
                message = validation(code_module, semester, list(set(assessment_type)))
                print(f"validation: {message}")
                if message != 'ok':
                    print(f'message:{message}')
                    return render_template('input_popup.html', random_id=student_id, message=message, info=info)

        # if course information is not none, then write it into database
        print(f"courses:{courses}")
        print(f"ratings:{ratings}")
        if courses:
            print("insert data into database！")
            student_info.insert_one(
                {'id_student': student_id,
                 'code_module': str(courses),
                 'weighted_score': str(ratings),
                 'highest_education': education,
                 'region': region,
                 'age_band': age_band,
                 'gender': gender,
                 'date_registration' : "0.0"})
            flag = True
        print(f"student_id:{student_id}")
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
            assessment_type = ['TMA', 'EXAM']
        elif name == "BBB":
            assessment_type = ['TMA', 'CMA', 'EXAM']
        elif name == "CCC":
            assessment_type = ['TMA', 'CMA', 'EXAM']
        elif name == "DDD":
            assessment_type = ['TMA', 'CMA', 'EXAM']
        elif name == "EEE":
            assessment_type = ['TMA', 'EXAM']
        elif name == "FFF":
            assessment_type = ['TMA', 'CMA', 'EXAM']
        elif name == "GGG":
            assessment_type = ['TMA', 'CMA', 'EXAM']
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


@app.route('/bbb')
def bbb():
    year = request.args.get('plot')
    return render_template('BBB.html', year=year)


@app.route('/ccc')
def ccc():
    year = request.args.get('plot')
    return render_template('CCC.html', year=year)


@app.route('/ddd')
def ddd():
    year = request.args.get('plot')
    return render_template('DDD.html', year=year)


@app.route('/eee')
def eee():
    year = request.args.get('plot')
    return render_template('EEE.html', year=year)


@app.route('/fff')
def fff():
    year = request.args.get('plot')
    return render_template('FFF.html', year=year)


@app.route('/ggg')
def ggg():
    year = request.args.get('plot')
    return render_template('GGG.html', year=year)


@app.route('/test1')
def test1():
    return render_template('test1.html')


def validation(course, semester, assessment_type):
    if course == 'AAA' and semester in ['2013J', '2014J'] and sorted(assessment_type) == sorted(['TMA', 'EXAM']):
        message = 'ok'
    elif course == 'BBB' and semester in ['2013B', '2013J', '2014B'] and sorted(assessment_type) == sorted(
            ['TMA', 'CMA', 'EXAM']):
        message = 'ok'
    elif course == 'BBB' and semester in ['2014J'] and sorted(assessment_type) == sorted(['TMA', 'EXAM']):
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
            ['TMA', 'EXAM']):
        message = 'ok'
    elif course == 'FFF' and semester in ['2013J', '2013B', '2014J', '2014B'] and sorted(assessment_type) == sorted(
            ['TMA', 'CMA', 'EXAM']):
        message = 'ok'
    elif course == 'GGG' and semester in ['2013J', '2014J', '2014B'] and sorted(assessment_type) == sorted(
            ['TMA', 'CMA', 'EXAM']):
        message = 'ok'
    else:
        message = f"the course {course} information is incorrectly! Please check the semester information and " \
                  f"assessment_type carefully. "
    return message


@app.route('/classes')
def classes():
    return render_template('classes.html')


@app.route('/staff')
def staff():
    return render_template('staff.html')


if __name__ == '__main__':
    app.run()
