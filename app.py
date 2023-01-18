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
db = client.flask_db
# create a collection "todos", just for testing
todos = db.todos


@app.route('/')
def hello_world():  # put application's code here
    return redirect(url_for('index'))


@app.route('/index')
def index():
    return render_template("index.html")


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/contact')
def contact():
    return render_template("contacts.html")


@app.route('/main_real')
def main_real():
    return render_template("main_real.html")


@app.route('/result_real')
def result_real():
    return render_template("result_real.html")


@app.route('/vis_real')
def vis_real():
    return render_template("vis_real.html")


@app.route('/input_popup')
def input_popup():
    return render_template("input_popup.html")


# just for test how to combine flask and mongodb
@app.route('/test', methods=('GET', 'POST'))
def test():
    if request.method == 'POST':
        content = request.form['content']
        degree = request.form['degree']
        # insert data into mongodb
        todos.insert_one({'content': content, 'degree': degree})
        return redirect(url_for('test'))

    all_todos = todos.find()
    return render_template('test.html', todos=all_todos)


# @app.post("/login") is a shortcut for @app.route("/login", methods=["POST"]).
@app.post('/<id>/delete/')
def delete(id):
    items = todos.find({"_id": ObjectId(id)})
    for data in items:
        print(data)
    todos.delete_one({"_id": ObjectId(id)})
    return redirect(url_for('test'))


if __name__ == '__main__':
    app.run()
