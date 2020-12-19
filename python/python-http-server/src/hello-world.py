from flask import Flask
import time

app = Flask(__name__)

@app.route('/')
def index():
    return "<span style='color:red'>Hello world!</span>"

@app.route('/slow')
def slow():
    app.logger.info('Start an extremly slow request... sleep for 180 seconds')
    time.sleep(180)
    return "<span style='color:red'>I'm lazy!</span>"