from flask import Flask, request, redirect, url_for, send_from_directory, render_template
from werkzeug import secure_filename
import imghdr
import string
import random
import time
import sqlite3
import os
import cropped_thumbnail
from PIL import Image

###############################################################################
### Hack to teach imghdr how to recognize more jpegs
###############################################################################
def test_icc_profile_images(h, f):
    if h.startswith('\xff\xd8') and h[6:17] == b'ICC_PROFILE':
        return "jpeg"
imghdr.tests.append(test_icc_profile_images)

###############################################################################
### Flask app config
###############################################################################
app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'images'
app.config['MAX_CONTENT_LENGTH'] = 25 * 1024 * 1024

###############################################################################
### Database connection
###############################################################################
connection = sqlite3.connect('img.db', check_same_thread=False)
connection.isolation_level = None
db_cursor = connection.cursor()

###############################################################################
### Convenience functions
###############################################################################
def _generate_filename(filetype):
    ''' Create filename. This will produce collisions and not resolve them.
    TODO: upgrade this to use a lehmer function to create pseudorandom unique
    filenames/ids for the images. '''
    alphanumeric = string.ascii_lowercase
    alphanumeric += string.digits
    # find an unused shortcode
    while True:
        chars = [random.choice(alphanumeric) for _ in range(6)]
        shortcode = ''.join(chars)
        c = db_cursor.execute("SELECT * FROM uploads"
                " WHERE shortcode = '%s'" % shortcode)
        # 0 rows so shortcode is unused
        if not c.fetchall():
            break
    return shortcode + '.' + filetype

def _generate_path(filename):
    ''' Use the app settings to create the path the image will be saved
    under. '''
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return path

def _create_thumbnail(input_file, thumbname):
    ''' Create a square thumbnail using the method created by olooney and
    documented at https://gist.github.com/olooney/1601455 '''
    size = (300, 300)
    image = Image.open(input_file, 'r')
    thumb = cropped_thumbnail.cropped_thumbnail(image, size)
    thumb.save(_generate_path(thumbname))
    return thumb

def _save_image_files(input_file):
    ''' Takes an image file and saves it and a thumbnail to disk. Returns the
    filename of the main image file. '''
    filetype = imghdr.what(input_file)
    if filetype is None:
        return None
    filename = _generate_filename(filetype)
    input_file.save(_generate_path(filename))
    thumbname = 'thumb_' + filename
    _create_thumbnail(input_file, thumbname)
    return filename

###############################################################################
### Routes
###############################################################################
@app.route('/')
def index():
    ''' Returns the index. Supplies the template with the most recent 50
    uploads to populate the front page with. '''
    rows = db_cursor.execute('SELECT * FROM uploads ORDER BY key DESC'
            ' limit 50;')
    recent_uploads = [('v/thumb_' + row[2], 'v/' + row[2]) for row in rows]
    return render_template('index.html', recent_uploads=recent_uploads)

@app.route('/post', methods=['POST'])
def post_image():
    ''' Accepts an image as part of a post request. If the image can be
    identified to be of a supported type it is uploaded and the relative path
    to the image (always begining with 'v/' is returned. Otherwise an error
    message is returned. '''
    image_file = request.files['file']
    filename = _save_image_files(image_file)
    if filename is None:
        return 'ERROR: Not an image'
    db_cursor.execute('INSERT INTO uploads (ip, filename, shortcode, time)'
            ' VALUES (?,?,?,?);', (str(request.remote_addr), filename,
            filename.split('.')[0], int(time.time())))
    return 'v/%s' % filename

@app.route('/v/<image>', methods=['GET'])
def view(image):
    ''' Get an image based off the filename. This can be optimized by having
    the server rewrite this route and serve the image directly. '''
    secure_image = secure_filename(image)
    return send_from_directory('images', secure_image)

###############################################################################
### Run
###############################################################################
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
