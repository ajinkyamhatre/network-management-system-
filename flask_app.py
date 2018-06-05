import random
from flask import request
from telnet.mytelnet import telnet
from net.mynet import connected_to_internet
import re
import requests
from flask import Flask,render_template,request,session,redirect,url_for
import MySQLdb
import os
import telnetlib
import commands
import time
from werkzeug import secure_filename
UPLOAD_FOLDER = '/home/glassofvodka/Desktop/project /code/uploads'
hostname = "192.168.0.1" 
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.secret_key = 'my key'

@app.route('/myrouter')
def myrouter():
	op = []
	# Open database connection
	db = MySQLdb.connect("localhost","root","qwerty@123","mysql" )
	# prepare a cursor object using cursor() method
	cursor = db.cursor()
	sql = "select * from Myrouter"
	try:
		cursor.execute(sql)
		results = cursor.fetchall()
		for i in results:
			op.append(i)
	except:
		return "</br><h1>Error: unable to fecth data</h1>"
	db.close()
	
        return render_template('router.html',route=op)

@app.route('/logs')
def mylogs():
	op = []
	# Open database connection
	db = MySQLdb.connect("localhost","root","qwerty@123","mysql" )
	# prepare a cursor object using cursor() method
	cursor = db.cursor()
	sql = "select * from mylogs"
	try:
		cursor.execute(sql)
		results = cursor.fetchall()
		for i in results:
			op.append(i)
	except:
		return "</br><h1>Error: unable to fecth data</h1>"
	db.close()
	
        return render_template('logs.html',route=op)


@app.route('/data/<ip>')
def test(ip):
	cpu=''
	

	myip = 'http://'+ip
	r = connected_to_internet(myip)
	if r :
		cpu = telnet(["cpuocpy"])
		cpu = cpu.split('%')[0]
		cpu = int(cpu.split('occupancy')[1])
	mem =['62%','63%','62.5%','64%','63.3%','61.6%','65%','64%','61%','60%']
	m = mem[random.randint(0,9)]
	nw = []
	nw2 = []
	if r:
		cmd = 'show mac'
		op = telnet([cmd])
		op = op.split('Port  State')
		op = op[0]
		op = op.split('aging')[1]
		op = op.split('\r')
		for o in op:
			d = re.split(r'[?,|;|\s]\s*',o)
			if (len(d) > 2):
				nw.append(d)

		id2 = 'show arp'
		op2 = telnet([id2])
		op2 = op2.split('Interface')[1]
		op2 = op2.split('\r')
	
		for o in op2:
			d = re.split(r'[?,|;|\s]\s*',o)
			if (len(d) > 2):
				nw2.append(d)
        return render_template('indexpage.html',myuser=nw,mu=nw2,mem=m,r=r,cpu=cpu)




@app.route('/login', methods=['GET','POST'])
def myrequest():
	session['logged_in'] = False
	if request.method == 'POST':
		if request.form['email'] == 'admin@gmail.com' and request.form['password'] == 'admin':
			session['logged_in'] = True
			return redirect(url_for('test',ip='192.168.01'))
		else:
			return "</br></br><h1>Wrong Password</h1>"
	else:
		return render_template('Signin.html')

@app.route('/upload')
def upload_file1():
	return render_template('input.html')
	
@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
	if request.method == 'POST':
		f = request.files['file']
		filename = secure_filename(f.filename)
		f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		path = '/home/glassofvodka/Desktop/project /code/uploads/'+str(filename)
		myfile = open(path,'r')
		op1 = myfile.read()
		myfile.close()
		op = op1.split('\n')
		

		op = telnet(op)
		
		op = op.split('\n')
		return render_template('upload.html',op=op)
		

@app.route('/command', methods=['GET','POST'])
def router():
	if request.method == 'POST':
		id = request.form['command']
		id = str(id)
		
		op = telnet([id])
		
		#change starts
			
		db = MySQLdb.connect("localhost","root","qwerty@123","mysql" )

		cursor = db.cursor()
		
		sql = "INSERT INTO mylogs (ip,cmd,date) VALUES ('%s', '%s','%s');"%(request.remote_addr,id,time.asctime( time.localtime(time.time()) ))
	
		try:
			cursor.execute(sql)
			db.commit()
		except:
			print "rool back --------------------------------------------"
			db.rollback()
		db.close()
		#change ends
		
		op = op.split('\n')
		return render_template('upload.html',op=op)
	return render_template('form.html')

@app.route('/sync')
def sync():
	# Open database connection
	db = MySQLdb.connect("localhost","root","qwerty@123","mysql" )
	# prepare a cursor object using cursor() method
	cursor = db.cursor()
	sql = "select * from routertbl"
	try:
		cursor.execute(sql)
		results = cursor.fetchall()
	except:
		return "</br><h1>Error: unable to fecth data</h1>"
	op = results[0][1]
	op=op.replace("\n","</br>")
	db.close()
	url = "http://mysoftwaretechmart.pythonanywhere.com/"
	myjson = {'IP' : '192.168.0.1','type' : 'mac','text' : op}
	r = requests.post(url+"mypost",json=myjson)
	op = [r.text]
	r = requests.get(url+"cmd")
	rp = eval(r.text)
	cmd = rp['cmd']
	reply = rp['reply']
	if reply == 'not set':
		reply = telnet([cmd])
	return render_template('upload.html',op=reply.split('\n'))

@app.route('/backup')
def backup():
	# mac table --------------------------------------------
	mac = ''
	cmd = 'show mac'
	
	op = telnet([cmd])
	
	op = op.split('Port  State')
	op = op[0]
	mac = op.split('show mac')[1]
	
	# arp table --------------------------------------------
	arp = ''
	cmd = 'show arp'
	op = telnet([cmd])
	arp = op


	db = MySQLdb.connect("localhost","root","qwerty@123","mysql" )

	# prepare a cursor object using cursor() method
	cursor = db.cursor()
	dlt = "delete from routertbl where IP = '192.168.0.1'"
	try:
		cursor.execute(dlt)
		db.commit()
	except:
		print "rool back bro"
		db.rollback()
		
		
	sql = "INSERT INTO routertbl (IP,mac,arp) VALUES ('192.168.0.1', '%s','%s');"%(mac,arp)

	try:
		cursor.execute(sql)
		db.commit()
	except:
		db.rollback()
		
	
	db.close()
	op = ['Backup Complete']
	return render_template('upload.html',op=op)

@app.route('/conn', methods=['GET','POST'])
def connection():
	t = time.asctime( time.localtime(time.time()) )
	net = "http://google.com"
	router = "http://192.168.0.1"
	ans = []
	a = connected_to_internet(net)
	ans.append(a)
	b = connected_to_internet(router)
	ans.append(b)
	return render_template('conn.html',con=ans,t=t)

@app.route('/lan', methods=['GET','POST'])
def lan():
	nw2 = []
	id2 = 'show arp'
	op2 = telnet([id2])
	op2 = op2.split('Interface')[1]
	op2 = op2.split('\r')
	for o in op2:
		d = re.split(r'[?,|;|\s]\s*',o)
		if (len(d) > 2):
			nw2.append(d)
	return render_template('lan.html',con=nw2)

@app.route('/restart')
def restart():
	telnet('restart')
	return redirect(url_for('test'))

@app.route('/logout')
def logout():
	session['logged_in'] = False
	return redirect(url_for('myrequest'))

if __name__ == "__main__":
	app.run(host='0.0.0.0')
