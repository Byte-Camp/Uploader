import sys, os, inspect, webbrowser, subprocess, shutil
from flask import Flask, render_template, request, url_for, flash, send_from_directory, redirect, json
from werkzeug.utils import secure_filename

# Initialize flask app
app = Flask(__name__, template_folder='html')
cwd = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
UPLOAD_FOLDER = cwd+'/static/files'
ALLOWED_EXTENSIONS = set([]) #no exceptions

def allowedFile(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def avi2mp4(filename, filepath):
	subprocess.call(['ffmpeg','-i',filepath,'-c:a','aac','-b:a','128k','-c:v','libx264','-preset','slow','-strict','-2','-crf','22',filepath[:-4]+'.mp4','-y'])
	os.remove(filepath)
	filename = filename[:-4]+'.mp4'
	filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
	return filename, filepath

def makeThumb(filepath):
	subprocess.call(['ffmpeg','-i',filepath,'-ss','00:00:00','-vframes','1',filepath[:-4]+'.jpg','-y'])
	return True

def getThumb(filepath, upload):
	file_ext = -4;
	if (filepath[file_ext] != '.'):
		file_ext = None
	elif (filepath[file_ext:] == '.mp3' or filepath[file_ext:] == '.wav'):
		upload = 'audio'
	shutil.copyfile(cwd+'/static/thumbnails/'+upload+'.jpg', filepath[:file_ext]+'.jpg')
	return True

def upload(upload):
	files = request.files.getlist(upload)
	student = request.form['student']; name = student+'-'
	global filename; global error; directory = '/'
	filetype_error = None; error = None;
	dir_temp = request.files[upload].filename.split('/')
	if (len(dir_temp) > 1):
		directory += name+dir_temp[0]
		name = ''
		if (not os.path.exists(app.config['UPLOAD_FOLDER']+directory)):
			os.makedirs(app.config['UPLOAD_FOLDER']+directory)
		thumb = getThumb(app.config['UPLOAD_FOLDER']+directory, 'directory')
	
	for file in files:
		file.filename = file.filename.replace(dir_temp[0]+'/', '')
		filename = name+(secure_filename(file.filename)).replace('_','')
		dirpath = os.path.join(app.config['UPLOAD_FOLDER']+directory, filename)
		file.save(dirpath)
		if (filename[-4:] == '.mp4'):
			thumb = makeThumb(dirpath)
		elif (filename[-4:] == '.avi'):
			print ("Converting AVI to MP4. This could take a little while...")
			filename, dirpath = avi2mp4(filename, dirpath)
			thumb = makeThumb(dirpath)
		elif (filename[-8:] == '.scratch'):
			thumb = getThumb(dirpath, 'scratch')
		else: 
			thumb = getThumb(dirpath, 'default')

def checkUSB(drive, i):
	player_loaded = "no"; error = True; size=""; used=""; available=""
	usb_error = "USB Not installed. Plug the USB in and press OK"

	if ("BYTECAMP" in drive[-1] or "BYTECAMP" in drive[0]):
		error = None; usb_error = None;
		size = int(round(int(drive[1])/1000.0))
		used = int(round((int(drive[1])-int(drive[3]))/1000.0))
		available = int(round(int(drive[3])/1000.0))	
		
		global usb_path
		if (i != 0):
			usb_path = i
		else:
			usb_path = drive[-1]+'/'

		if (os.path.isfile(usb_path+'Byte Camp Player.html')):
			player_loaded = 'yes'

		try: shutil.rmtree(UPLOAD_FOLDER)
		except Exception: pass
		shutil.copytree(usb_path+'data/projects', UPLOAD_FOLDER, symlinks=False, ignore=None)	
		app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

	return size, used, available, usb_error, player_loaded, error

@app.route('/')
def startUploader():
	unix = ['darwin','linux2','os2','os2emx']
	windows = ['win32','cygwin']
	platform = sys.platform
	
	if (platform in unix): # UBUNTU System
		df = subprocess.Popen(["df"], stdout=subprocess.PIPE)
		output = df.communicate()[0]; i = 1;
		while output.split("\n")[i].split():
			drive = \
			    output.split("\n")[i].split()
			size, used, available, usb_error, player_loaded, error = checkUSB(drive, 0)
			if (not error):
				break
			i += 1
	elif (platform in windows): #WINDOWS System
		import win32api
		drives = win32api.GetLogicalDriveStrings()
		drives = drives.split('\000')[:-1]
		dont_check = ['C:\\', 'D:\\', 'E:\\']
		for i in drives:
			if (i not in dont_check):
				drive = win32api.GetVolumeInformation(str(i))
				size, used, available, usb_error, player_loaded, error = checkUSB(drive, i)
				if (not error):
					break
	else: #Other System
		print ("This program should be run on Windows or UNIX Systems Only!")
		sys.exit()

	return render_template('index.html',disk_size=size, disk_avail=available, 
	player_loaded=player_loaded, disk_used=used, error=error, error_type=usb_error)
	

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
    upload('file')
    return json.dumps('success uploading file')


@app.route('/uploadDirectory', methods=['POST'])
def uploadDirectory():
    upload('dir')
    return json.dumps('success uploading directory')


@app.route('/removeFile', methods=['POST'])
def removeFile():
	filename = request.get_json(); file_ext = -4;
	filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
	if (filename[file_ext] != '.'):
		shutil.rmtree(filepath); file_ext = None;
	else:
		os.remove(filepath)
	os.remove(filepath[:file_ext]+'.jpg')
	return json.dumps('success removing file')


@app.route('/preview', methods=['GET'])
def preview():
	shutil.rmtree(usb_path+'data/projects/')
	shutil.copytree(app.config['UPLOAD_FOLDER'], usb_path+'data/projects/', symlinks=False, ignore=None)
	
	on_usb = os.listdir(app.config['UPLOAD_FOLDER'])
	shutil.copyfile(cwd+'/static/player/player_template.html', cwd+'/static/player/player_template_full.html')
	with open(cwd+'/static/player/player_template_full.html', 'a') as player:
		player.write("\n<div id='projects' style='display:inline'>\n")
		
		for project in on_usb:
			if (project[-4:] != '.jpg'):
				student = project.split("-"); j = ''
				project_name = student[1:]; student = student[0]
				player.write(
					"<div id='scrollitem'>\n"+
						"\t<a href='javascript:newSWF(\""+project+"\")'>\n"+
							"\t\t<img src='data/projects/"+project[:-4]+".jpg' width='60' height='48'>\n"+
						"\t</a>\n"+
						"\t<div id='scrolltext'>\n"+
							"\t\t<a href='javascript:newSWF(\""+project+"\")'>\n"+
								"\t\t\t<span id='scrolltitle'>"+j.join(project_name)+"</span><br>\n"+
								"\t\t\t<span id='scrollsubtitle'>"+student+"</span>\n"+
							"\t\t</a>\n"+
						"\t</div>\n"+
					"</div>\n"
				)
		player.write("</div></div><div class='clear'></div></div></body></html>")

	os.remove(usb_path+"Byte Camp Player.html")
	shutil.copyfile(cwd+'/static/player/player_template_full.html', usb_path+"Byte Camp Player.html")
	os.remove(cwd+'/static/player/player_template_full.html')
	webbrowser.open_new("file://"+usb_path+"Byte Camp Player.html")
	return json.dumps('success loading preview')

if __name__=="__main__":
	app.secret_key = 'super secret key'
	app.config['SESSION_TYPE'] = 'filesystem'
	#app.debug = True
	webbrowser.open_new("http://localhost:5000")
	app.run()
