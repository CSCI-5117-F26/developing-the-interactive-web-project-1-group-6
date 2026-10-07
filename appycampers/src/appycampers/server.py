from flask import Flask, render_template

app = Flask(__name__)

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/explore")
def explore():
    return render_template("index.html")

@app.get("/my_camps")
def my_camps():
    return render_template("index.html")

@app.get("/login")
def login():
    return render_template("index.html")

@app.get("/create_camp")
def create_camp():
    return render_template("index.html")