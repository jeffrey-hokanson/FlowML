#! /opt/local/bin/python
from flask import Flask, render_template
app = Flask(__name__)

#@app.route('/hello/')
#@app.route('/hello/<name>/')
#def hello():
#	return render_template('hello.html', name=name)

@app.route('/')
def landing():
	return render_template('landing.html')

@app.route('/visne')
def visne():
	return render_template('visne.html')

if __name__ == '__main__':
	app.run()
