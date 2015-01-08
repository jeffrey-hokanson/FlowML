#! /opt/local/bin/python
# Flask server script


# This follows large portions of the jQuery-File-Upload project
# https://github.com/blueimp/jQuery-File-Upload
# and the corresponding flask code:
# https://github.com/ngoduykhanh/flask-file-uploader

import os

from flask import Flask, request, render_template, session, redirect, url_for, flash, send_from_directory
from flask.ext.bootstrap import Bootstrap
import simplejson
import traceback
from werkzeug import secure_filename


from lib.upload_file import uploadfile

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['UPLOAD_FOLDER'] = 'data/'
app.config['THUMBNAIL_FOLDER'] = 'data/thumbnail/'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
bootstrap = Bootstrap(app)

ALLOWED_EXTENSIONS = set(['fcs'])
IGNORED_FILES = set(['.gitignore'])

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def gen_file_name(filename):
    """
    If file was exist already, rename it and return a new name
    """

    i = 1
    while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
        name, extension = os.path.splitext(filename)
        filename = '%s_%s%s' % (name, str(i), extension)
        i = i + 1

    return filename

@app.route("/upload", methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        #pprint (vars(objectvalue))

        if file:
            filename = secure_filename(file.filename)
            filename = gen_file_name(filename)
            mimetype = file.content_type


            if not allowed_file(file.filename):
                result = uploadfile(name=filename, type=mimetype, size=0, not_allowed_msg="Filetype not allowed")

            else:
                # save file to disk
                uploaded_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(uploaded_file_path)

                # get file size after saving
                size = os.path.getsize(uploaded_file_path)

                # return json for js call back
                result = uploadfile(name=filename, type=mimetype, size=size)
            
            return simplejson.dumps({"files": [result.get_file()]})

    if request.method == 'GET':
        # get all file in ./data directory
        files = [ f for f in os.listdir(app.config['UPLOAD_FOLDER']) if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'],f)) and f not in IGNORED_FILES ]
        
        file_display = []

        for f in files:
            size = os.path.getsize(os.path.join(app.config['UPLOAD_FOLDER'], f))
            file_saved = uploadfile(name=f, size=size)
            file_display.append(file_saved.get_file())

        return simplejson.dumps({"files": file_display})

    return redirect(url_for('visne'))


@app.route("/delete/<string:filename>", methods=['DELETE'])
def delete(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    #file_thumb_path = os.path.join(app.config['THUMBNAIL_FOLDER'], filename)

    if os.path.exists(file_path):
        try:
            os.remove(file_path)

            #if os.path.exists(file_thumb_path):
            #    os.remove(file_thumb_path)
            
            return simplejson.dumps({filename: 'True'})
        except:
            return simplejson.dumps({filename: 'False'})

	


@app.route("/data/<string:filename>", methods=['GET'])
def get_file(filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER']), filename=filename)


@app.route("/run-tsne", methods = ['POST', 'GET'])
def run():
	"""Run t-SNE
	"""
	filename = os.path.join(app.config['UPLOAD_FOLDER'],'test')
	
	if request.method == 'POST':
		f = open(filename, 'w')
		f.write('Hello')
		f.close()
	return redirect(url_for('visne'))
				

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/visne', methods = ['GET', 'POST'])
def visne():
	return render_template('visne.html')

if __name__ == '__main__':
	app.run()
