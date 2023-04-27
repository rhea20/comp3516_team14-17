# COMP3516 2022-23 Course Project

## Group 14 Members:
| <strong>Name      | UID |
| ----------| ----------- |
| Rahman, Tasnia Ishrar | 3035718187|
| Gupta, Rhea   | 3035550731   |
| Bhargava, Anishka | 3035660782 |


----
Project Topic: File Transfer via High-Speed Screen-Camera Communication
----

### Setup

1. Clone the application

```bash
git clone https://github.com/rhea20/comp3516_team14-17
```

2. Install necessary libraries

```bash
pip install flask qrcode Pillow pyzbar libzbar0 opencv-python fpdf PyPDF2
```

3. Run

```bash
flask run
```

### Paths

http://127.0.0.1:5000 : For uploading a file on the senders' to be encoded into QR code(s)
http://127.0.0.1:5000/scanner : For uploading QR code(s) to be decoded and reconstruct the file on the receivers' end

Note: Please remove the files with the 'encoded_image' prefix from the 'sender' directory every time you test out with a new image file


All rights reserved &copy; The University of Hong Kong 2023
