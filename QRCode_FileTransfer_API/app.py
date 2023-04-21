import os
from flask import Flask, request, redirect, url_for, render_template, send_from_directory
from werkzeug.utils import secure_filename
# from PyPDF2 import PdfFileReader, PdfFileWriter
import qrcode
import cv2
import numpy as np
import io
from PIL import Image
from pyzbar.pyzbar import decode

UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/uploads/'
DOWNLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/downloads/'
ALLOWED_EXTENSIONS = {'png', 'txt', 'jpeg', 'tiff', 'pdf'}

app = Flask(__name__, static_url_path="/static")
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
# limit upload size upto 8mb
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            print('No file attached in request')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            print('No file selected')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            process_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), filename)
            return redirect(url_for('uploaded_file', filename='qrcode.png'))
    return render_template('index.html')


@app.route('/scanner', methods=['GET', 'POST'])
def scanner():
    if request.method == 'POST':
        if 'file' not in request.files:
            print('No file attached in request')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            print('No file selected')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            process_QR(os.path.join(app.config['UPLOAD_FOLDER'], filename), filename)
            return redirect(url_for('uploaded_file', filename='qrcode.png'))
    return render_template('scanner.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    qrcode = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return render_template("qrcode.html", user_image=qrcode)
    # return send_from_directory(app.config['DOWNLOAD_FOLDER'], 'tempt.txt', as_attachment=True)

def process_file(path, filename):
    if 'txt' in filename:
        input_file = open(path, 'rb')
        data = input_file.read()
        img = qrcode.make(data)
        img.save(os.path.join(app.config['UPLOAD_FOLDER'], f'qrcode.png'))
    # if 'png' in filename:
    #     path1 = os.path.join(path)
    #     print(path1)
    #     print(type(path1))
    #     img = cv2.imread(path1)
    #     all_pixels = img.reshape((-1, 3))
    #     nptext_dir = 'C:\\Users\\ASUS\\Desktop\\y4s2\\iot\\group_project\\QRCode_FileTransfer_API\\uploads\\imgtxt.txt'
    #     print(nptext_dir)
    #     np.savetxt(nptext_dir, all_pixels, fmt='%d')
    #     print("saves txt file")
    #     input_file2 = open(nptext_dir, 'rb')
    #     data = input_file2.read()
    #     img = qrcode.make(data)
    #     img.save(os.path.join(app.config['UPLOAD_FOLDER'], f'qrcode2.png'))


def process_QR(path, filename):
    path1 = os.path.join(path)
    image = cv2.imread(path1)
    decoded_qr = decode(image)
    decoded = (decoded_qr[0].data).decode('utf-8')
    dir = 'C:\\Users\\ASUS\\Desktop\\y4s2\\iot\\group_project\\QRCode_FileTransfer_API\\downloads\\decoded.txt'
    with open(dir, 'w') as f:
        # Write the string to the file
        f.write(decoded)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
