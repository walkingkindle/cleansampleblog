import flask
from flask import Flask
import requests
from flask import request
import smtplib



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

@app.route('/form-entry',methods = ['POST','GET'])
def receive_data():
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email-address']
        phone = request.form['phone-number']
        message = request.form['message']
        user = [username, email, phone, message]
        print(user)
        my_email = "YOUR EMAIL HERE"
        my_password = "YOUR PASSWORD HERE"
        connection = smtplib.SMTP("smtp.gmail.com",timeout=120,port=587)
        connection.starttls()
        connection.login(user=my_email,password=my_password)
        connection.sendmail(from_addr=my_email,to_addrs=email,msg=message)
        connection.close()
        return flask.render_template('contact.html',msg_sent=True)
    return flask.render_template('contact.html',msg_sent=False)



if __name__ == "__main__":
    app.run(debug=True)
