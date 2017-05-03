import sys, os, inspect, webbrowser, subprocess, shutil
import usb.core
from flask import Flask, render_template, request, url_for, flash, send_from_directory, redirect, json
from werkzeug.utils import secure_filename
#from flask_mysqldb import MySQL


# Initialize the Flask application
cwd = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
UPLOAD_FOLDER = cwd+'/static/files'
ALLOWED_EXTENSIONS = set([])
app = Flask(__name__, template_folder='html')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#app.config['MYSQL_USER'] = 'bytecamp_test2'
#app.config['MYSQL_PASSWORD'] = '18888082983Unicorn'
#app.config['MYSQL_HOST'] = 'localhost:3306'
#app.config['MYSQL_DB'] = 'bytecamp_test'
#mysql = MySQL(app)

disk = ""; size = ""; used = ""; available = ""; percent_used = ""
mountpoint = ""; filename = "Browse..."; files = []; player_loaded = "no"
error = True

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def startUploader():
	df = subprocess.Popen(["df"], stdout=subprocess.PIPE)
	output = df.communicate()[0]
	
	i = 1; usb_error = "USB Not installed. Plug the USB in and press OK";
	while output.split("\n")[i].split():
		x = \
		    output.split("\n")[i].split()
		if "BYTECAMP" in x[-1]:
			global disk; global size; global error
			global used; global available;
			
			usb_error = None
			error = None	
			disk = x[0]
			size = int(round(int(x[1])/1000.0))
			used = int(round(int(x[2])/1000.0))
			available = int(round(int(x[3])/1000.0))
			
			if (os.path.isfile('/media/adar/BYTECAMP/Byte Camp Player.html') or
				os.path.isfile('/Volumes/BYTECAMP/Byte Camp Player.html')):
				global player_loaded
				player_loaded = "yes"
			break;
		i += 1
	return render_template('index.html',disk=disk, disk_size=size, disk_avail=available, 
										player_loaded=player_loaded, disk_used=used, 
										filename=filename, error=error, error_type=usb_error)


@app.route('/uploadFile', methods=['POST'])
def uploadFile():
    file = request.files['file']
    global filename; global error
    filetype_error = None; error = None
    #if (allowedFile(file.filename)):
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    if (filename[-4:] == '.avi'):
	    subprocess.call(['ffmpeg','-i',filepath,'-c:a','aac','-b:a','128k','-c:v','libx264','-strict','-2','-crf','23',filepath[:-4]+'.mp4','-y'])
	    filename = filename[:-4]+'.mp4'
	    subprocess.call(['ffmpeg','-i',filepath[:-4]+'.mp4','-ss','00:00:00','-vframes','1',filepath[:-4]+'.png','-y'])
	    thumb = filename[:-4]+'.png'
    files.append(filename)
    return json.dumps({'files':files})


@app.route('/removeFile', methods=['POST'])
def removeFile():
	filename = request.get_json()
	filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
	if (filename[-4:] == '.mp4'):
		os.remove(filepath[:-4]+'.avi')
		os.remove(filepath[:-4]+'.png')
	os.remove(filepath)
	#shutil.rmtree('/media/adar/BYTECAMP/data/projects/')
    #shutil.copytree(app.config['UPLOAD_FOLDER'], '/media/adar/BYTECAMP/data/projects/', symlinks=False, ignore=None)
	return json.dumps({'files':filename})


if __name__=="__main__":
	app.secret_key = 'super secret key'
	app.config['SESSION_TYPE'] = 'filesystem'
	#app.debug = True
	webbrowser.open_new("http://localhost:5000")
	app.run()
