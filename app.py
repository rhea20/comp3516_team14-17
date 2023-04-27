import os
from flask import Flask, request, redirect, url_for, render_template, send_from_directory
from werkzeug.utils import secure_filename
import cv2
from PyPDF2 import PdfReader, PdfWriter
import filecmp
from fpdf import FPDF
import textwrap
from PIL import Image
import base64
import qrcode
from pyzbar.pyzbar import decode as zbar_decode
import time

SENDER_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/sender/'
RECEIVER_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/receiver/'
ALLOWED_EXTENSIONS = {'png', 'txt', 'jpeg', 'jpg', 'tiff', 'pdf'}
main_dir = "C:/Users/ASUS/Desktop/y4s2/iot/group_project/QRCode_FileTransfer_API/"
app = Flask(__name__, static_url_path="/static")
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
app.config['SENDER_FOLDER'] = SENDER_FOLDER
app.config['RECEIVER_FOLDER'] = RECEIVER_FOLDER
# limit upload size upto 8mb
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024

#upload image and encode to QR in this path: http://127.0.0.1:5000/
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
            pre_encoding = time.time()
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['SENDER_FOLDER'], 'to_encode' + filename[filename.rfind('.'):]))
            process_file(os.path.join(app.config['SENDER_FOLDER'], filename), filename, pre_encoding)
            return redirect(url_for('uploaded_file', filename=filename))
    return render_template('index.html')

#upload QR code(s) and decode the file in this path: http://127.0.0.1:5000/scanner
@app.route('/scanner', methods=['GET', 'POST'])
def scanner():
    if request.method == 'POST':
        # check if the post request has multiple files
        if 'files[]' not in request.files:
            print('No file attached in request')
            return redirect(request.url)

        files = request.files.getlist('files[]')
        pre_decoding = time.time()
        for file in files:
            if file.filename == '':
                print('No file selected')
                return redirect(request.url)

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['SENDER_FOLDER'], filename))
                process_QR(os.path.join(app.config['SENDER_FOLDER'], filename), filename, pre_decoding)
                break

        return redirect(url_for('uploaded_file', filename='qrcode.png'))
    return render_template('scanner.html')


@app.route('/sender/<filename>')
def uploaded_file(filename):
    qrcode = os.path.join(app.config['SENDER_FOLDER'], filename)
    return render_template("qrcode.html", user_image=qrcode)
    return send_from_directory(app.config['RECEIVER_FOLDER'], filename, as_attachment=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#function to process uploaded file and encode into QR code
def process_file(path, filename, pre_encoding):
    if 'txt' in filename:
        input_file = open(path, 'rb')
        data = input_file.read() + '.txt'.encode('utf-8')
        img = qrcode.make(data)
        img.save(os.path.join(app.config['SENDER_FOLDER'], 'qrcode.png'))

    elif 'pdf' in filename:
        pdf_file = open(path, 'rb')
        pdf_reader = PdfReader(pdf_file)
        # Get the first page of the PDF file
        page = pdf_reader.pages[0]
        # Extract the text from the page
        data = bytes(page.extract_text(), 'utf-8') + '.pdf'.encode('utf-8')
        img = qrcode.make(data)
        img.save(os.path.join(app.config['SENDER_FOLDER'], 'qrcode.png'))

    else:
        img_dir = os.path.join(path)
        print(img_dir)
        encoded_image_prefix = "encoded_image"
        # Encode image as base64 and create QR codes
        base64_str = image_to_base64(img_dir)
        create_qrcodes(base64_str, encoded_image_prefix)
    print(f'Encoding time: {time.time() - pre_encoding}')


#function to decode QR code according to file type
def process_QR(path, filename, pre_decoding):
    path1 = os.path.join(path)
    image = cv2.imread(path1)
    decoded_qr = zbar_decode(image)
    decoded = (decoded_qr[0].data).decode('utf-8')
    ext_index = decoded.rfind('.')
    extension = decoded[ext_index:]
    decoded = decoded[:ext_index]
    dir = f'C:/Users/ASUS/Desktop/y4s2/iot/group_project/QRCode_FileTransfer_API/receiver/decoded_{extension[1:]}{extension}'

    if extension == '.pdf':
        a4_width_mm = 210
        pt_to_mm = 0.35
        character_width_mm = 7 * pt_to_mm
        width_text = a4_width_mm / character_width_mm
        fontsize_pt = 10
        margin_bottom_mm = 10
        fontsize_mm = fontsize_pt * pt_to_mm

        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.set_auto_page_break(True, margin=margin_bottom_mm)
        pdf.add_page()
        pdf.set_xy(0, 0)
        pdf.set_font('helvetica', size=11.0)

        split = decoded.split('\n')
        for line in split:
            lines = textwrap.wrap(line, width_text)
            if len(lines) == 0:
                pdf.ln()
            for wrap in lines:
                pdf.cell(0, fontsize_mm, wrap, ln=1)

        pdf.output(dir, 'F')

    elif extension == '.txt':
        with open(dir, 'w') as f:
            f.write(decoded)

    else:
        encoded_image_prefix = "encoded_image"
        encoded_dir = 'C:/Users/ASUS/Desktop/y4s2/iot/group_project/QRCode_FileTransfer_API/sender/'
        num_qrcodes = len([name for name in os.listdir(encoded_dir) if name.startswith(encoded_image_prefix)])
        # Decode QR codes and save the image
        decoded_base64_str = decode_qrcodes(encoded_image_prefix, num_qrcodes, encoded_dir)
        base64_to_image(decoded_base64_str, f'{main_dir}receiver/decoded_jpeg.jpeg')

    print(f'Decoding time: {time.time() - pre_decoding}')


#functions to encode and decode image files
def image_to_base64(img_path):
    with open(img_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

def base64_to_image(base64_str, img_path):
    img_data = base64.b64decode(base64_str)
    with open(img_path, 'wb') as img_file:
        img_file.write(img_data)

def create_qrcodes(data, qr_prefix):
    chunk_size = 2500
    chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

    for i, chunk in enumerate(chunks):
        qr = qrcode.QRCode(
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(chunk)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(os.path.join(app.config['SENDER_FOLDER'], f"{qr_prefix}_{i}.png"))

def decode_qrcodes(qr_prefix, num_qrcodes, qr_dir):
    decoded_data = ""
    for i in range(num_qrcodes):
        qr_path = f"{qr_dir}{qr_prefix}_{i}.png"
        decoded_chunk = zbar_decode(Image.open(qr_path))
        if decoded_chunk:
            decoded_data += decoded_chunk[0].data.decode('utf-8')
        else:
            raise ValueError(f"No QR code found in the image {qr_path}")
    return decoded_data

#driver function
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

