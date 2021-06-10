import os
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename

app = Flask(__name__,template_folder='templates')


@app.route('/')
def upload_file():
    return render_template('index.html')

app.config['UPLOAD_FOLDER'] = '/Users/aryantaneja/Desktop/Web_Development/flask/templates'
@app.route('/uploader', methods=['GET', 'POST'])
def uploader():
    if request.method=='POST':
        f = request.files['file1']
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
        return "Uploaded successfully!"


if __name__ == '__main__':
    app.run(debug=True)