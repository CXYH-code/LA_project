import random
from flask import Flask, render_template, redirect, url_for, request
from pymongo import MongoClient
# this is the objectID() class you'll use to convert string IDs to ObjectID objects.
from bson.objectid import ObjectId
import config

app = Flask(__name__)

# Binding config files
app.config.from_object(config)

# connect to mongodb
client = MongoClient('localhost', 27017)

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
        if data is not None:
            info = list(data)[0]
            print(f"+++++++{type(info['id_student'])}")
        else:
            print(f"-------")
            info = {}
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
            num_assessment_type = "assessment_type_" + str(i)
            num_score = "score_" + str(i)
            num_semester = "semester_" + str(i)

            assessment_type = request.form[num_assessment_type]
            code_module = request.form[num_code_module]
            score = request.form[num_score]
            semester = request.form[num_semester]

            # if course information is not none, then write it into database
            if code_module != '':
                print("insert data into database！")
                student_info.insert_one(
                    {'conde_module': code_module, 'code_presentation': semester, 'id_student': int(student_id),
                     'gender': gender, 'region': region, 'highest_education': education, 'age_band': age_band})
                flag = True
            course['code_module'] = code_module
            course['assessment_type'] = assessment_type
            course['score'] = score
            course['semester'] = semester

            courses.append(course)
        print(f"student_id:{student_id},{type(student_id)}")
        print(f"random_id:{random_id}")
        for item in courses:
            print(item)
        return redirect(url_for('main_real', id_student=student_id, flag=flag))
    return render_template('input_popup.html', random_id=random_id, info=info)


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
