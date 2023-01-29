import pickle
import random
from flask import Flask, render_template, redirect, url_for, request, jsonify
from pymongo import MongoClient
# this is the objectID() class you'll use to convert string IDs to ObjectID objects.
import pandas as pd
import config

app = Flask(__name__)

# Binding config files
app.config.from_object(config)

# connect to mongodb
client = MongoClient('mongodb+srv://rubberduck:la2023@cluster0.mqzk6yg.mongodb.net/?retryWrites=true&w=majority')

# create database "flask.db", just for testing
db = client.project_db
# create a collection "todos", just for testing
student_info = db.studentInfo


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
    info = {}
    flag = request.args.get("flag")
    random_id = request.args.get('random_id')
    student_id = None
    print(f"flag: {flag}")
    if flag:
        student_id = request.args.get('id_student')
        data = student_info.find({"id_student": int(student_id)})
        if data is not None:
            info = list(data)[0]
        else:
            info = {}
    elif request.method == 'POST':
        student_id = request.form['student_id']
        data = student_info.find({"id_student": int(student_id)})
        if data is not None and data !=[]:
            info = list(data)[0]
            print(f"+++++++{type(info['id_student'])}")
        else:
            print(f"-------")
            info = {}

    if info:
        # execute the recommendation model
        # d = {'id_student': [80329], 'code_module': ['AAA']}
        # input_test = pd.DataFrame(data=d)
        # filename = 'finalized_model.sav'
        # loaded_model = pickle.load(open(filename, 'rb'))
        # result = loaded_model.recommend_k_items(input_test, top_k=3, remove_seen=True)["code_module"][0]
        # print(result)
        print("recommendation")
    print(f"info:{info}")
    print(f"random_id:{random_id}")
    return render_template("main_real.html", random_id=random_id, info=info, flag=flag, student_id=student_id)


@app.route('/result_real')
def result_real():
    student_id = request.args.get("student_id")

    print(f"result_page-student_id:{student_id}")
    info={}
    if student_id:
        data = student_info.find({"id_student": int(student_id)})
        if data is not None:
            info = list(data)[0]
        else:
            info = {}
    return render_template("result_real.html", info=info)


@app.route('/vis_real')
def vis_real():
    return render_template("vis_real.html")


@app.route('/input_popup', methods=('GET', 'POST'))
def input_popup():
    random_id = request.args.get("random_id")
    info = request.args.get("info")
    # receive data from popup form.
    if request.method == 'POST':
        courses = []

        # receive general information
        student_id = request.form['student_id']
        age = int(request.form['age'])
        age_band = '0-35'
        # convert age to '0-35','35-55','55<='
        if age >= 35:
            age_band = '35-55'
        elif age >= 55:
            age_band = '55<='
        gender = request.form['gender']
        region = request.form['region']
        education = request.form['highest_education']
        print(f"age:{age}-gender:{gender}-region:{region}-education:{education}")

        # if flag = false means there is no inputting in popup.
        # if flag = True means some information have already been written into database
        flag = False
        # receive course information
        for i in range(1, 8):
            course = {}

            num_code_module = "code_module_" + str(i)
            num_semester = "semester_" + str(i)
            num_assessment_type_1 = "assessment_type_" + str(i)+"_1"
            num_assessment_type_2 = "assessment_type_" + str(i)+"_2"
            num_assessment_type_3 = "assessment_type_" + str(i)+"_3"
            num_score_1= "score_" + str(i)+"_1"
            num_score_2 = "score_" + str(i) + "_2"
            num_score_3 = "score_" + str(i) + "_3"
            print(f"{num_assessment_type_1}:{num_score_1}")
            print(f"{num_assessment_type_2}:{num_score_2}")
            print(f"{num_assessment_type_3}:{num_score_3}")

            # Each course accepts three assessment_types,score, some of them may be empty if they are not filled in.
            assessment_type_1 = request.form[num_assessment_type_1]
            assessment_type_2 = request.form[num_assessment_type_2]
            assessment_type_3 = request.form[num_assessment_type_3]
            score_1 = request.form[num_score_1]
            score_2 = request.form[num_score_2]
            score_3 = request.form[num_score_3]
            print(f"{assessment_type_1}:{score_1}")
            print(f"{assessment_type_2}:{score_2}")
            print(f"{assessment_type_3}:{score_3}")

            code_module = request.form[num_code_module]
            semester = request.form[num_semester]

            # if course information is not none, then write it into database
            if code_module != '':
                print("insert data into database！")
                student_info.insert_one(
                    {'conde_module': code_module, 'code_presentation': semester, 'id_student': int(student_id),
                     'gender': gender, 'region': region, 'highest_education': education, 'age_band': age_band})
                flag = True
            # course['code_module'] = code_module
            # course['assessment_type'] = assessment_type
            # course['score'] = score
            # course['semester'] = semester
            #
            # courses.append(course)
        print(f"student_id:{student_id},{type(student_id)}")
        print(f"random_id:{random_id}")
        for item in courses:
            print(item)
        return redirect(url_for('main_real', id_student=student_id, flag=flag))
    return render_template('input_popup.html', random_id=random_id, info=info)


@app.route('/changeselectfield/', methods=['GET', 'POST'])
def changeselectfield():
    if request.method == "POST":
        data = request.get_json()
        name = data['name']
        print(name)
        if name == "AAA":
            assessment_type = ['TMA', 'CMA']
        elif name == "BBB":
            assessment_type = ['TMA', 'CMA', 'Exam']
        else:
            assessment_type =[]
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


@app.route('/test1')
def test1():
    return render_template('test1.html')


if __name__ == '__main__':
    app.run()
