import sys, os, inspect, webbrowser, subprocess, shutil
import usb.core
from flask import Flask, render_template, request, url_for, flash, send_from_directory, redirect, json
from werkzeug.utils import secure_filename
#from flask_mysqldb import MySQL


# Initialize the Flask application
cwd = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
UPLOAD_FOLDER = cwd+'/static/files'
try:
	shutil.rmtree(UPLOAD_FOLDER)
except Exception:
	pass

ALLOWED_EXTENSIONS = set([])
app = Flask(__name__, template_folder='html')

#app.config['MYSQL_USER'] = 'bytecamp_test2'
#app.config['MYSQL_PASSWORD'] = '18888082983Unicorn'
#app.config['MYSQL_HOST'] = 'localhost:3306'
#app.config['MYSQL_DB'] = 'bytecamp_test'
#mysql = MySQL(app)

disk = ""; size = ""; used = ""; available = ""; percent_used = ""
mountpoint = ""; filename = "Browse..."; files = []; player_loaded = "no"
error = True; usb_path='';

def allowedFile(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def avi2mp4(filename, filepath):
	subprocess.call(['ffmpeg','-i',filepath,'-c:a','aac','-b:a','128k','-c:v','libx264','-strict','-2','-crf','23',filepath[:-4]+'.mp4','-y'])
	os.remove(filepath)
	filename = filename[:-4]+'.mp4'
	filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
	return filename, filepath

def makeThumb(filepath):
	subprocess.call(['ffmpeg','-i',filepath,'-ss','00:00:00','-vframes','1',filepath[:-4]+'.jpg','-y'])

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
			global player_loaded; global usb_path
			if (os.path.isfile('/media/adar/BYTECAMP/Byte Camp Player.html')):
				player_loaded = 'yes'
				usb_path = '/media/adar/BYTECAMP/'
			elif (os.path.isfile('/Volumes/BYTECAMP/Byte Camp Player.html')):
				player_loaded = 'yes'
				usb_path = '/Volumes/BYTECAMP/'
			try:
				shutil.copytree(usb_path+'data/projects', UPLOAD_FOLDER, symlinks=False, ignore=None)
			except Exception:
				pass
			app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

			break;
		i += 1
	return render_template('index.html',disk=disk, disk_size=size, disk_avail=available, 
										player_loaded=player_loaded, disk_used=used, 
										filename=filename, error=error, error_type=usb_error)


@app.route('/showContents', methods=['GET'])
def showContents():
	on_usb = os.listdir(app.config['UPLOAD_FOLDER'])
	students = []; projects = []; j = '-'
	for i in range(len(on_usb)):
		students.append((on_usb[i].split('-')[0]).strip())
		try:
			projects.append((j.join(on_usb[i].split('-')[1:])).strip())
		except Exception:
			pass
		if (not os.path.isfile(app.config['UPLOAD_FOLDER']+students[i]+j+projects[i])):
			os.rename(app.config['UPLOAD_FOLDER']+'/'+on_usb[i], app.config['UPLOAD_FOLDER']+'/'+students[i]+j+projects[i])
	return json.dumps([students, projects])


@app.route('/uploadFile', methods=['POST'])
def uploadFile():
    file = request.files['file']
    student = request.form['student']
    global filename; global error
    filetype_error = None; error = None
    #if (allowedFile(file.filename)):
    filename = student+'-'+(secure_filename(file.filename)).replace('_','')
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    if (filename[-4:] == '.mp4'):
    	makeThumb(filepath)
    elif (filename[-4:] == '.avi'):
    	filename, filepath = avi2mp4(filename, filepath)
    	makeThumb(filepath)

    files.append(filename)
    return json.dumps([files, student])


@app.route('/removeFile', methods=['POST'])
def removeFile():
	filename = request.get_json()
	filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
	print filepath
	if (filename[-4:] == '.mp4'):
		os.remove(filepath[:-4]+'.jpg')
	os.remove(filepath)
	return json.dumps({'files':filename})


@app.route('/preview', methods=['GET'])
def preview():
	shutil.rmtree(usb_path+'data/projects/')
	shutil.copytree(app.config['UPLOAD_FOLDER'], usb_path+'data/projects/', symlinks=False, ignore=None)
	webbrowser.open_new("file://"+usb_path+"Byte Camp Player.html")
	return json.dumps('success')

if __name__=="__main__":
	app.secret_key = 'super secret key'
	app.config['SESSION_TYPE'] = 'filesystem'
	#app.debug = True
	webbrowser.open_new("http://localhost:5000")
	app.run()
