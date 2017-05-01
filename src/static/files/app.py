# IMPORT PYTHON LIBRARIES
import sys, os, inspect, ntpath, webbrowser, subprocess, shutil
import usb.core

cwd = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))


from flask import Flask, render_template, request, url_for, flash, send_from_directory, redirect
#from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename


# Initialize the Flask application
UPLOAD_FOLDER = cwd+'/static/wav'
ALLOWED_EXTENSIONS = set(['wav', 'WAV'])
app = Flask(__name__, template_folder='www')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

disk = ""; size = ""; used = ""; available = ""; percent_used = ""; mountpoint = ""; filename = ""

#app.config['MYSQL_USER'] = 'bytecamp_test2'
#app.config['MYSQL_PASSWORD'] = '18888082983Unicorn'
#app.config['MYSQL_HOST'] = 'localhost:3306'
#app.config['MYSQL_DB'] = 'bytecamp_test'
#mysql = MySQL(app)

# Define a route for the default URL, which loads the form
@app.route('/')
def form():
	#cur = mysql.connection.cursor()
	#cur.execute('''SELECT * FROM schools WHERE `District Number` = 61''')
	#rv = cur.fetchall()

	df = subprocess.Popen(["df"], stdout=subprocess.PIPE)
	output = df.communicate()[0]
	i = 1; usb_error = True;
	while output.split("\n")[i].split():
		x = \
		    output.split("\n")[i].split()
		if "BYTECAMP" in x[-1]:
			usb_error = None
			global disk
			disk = x[0]		
		i += 1

	return render_template('index.html', disk=disk, filename=filename, error=usb_error)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods = ['POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        #if (allowed_file(file.filename)):
        global filename
        filename = secure_filename(file.filename)
        print filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        shutil.copytree(app.config['UPLOAD_FOLDER'], '/media/adar/BYTECAMP/data/projects/test/', symlinks=False, ignore=None)
        return render_template('index.html', disk=disk, filename=filename, error=None)
	filetype_error = "Sorry! Must be a ... file."
	return render_template('index.html', disk=disk, filename=filename, error=filetype_error)

# Define a route for the action of the form, for example '/hello/'
# We are also defining which type of requests this route is 
# accepting: POST requests in this case
@app.route('/'+'static/wav'+'/', methods=['POST'])
def hello():
	if request.method == 'POST':
		settings = [request.form['inst1'],		request.form['dyn'],
					request.form['inst2'],		request.form['pattern'],
					request.form['inst3'],		request.form['timeSig'],

					request.form['style'],		request.form['busy'],
					request.form['tight'],		request.form['speed'],
					request.form['filename']]
		return render_template('index.html', filename='Browse for file...', disabled_radio="true", error=error)


# Run the app :)
if __name__ == '__main__':
	app.secret_key = 'super secret key'
	app.config['SESSION_TYPE'] = 'filesystem'
	app.debug = True
	webbrowser.open_new("http://localhost:5000")
	app.run()

