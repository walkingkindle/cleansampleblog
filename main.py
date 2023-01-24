import flask
from flask import Flask
import requests


app = Flask(__name__)
url="https://api.npoint.io/93f14c94fb7ca980d04a"
response = requests.get(url=url).json()
number = 0

@app.route('/')
def welcome_page():
    return flask.render_template('index.html',response=response,number=number)
@app.route('/about')
def to_about():
    return flask.render_template('about.html')
@app.route('/contact')
def contact():
    return flask.render_template('contact.html')
@app.route('/post/<int:index>')
def show_post(index):
    url = "https://api.npoint.io/93f14c94fb7ca980d04a"
    response = requests.get(url=url).json()
    return flask.render_template('post.html',response=response,index=int(index))

if __name__ == "__main__":
    app.run(debug=True)
