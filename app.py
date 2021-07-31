from flask import Flask,render_template,request,url_for,redirect,flash,session,g, send_from_directory, abort,send_file
from database import connection
from wtforms import Form, BooleanField,TextAreaField, TextField, PasswordField,validators
from flask_bcrypt import Bcrypt
from functools import wraps
from MySQLdb import escape_string as thwart
import gc
from time import localtime,strftime
from datetime import datetime
import os
from werkzeug.utils import secure_filename
#from flask_socketio import SocketIO,send, emit, join_room, leave_room
#from asgiref.wsgi import WsgiToAsgi
import smtplib,ssl
from email.mime.text import MIMEText
import random


app=Flask(__name__)
app.config['SECRET_KEY'] = "ignance123@"
app.config['DEBUG'] = True

    
#initializations
bcrypt = Bcrypt()
#socketio = SocketIO(app)

       
@app.route("/confirm_email/", methods=["GET","POST"])
def confirm_email():
    port = 465
    stmp_server = "smtp.gmail.com"
    
    sender_email = "akietorna@gmail.com"
    receiver_email = str(session["email"])
    name = session['lastname']
    password = "hispresence"

    confirmation_code = ""
    for a in range(0,7):
        confirmation_code += str(random.randint(0,9))

    

    msg = MIMEText(" Hello "+ name + " ! \n \n You signed up an account on the Pentecostal Revival center,AG website.To confirm that it was really you, please enter the confirmatory code  into the box provided. Thank you \n \n \t \t Confirmatory Code: "+ confirmation_code  +"\n \n  But if it was not you can ignore this mail sent to you ")
    msg['Subject'] = 'PRC AG website sign up email confirmation'
    msg['From'] = 'pentecostalrevivalcenterag@gmail.com'
    msg['To'] = session["email"]
    
    session['conf'] = confirmation_code

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(stmp_server,port,context = context) as server:
        server.login(sender_email,password)
        server.sendmail(sender_email,receiver_email,msg.as_string())
        print('Mail sent')

    return redirect(url_for('confirm_coded'))
    

@app.route("/confirm_coded/", methods=["POST", "GET"])
def confirm_coded():
    form = ConfirmEmail(request.form)
    if request.method =="POST" and form.validate():
        confirmed_code = form.confirmation.data
        conf = session['conf']
        # inserting statements into the database
        if confirmed_code == conf:
            firstname = session["firstname"]
            lastname=session["lastname"]
            day= session["day"]
            month=session["month"]
            year=session["year"]
            sex=session["sex"]
            contact=session["contact"]
            marital_status=session["marital_status"]
            username=session["username"]
            email = session["email"]
            password = session["password"]

            print('it worked')

            curs,connect = connection()

            curs.execute("INSERT INTO users (firstname,lastname, day, month, year, sex,tel_number, marital_status, username, email, password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",([firstname],[lastname], [day],[month],[year],[sex],[contact],[marital_status],[username], [email], [password]) ) 

            connect.commit()
            flash("Thanks. Registration was succesfull!")
            curs.close()
            connect.close()
            gc.collect()

            session['logged_in'] = True

            return redirect(url_for('home'))

        else:
            error = "Your credentials do not match, try again" 
            return render_template('sign_up_page.html', error = error)

    return render_template("confirm_email.html", form = form)




def login_required(f):
    @wraps(f)
    def wrapping(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        
        else :
            flash('You need to login first')
            return redirect(url_for('home_page'))
        
    return wrapping

def logged_in_required(f):
    @wraps(f)
    def wrapping(*args, **kwargs):
        if 'admin' in session:
            return f(*args, **kwargs)
        
        else :
            flash('You need to login first')
            return redirect(url_for('admin'))
        
    return wrapping 
    

class RegistrationForm(Form):
    firstname = TextField('Firstname', [validators.Length(min=4, max=24)])
    lastname = TextField('Lastname', [validators.Length(min=4, max=24)])
    sex = TextField('Sex', [validators.Length(min=1, max=7)])
    username = TextField('Username', [validators.Length(min=4, max=24)])
    email = TextField('Email Address', [validators.Length(min=9, max=50)])
    password = PasswordField('Password', [validators.Length(min=5, max=40)])


class ResetPassword(Form):
    username = TextField('Enter your Username', [validators.Length(min=4, max=24)])

class ConfirmEmail(Form):
    confirmation = TextField('Enter the Confirmatory Code', [validators.Length(min=4, max=24)])

class SetPassword(Form):
    username = TextField('Enter your Username', [validators.Length(min=4, max=24)])
    password = PasswordField('Enter your new Password', [validators.Required(),validators.EqualTo('confirm_password', message="Passwords must match")])
    confirm_password = PasswordField(' Confirm Password')


class DailyDevotion(Form):
    sender_name = TextField('Author', [validators.Length(min=4, max=50)])
    title = TextField('Title', [validators.Length(min=1, max=100)])
    passage = TextField('Passage', [validators.Length(min=4, max=24)])
    message = TextAreaField('Message', [validators.Length(min=1, max=50000)])

class AddTestimony(Form):
    sender_name = TextField('Author', [validators.Length(min=4, max=50)])
    title = TextField('Title', [validators.Length(min=1, max=100)])
    testimony = TextAreaField('Testimony', [validators.Length(min=1, max=100000)])

class Announcement(Form):
    sender_name = TextField('Author', [validators.Length(min=4, max=50)])
    title = TextField('Title', [validators.Length(min=1, max=100)])
    announcement = TextAreaField('Announcement', [validators.Length(min=1, max=50000)])
    department = TextField('Department Code', [validators.Length(min=2, max=2)])

class PrayerRequest(Form):
    sender_name = TextField('Name', [validators.Length(min=4, max=50)])
    prayer = TextAreaField('Prayer_request', [validators.Length(min=1, max=50000)])
    contact = TextField('Contact', [validators.Length(min=10, max=15)])


class Comments(Form):
    sender_name = TextField('Name', [validators.Length(min=4, max=50)])
    comments = TextAreaField('Comment', [validators.Length(min=1, max=50000)])
    contact = TextField('Contact', [validators.Length(min=10, max=15)])


@app.route("/forget_password/", methods=["POST", "GET"])
def forget_password():
    
    form = ResetPassword(request.form)

    if request.method =="POST" and form.validate():
        username = form.username.data

        # fetching the email from database
        curs,connect = connection()
           
        curs.execute("select email from users where username = (%s) " , [username])
        r_email = curs.fetchone()[0]
        
        connect.commit()
        curs.close()
        connect.close()
        gc.collect()


        # sending the code to the eamil
        port = 465
        stmp_server = "smtp.gmail.com"
        
        sender_email = "pentecostalrevivalcenterag@gmail.com"
        receiver_email = r_email
        name = username
        password = "revmoses1954"

        confirmation_code = ""
        for a in range(0,7):
            confirmation_code += str(random.randint(0,9))

        

        msg = MIMEText(" Hello "+ name + " ! \n \n You requested for a reset of password on the Pentecostal Revival center,AG website.To confirm that it was really you, please enter the confirmatory code  into the box providedonthe website. Thank you \n \n \t \t Confirmatory Code: "+ confirmation_code  +"\n \n  But if it was not you can ignore this mail sent to you ")
        msg['Subject'] = 'PRC AG website sign up email confirmation'
        msg['From'] = 'pentecostalrevivalcenterag@gmail.com'
        msg['To'] =  r_email
        
        session["conf"] = confirmation_code

        print(confirmation_code)

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(stmp_server,port,context = context) as server:
            server.login(sender_email,password)
            server.sendmail(sender_email,receiver_email,msg.as_string())
            print('Mail sent')


        return redirect(url_for('confirm_reset'))

    return render_template("forgetPassword.html", form=form)


@app.route('/confirm_reset/', methods=["GET","POST"])
def confirm_reset():
    form=ConfirmEmail(request.form)
    if request.method =="POST" and form.validate():
        confirmed_code = form.confirmation.data
        conf = session["conf"]
        if conf == confirmed_code:
            return redirect(url_for('set_password'))

        else:
            error = "Your credentials do not match, try again" 
            return redirect(url_for('home_page'))

    return render_template("confirm_email.html", form = form)




@app.route('/set_password/',methods=["GET","POST"])
def set_password():
    error = ''
    form = SetPassword(request.form)
    if request.method =='POST' and form.validate():
        username = form.username.data
        password = form.password.data
        confirm_password = form.confirm_password.data

        if password == confirm_password:

            bcrypt = Bcrypt()
            password = bcrypt.generate_password_hash(password)

            curs, connect = connection()
            curs.execute("update users set password = (%s)  WHERE username = (%s)",[password,username])
            connect.commit()
            curs.close()
            connect.close()
            gc.collect()

            session['logged_in'] = True
            return redirect(url_for("home"))

        else:
            error = "Your credentials do not match, try again" 
            return render_template('reset_password.html', error = error)


    return render_template('reset_password.html', form=form)

@app.route("/addpost/", methods=["POST", "GET"])
@logged_in_required
def addpost():
    form = DailyDevotion(request.form)
    if request.method =='POST' and form.validate():
        sender_name = form.sender_name.data
        title = form.title.data
        passage = form.passage.data
        message= form.message.data

        time_sent = datetime.now()

        curs,connect = connection()
                    
        input_statement = ("INSERT INTO dailydevotion (sender_name,time_sent,title,passage,message) VALUES (%s,%s,%s,%s, %s)" ) 
        data = [sender_name, time_sent,title, passage,message]
        curs.execute( input_statement, data)

        connect.commit()
        print("The process was sucessful")
        curs.close()
        connect.close()
        gc.collect()

        return redirect(url_for('devotional'))

    return render_template("addpost.html", form=form, name=session['logged_in'])


@app.route("/addtestimony/", methods=["POST", "GET"])
@login_required
def addtestimony():
    form = AddTestimony(request.form)
    if request.method =='POST' and form.validate():
        sender_name = form.sender_name.data
        title = form.title.data
        testimony= form.testimony.data

        time_sent = datetime.now()

        curs,connect = connection()
                    
        input_statement = ("INSERT INTO testimony (sender_name,time_sent,title,testimony) VALUES (%s,%s,%s,%s)" ) 
        data = [sender_name, time_sent,title, testimony]
        curs.execute( input_statement, data)

        connect.commit()
        print("The process was sucessful")
        curs.close()
        connect.close()
        gc.collect()

        return redirect(url_for('testimony'))

    return render_template("addtestimony.html", form=form, name=session['admin'])


@app.route("/add_announcement/", methods=["POST", "GET"])
@logged_in_required
def add_announcement():
    form = Announcement(request.form)
    if request.method =='POST' and form.validate():
        sender_name = form.sender_name.data
        title = form.title.data
        announcement= form.announcement.data
        department= form.department.data

        time_sent = datetime.now()

        curs,connect = connection()
                    
        input_statement = ("INSERT INTO announcement (sender_name,time_sent,title,announcement,Dept_code) VALUES (%s,%s,%s,%s,%s)" ) 
        data = [sender_name, time_sent,title, announcement,department]
        curs.execute( input_statement, data)

        connect.commit()
        print("The process was sucessful")
        curs.close()
        connect.close()
        gc.collect()

        return redirect(url_for('announcement'))

    return render_template("add_announcement.html", form=form, name=session['admin'])



@app.route("/deletepost/",methods=["POST", "GET"])
@logged_in_required
def deletepost():
    if request.method == 'POST':
        picked = request.form['picked']


        # connection to database
        curs,connect = connection()
        curs.execute("DELETE FROM  dailydevotion WHERE user_id = %s", [picked])

        connect.commit()
        curs.close()
        connect.close()
        gc.collect()

        return redirect(url_for("devotional"))

    return redirect(url_for("devotional"), name= session['admin']) 

@app.route("/delete_announcement/",methods=["POST", "GET"])
@logged_in_required
def delete_announcement():
    if request.method == 'POST':
        picked = request.form['picked']


        # connection to database
        curs,connect = connection()
        curs.execute("DELETE FROM  announcement WHERE id_number = %s", [picked])

        connect.commit()
        curs.close()
        connect.close()
        gc.collect()

        return redirect(url_for("announcement"))

    return redirect(url_for("announcement"), name= session['admin']) 



@app.route("/delete_testimony/",methods=["POST", "GET"])
@login_required
def delete_testimony():
    if request.method == 'POST':
        picked = request.form['picked']


        # connection to database
        curs,connect = connection()
        curs.execute("DELETE FROM  testimony WHERE user_id = %s", [picked])

        connect.commit()
        curs.close()
        connect.close()
        gc.collect()

        return redirect(url_for("testimony"))

    return redirect(url_for("testimony"), name= session['logged_in']) 

@app.route("/devotional/",methods=["POST","GET"])
def devotional():
    error=''
    try:
        curs, connect = connection()
        curs.execute('SELECT * FROM dailydevotion')
        data = curs.fetchall()

        data = reversed(data)        
       
        return render_template("devotional.html", value = data)

    except Exception as e:
        return render_template('admin1.html', error = error , name=session['admin'])



@app.route("/announcement/",methods=["POST","GET"])
@logged_in_required
def announcement():
    error=''
    try:
        curs, connect = connection()
        curs.execute('SELECT * FROM announcement')
        data = curs.fetchall()

        data = reversed(data)        
       
        return render_template("announcement.html", value = data)

    except Exception as e:
        return render_template('admin1.html', error = error , name=session['admin'])


@app.route("/logout/")
@login_required
def logout():
    session.clear()
    gc.collect()
    return redirect(url_for('home_page'))

#routing the various webpages 


@app.route('/',methods=["GET","POST"])
def home_page():
    error = ''
    if request.method == 'POST':
        try:

            username = request.form['username']
            password = request.form['password']

            curs, connect = connection()
            info = curs.execute("SELECT * FROM users WHERE username = %s", [username])

            # fetching the password
 
            Passwd = curs.fetchone()[10]

            

            # checking if the password valid

            

            if info == 1 and bcrypt.check_password_hash(Passwd,password ) == True :
                session['logged_in'] = True
                session['username'] = request.form['username']
                update = request.form['username']

                return redirect(url_for("home"))

           


            else:
                error = "Your credentials are invalid, try again" 
            
            gc.collect() 
            return render_template('beginning.html', error = error)


        except Exception as e:

            return render_template('beginning.html', error = error)

    return render_template('beginning.html', error = error)
    


@app.route('/administration_page/',methods=["GET","POST"])
def admin():
    error = ''
    if request.method == 'POST':
        try:

            username = request.form['username']
            password = request.form['password']

            curs, connect = connection()
            info = curs.execute("SELECT * FROM administration WHERE username = %s", [username])



            # fetching the password

            Passwd = curs.fetchone()[3]

            

            # checking if the password valid

            

            if info == 1 and bcrypt.check_password_hash(Passwd,password ) == True :
                session['admin'] = True
                session['username'] = request.form['username']

                print("it worked")
                

                return redirect(url_for("users"))

            


            else:
                error = "Your credentials are invalid, try again" 
            
            gc.collect() 
            return render_template('admin1.html', error = error)


        except Exception as e:

            return render_template('admin1.html', error = error)

    return render_template('admin1.html', error = error)





@app.route('/users/',methods=['GET', 'POST'])
@logged_in_required
def users():
    error=''
    try:
        curs, connect = connection()
        curs.execute('SELECT * FROM users')
        data = curs.fetchall()

        return render_template("users.html", value = data)

    except Exception as e:
            return render_template('admin1.html', error = error , name=session['admin'])



@app.route('/add_users/', methods=['GET','POST'])
@logged_in_required
def add_users():

    form = RegistrationForm(request.form)
    if request.method =='POST' and form.validate():
        firstname = form.firstname.data
        lastname = form.lastname.data
        sex = form.sex.data
        username= form.username.data
        email = form.email.data

        bcrypt = Bcrypt()
        password = bcrypt.generate_password_hash(form.password.data)

        

            

        curs,connect = connection()

        # checking if the username matches that of another person
    

        check_name = curs.execute("SELECT * FROM users WHERE username = %s ", [username] )

        check_mail = curs.execute("SELECT * FROM users WHERE email = %s ", [email])

        if int(check_name) > 0:
            flash("Username already used,please choose another one")
            return render_template('add.html')

        elif int(check_mail) > 0:
            flash("Email already used,please choose another one")
            return render_template('add.html')

        else:


            # inserting statements into the database
            input_statement = ("INSERT INTO administration (firstname, lastname,sex,username,email, password) VALUES (%s, %s, %s, %s, %s, %s)" ) 
            data = (thwart(firstname), thwart(lastname), thwart(sex),  thwart(username),thwart(email),  thwart(password) )
            curs.execute( input_statement, data)

            connect.commit()
            flash("Thanks. Registration was succesfull!")
            curs.close()
            connect.close()
            gc.collect()

            return redirect(url_for("users"))

    return render_template("add.html", form=form, name=session['admin'])


@app.route('/delete_user/', methods=["GET", "POST"])
@logged_in_required
def delete_user():
    if request.method == 'POST':
        picked = request.form['picked']


# connection to database
        curs,connect = connection()
        curs.execute("DELETE FROM  users WHERE user_id = %s", [picked])

        connect.commit()
        curs.close()
        connect.close()
        gc.collect()

        return redirect(url_for('users'))
    return redirect(url_for('users'), name= session['admin']) 




@app.route('/home/',methods=["GET","POST"])
@login_required
def home():

    
    #flash("You are welcome to Pentecostal Revival Center, AG.We are happy to have you here")
    return render_template('home.html', name=session['logged_in'])



@app.route('/testimony/',methods=["GET","POST"])
@login_required
def testimony():
    error=''
    try:
        curs, connect = connection()
        curs.execute('SELECT * FROM testimony')
        data = curs.fetchall()
        
        data = reversed(data)



        return render_template("testimony.html", value = data)

    except Exception as e:
        return render_template('testimony.html', name=session['logged_in'])

@app.route('/prayer_request/',methods=["GET","POST"])
@logged_in_required
def prayer_request():
    error=''
    try:
        curs, connect = connection()
        curs.execute('SELECT * FROM prayer_request')
        data = curs.fetchall()
        
        data = reversed(data)



        return render_template("prayer_request.html", value = data)

    except Exception as e:
        return render_template('prayer_request.html', name=session['admin'])


@app.route('/get_comment/',methods=["GET","POST"])
@logged_in_required
def get_comment():
    error=''
    try:
        curs, connect = connection()
        curs.execute('SELECT * from comments')
        data = curs.fetchall()
        
        data = reversed(data)



        return render_template("comments.html", value = data)

    except Exception as e:
        return render_template('comments.html', name=session['admin'])



@app.route('/testimony1/',methods=["GET","POST"])
@logged_in_required
def testimony1():
    error=''
    try:
        curs, connect = connection()
        curs.execute('SELECT * FROM testimony')
        data = curs.fetchall()
        
        data = reversed(data)



        return render_template("testimony1.html", value = data)

    except Exception as e:
        return render_template('testimony1.html', name=session['admin'])

@app.route('/children/',methods=["GET","POST"])
@login_required
def children():
    try:
        curs, connect = connection()
        curs.execute('SELECT * from announcement where Dept_code="CM"')
        data = curs.fetchall()
        
        data = reversed(data)



        return render_template('children.html', name=session['logged_in'],value = data)

    except Exception as e:
        return render_template('children.html', name=session['logged_in'])

@app.route('/dailydevotion/',methods=["GET","POST"])
@login_required
def dailydevotion():
    error=''
    try:
        curs, connect = connection()
        curs.execute('SELECT * FROM dailydevotion')
        data = curs.fetchall()
        
        data = reversed(data)



        return render_template("dailydevotion.html", value = data)

    except Exception as e:
        return render_template('dailydevotion.html', name=session['logged_in'])
    

@app.route('/general/',methods=["GET","POST"] )
@login_required
def general():
    error=''
    try:
        curs, connect = connection()
        curs.execute('SELECT * FROM announcement where Dept_code = "GA" ')
        data = curs.fetchall()
        
        data = reversed(data)



        return render_template('general.html', name=session['logged_in'])

    except Exception as e:
        return render_template('general.html', name=session['logged_in'])
    


@app.route('/health1/',methods=["GET","POST"])
@login_required
def health1():
    error=''
    try:
        curs, connect = connection()
        curs.execute('SELECT id_number, filename,file FROM books where book_id = "HEAL"')
        data = curs.fetchall()

        return render_template('health1.html',  value = data)

    except Exception as e:
            return render_template('health1.html', name=session['logged_in'])
    

@app.route('/inspiration/',methods=["GET","POST"])
@login_required
def inspiration():

    error=''
    try:
        curs, connect = connection()
        curs.execute('SELECT id_number, filename,file FROM books where book_id="INS"')
        data = curs.fetchall()

        return render_template("inspiration.html", value = data)

    except Exception as e:
            return render_template('inspiration.html', name=session['logged_in'])

    

@app.route('/marriage1/',methods=["GET","POST"])
@login_required
def marriage1():
    error=''
    try:
        curs, connect = connection()
        curs.execute('SELECT id_number, filename,file FROM books where book_id = "MAR"')
        data = curs.fetchall()

        return render_template('marriage1.html',  value = data)

    except Exception as e:
        return render_template('marriage1.html', name=session['logged_in'])
    

@app.route('/men/',methods=["GET","POST"])
@login_required
def men():
    try:
        curs, connect = connection()
        curs.execute('SELECT * announcement where Dept_code="MM"')
        data = curs.fetchall()
        
        data = reversed(data)

        return render_template('men.html', name=session['logged_in'],value = data)

    except Exception as e:
        return render_template('men.html', name=session['logged_in'])

@app.route('/message/',methods=["GET","POST"])
@login_required
def message():
    error=''
    try:
        curs, connect = connection()
        curs.execute('SELECT filename,file,post_id FROM messages')
        data = curs.fetchall()

        return render_template("messages.html", value = data)

    except Exception as e:
            return render_template('messages.html', error = error , name=session['logged_in'])
    

@app.route('/prayer1/',methods=["GET","POST"])
@login_required
def prayer1():
    error=''
    try:
        curs, connect = connection()
        curs.execute('SELECT id_number, filename,file FROM books where book_id= "PRAY"')
        data = curs.fetchall()

        return render_template('prayer1.html',  value = data)

    except Exception as e:
        error = "please it did not work"
        return render_template('prayer1.html',error = error, name=session['logged_in'])


@app.route('/viewbook/',methods=["GET","POST"])
@login_required
def viewbook():
    error=''
    try:
        id_num = request.args.get('id')
        curs,connect = connection()
        curs.execute('select file,location,filename from books where id_number = %s',[id_num])
        data= curs.fetchall()
        return render_template('downloads.html',name=session['logged_in'], value=data)

    except Exception as e:
        return render_template('prayer1.html', name=session['logged_in'])

@app.route('/download/',methods=["GET","POST"])
@login_required
def download():
    path=request.args.get('id')
    return send_file(path,as_attachment=True)


@app.route('/download_audio/',methods=["GET","POST"])
@login_required
def download_audio():
    id_num=request.args.get('id')
    curs,connect = connection()
    curs.execute('select location from messages where post_id = %s',[id_num])
    path= curs.fetchone()[0]
    print(path)
    return send_file(path,as_attachment=True)


@app.route('/prayersections/',methods=["GET","POST"])
@login_required
def prayersections():
    form = PrayerRequest(request.form)
    if request.method =='POST' and form.validate():
        sender_name = form.sender_name.data
        prayer= form.prayer.data
        contact = form.contact.data

        time_sent = datetime.now()

        curs,connect = connection()
                    
        input_statement = ("INSERT INTO prayer_request (sender_name,time_sent,contact,prayer) VALUES (%s,%s,%s,%s)" ) 
        data = [sender_name, time_sent,contact, prayer]
        curs.execute( input_statement, data)

        connect.commit()
        print("The process was sucessful")
        curs.close()
        connect.close()
        gc.collect()

        return redirect(url_for('thank_you'))

    return render_template("prayersections.html", form=form, name=session['logged_in'])

@app.route('/comments/',methods=["GET","POST"])
@login_required
def comments():
    form = Comments(request.form)
    if request.method =='POST' and form.validate():
        sender_name = form.sender_name.data
        comments= form.comments.data
        contact = form.contact.data

        time_sent = datetime.now()

        curs,connect = connection()
                    
        input_statement = ("INSERT INTO comments(sender_name,time_sent,contact,comment) VALUES (%s,%s,%s,%s)" ) 
        data = [sender_name, time_sent,contact, comments]
        curs.execute( input_statement, data)

        connect.commit()
        print("The process was sucessful")
        curs.close()
        connect.close()
        gc.collect()

        return redirect(url_for('thank_you1'))

    return render_template("comments.html", form=form, name=session['logged_in'])

#takes care of audio extentions
def allowed_audio_types(filename):
    #this converts the data into binary format
    if not '.' in filename:
        return False
    
    extention = filename.rsplit('.', 1)[1]
    
    if extention.upper() in app.config['ALLOWED_AUDIO_EXTENTIONS']:
        return True
    else:
        return False


# takes care of extensions if books
def allowed_book_types(filename):
    #this converts the data into binary format
    if not '.' in filename:
        return False
    
    extention = filename.rsplit('.', 1)[1]
    
    if extention.upper() in app.config['ALLOWED_BOOK_EXTENTIONS']:
        return True
    else:
        return False


app.config['AUDIO_UPLOADS']= "/home/ekagbodjive/prcwebsite/static/sermon/"
app.config['SUNDAYSCH_UPLOADS']= "/home/ekagbodjive/prcwebsite/static/books/sundaysch/"
app.config['INSPIRATION_UPLOADS']= "/home/ekagbodjive/prcwebsite/static/books/inspirationalbooks/"
app.config['SPIRITUAL_UPLOADS']= "/home/ekagbodjive/prcwebsite/static/books/spirituallife/"
app.config['HEALTH_UPLOADS']= "/home/ekagbodjive/prcwebsite/static/books/health/"
app.config['PRAYER_UPLOADS']= "/home/ekagbodjive/prcwebsite/static/books/prayer/"
app.config['MARRIAGE_UPLOADS']= "/home/ekagbodjive/prcwebsite/static/books/marriage/"
app.config['ALLOWED_AUDIO_EXTENTIONS']= ['MP3', 'WMA', 'AAC', 'WAV', 'FLAC']
app.config['ALLOWED_BOOK_EXTENTIONS']=["PDF"]



@app.route('/spiritualbooks/', methods=["GET","POST"]) 
@logged_in_required
def spiritualbooks():
    if request.method =='POST':

        if request.files:
            spiritual = request.files['spiritualbooks']

            if spiritual.filename !='':

                if allowed_book_types(spiritual.filename):

                    filename = secure_filename(spiritual.filename)
                    spiritual.save(os.path.join(app.config['SPIRITUAL_UPLOADS'], filename))
                    

                    time_sent = datetime.now()

                    sender_name = session['username']

                    location = "/home/ekagbodjive/prcwebsite/static/books/spirituallife/" + filename

                    files = "/books/spirituallife/" + filename

                    curs,connect = connection()
                    

                    input_statement = ("INSERT INTO books (sender_name,time_sent,filename,file,location,book_id) VALUES (%s,%s,%s,%s,%s, %s)" ) 
                    data = [sender_name, time_sent,filename,files, location,"SPIR"]
                    curs.execute( input_statement, data)

                    connect.commit()
                    print("The process was sucessful")
                    curs.close()
                    connect.close()
                    gc.collect()

                else :
                    flash("that file type is not allowed")
                    print('that file type is not allowed')
                    return render_template('404.html')


                
            return redirect(url_for('spiritualbooks'))

    return render_template('spiritualbooks.html', name=session['admin'])



@app.route('/marriagebooks/', methods=["GET","POST"]) 
@logged_in_required
def marriagebooks():
    if request.method =='POST':

        if request.files:
            marriage = request.files['marriagebooks']

            if marriage.filename !='':

                if allowed_book_types(marriage.filename):

                    filename = secure_filename(marriage.filename)
                    marriage.save(os.path.join(app.config['MARRIAGE_UPLOADS'], filename))
                    

                    time_sent = datetime.now()

                    sender_name = session['username']

                    sermon = "/home/ekagbodjive/prcwebsite/static/books/marriage/"+ filename

                    files = "/books/marriage/" + filename
                    
                    curs,connect = connection()
                    

                    input_statement = ("INSERT INTO books (sender_name,time_sent,file,filename,location,book_id) VALUES (%s,%s,%s,%s,%s, %s)" ) 
                    data = [sender_name, time_sent,files,filename,sermon,"MAR"]
                    curs.execute( input_statement, data)

                    connect.commit()
                    print("The process was sucessful")
                    curs.close()
                    connect.close()
                    gc.collect()


                else :
                    flash("that file type is not allowed")
                    print('that file type is not allowed')
                    return render_template('404.html')

                
            return redirect(url_for('marriagebooks'))

    return render_template('marriagebooks.html', name=session['admin'])




@app.route('/sermons/', methods=["GET","POST"]) 
@logged_in_required
def sermons():
    if request.method =='POST':

        if request.files:
            audio = request.files['audio']

            if audio.filename !='':

                if allowed_audio_types(audio.filename):

                    filename = secure_filename(audio.filename)
                    audio.save(os.path.join(app.config['AUDIO_UPLOADS'], filename))
                    

                    time_sent = datetime.now()

                    sender_name = session['username']

                    sermon = "/home/ekagbodjive/prcwebsite/static/sermon/"+ filename

                    files = "/sermon/" + filename

                    curs,connect = connection()
                    

                    input_statement = ("INSERT INTO messages (sender_name,time_sent,location,filename,file) VALUES (%s,%s,%s,%s, %s)" ) 
                    data = [sender_name, time_sent, sermon,filename,files]
                    curs.execute( input_statement, data)

                    connect.commit()
                    print("The process was sucessful")
                    curs.close()
                    connect.close()
                    gc.collect()


                else :
                    flash("that file type is not allowed")
                    print('that file type is not allowed')
                    return render_template('404.html')

                
            return redirect(url_for('sermons'))

    return render_template('sermons.html', name=session['admin'])

  

@app.route('/sundayschool1/', methods=["GET","POST"]) 
@logged_in_required
def sundayschool1():
    if request.method =='POST':

        if request.files:
            sundaysch = request.files['sundaysch']

            if sundaysch.filename !='':

                if allowed_book_types(sundaysch.filename):

                    filename = secure_filename(sundaysch.filename)
                    sundaysch.save(os.path.join(app.config['SUNDAYSCH_UPLOADS'], filename))
                    

                    time_sent = datetime.now()

                    sender_name = session['username']

                    sermon = "/home/ekagbodjive/prcwebsite/static/books/sundaysch/" + filename

                    files = "/books/sundaysch/" + filename

                    curs,connect = connection()
                    

                    input_statement = ("INSERT INTO books (sender_name,time_sent,filename,file,location,book_id) VALUES (%s,%s,%s,%s,%s, %s)" ) 
                    data = [sender_name, time_sent,filename,files, sermon, "SSCH"]
                    curs.execute( input_statement, data)

                    connect.commit()
                    print("The process was sucessful")
                    curs.close()
                    connect.close()
                    gc.collect()

                else :
                    flash("that file type is not allowed")
                    print('that file type is not allowed')
                    return render_template('404.html')


                
            return redirect(url_for('sundayschool1'))

    return render_template('sundayschool1.html', name=session['admin'])




@app.route('/prayerbooks/', methods=["GET","POST"]) 
@logged_in_required
def prayerbooks():
    if request.method =='POST':

        if request.files:
            prayer = request.files['prayerbooks']

            if prayer.filename !='':

                if allowed_book_types(prayer.filename):

                    filename = secure_filename(prayer.filename)
                    prayer.save(os.path.join(app.config['PRAYER_UPLOADS'], filename))
                    

                    time_sent = datetime.now()

                    sender_name = session['username']

                    sermon =  "/home/ekagbodjive/prcwebsite/static/books/prayer/" + filename

                    files = "/books/prayer/" + filename
                    curs,connect = connection()
                    

                    input_statement = ("INSERT INTO books (sender_name,time_sent,filename,file,location,book_id) VALUES (%s,%s,%s,%s,%s, %s)" ) 
                    data = [sender_name, time_sent,filename,files, sermon,"PRAY"]
                    curs.execute( input_statement, data)

                    connect.commit()
                    print("The process was sucessful")
                    curs.close()
                    connect.close()
                    gc.collect()

                else :
                    flash("that file type is not allowed")
                    print('that file type is not allowed')
                    return render_template('404.html')


                
            return redirect(url_for('prayerbooks'))

    return render_template('prayerbooks.html', name=session['admin'])




@app.route('/healthbooks/', methods=["GET","POST"]) 
@logged_in_required
def healthbooks():
    if request.method =='POST':

        if request.files:
            health = request.files['healthbooks']

            if health.filename !='':

                if allowed_book_types(health.filename):

                    filename = secure_filename(health.filename)
                    health.save(os.path.join(app.config['HEALTH_UPLOADS'], filename))
                    

                    time_sent = datetime.now()

                    sender_name = session['username']

                    sermon = "/home/ekagbodjive/prcwebsite/static/books/health/" + filename

                    files = "books/health/" + filename

                    curs,connect = connection()
                    

                    input_statement = ("INSERT INTO books (sender_name,time_sent,filename,file,location,book_id) VALUES (%s,%s,%s,%s, %s)" ) 
                    data = [sender_name, time_sent,filename,files,sermon,"HEAL"]
                    curs.execute( input_statement, data)

                    connect.commit()
                    print("The process was sucessful")
                    curs.close()
                    connect.close()
                    gc.collect()

                else :
                    flash("that file type is not allowed")
                    print('that file type is not allowed')
                    return render_template('404.html')


                
            return redirect(url_for('healthbooks'))

    return render_template('healthbooks.html', name=session['admin'])


@app.route('/inspirationalbooks/', methods=["GET","POST"]) 
@logged_in_required
def inspirationalbooks():
    if request.method =='POST':

        if request.files:
            inspirational = request.files['inspirationalbooks']

            if inspirational.filename !='':

                if allowed_book_types(inspirational.filename):

                    filename = secure_filename(inspirational.filename)
                    inspirational.save(os.path.join(app.config['INSPIRATION_UPLOADS'], filename))
                    

                    time_sent = datetime.now()

                    sender_name = session['username']

                    sermon = "/home/ekagbodjive/prcwebsite/static/books/inspirationalbooks/" + filename

                    files = "/static/books/inspirationalbooks/" + filename

                    curs,connect = connection()
                    

                    input_statement = ("INSERT INTO books (sender_name,time_sent,filename,file,location,book_id) VALUES (%s,%s,%s,%s,%s, %s)" ) 
                    data = [sender_name, time_sent,filename,files,sermon, "INS"]
                    curs.execute( input_statement, data)

                    connect.commit()
                    print("The process was sucessful")
                    curs.close()
                    connect.close()
                    gc.collect()

                else :
                    flash("that file type is not allowed")
                    print('that file type is not allowed')
                    return render_template('404.html')


                
            return redirect(url_for('inspirationalbooks'))

    return render_template('inspirationalbooks.html', name=session['admin'])




@app.route('/sign_up_page/',methods=["GET","POST"])

def sign_up_page():

        if request.method == "POST":

            #taking in personal info

            session["firstname"] = request.form['firstname']
            session["lastname"] = request.form['lastname']

            session["day"] = request.form['day']
            session["month"] = request.form['month']
            session["year"] = request.form['year']

            session["sex"] = request.form['sex']

            session["contact"] = request.form['contact']

            session["marital_status"] = request.form['marry']
            
            session["username"] = request.form['username']

            session["email"] = request.form['email']


            bcrypt = Bcrypt()

            session["password"] = bcrypt.generate_password_hash(request.form['password'])

            curs,connect = connection()

            username = session["username"]
            email = session["email"]
            # checking if the username matches that of another person
        

            check_name = curs.execute("SELECT * FROM users WHERE username = %s ", [username] )

            connect.commit()
            print("The process was sucessful")
            curs.close()
            connect.close()
            gc.collect()

            if int(check_name) > 0:
                flash("Username already used,please choose another one")
                return render_template('sign_up_page.html')

            else:
                return redirect(url_for('confirm_email'))


            
        return render_template("sign_up_page.html")




@app.route('/ed_profile/', methods=["GET","POST"])
def ed_profile():

        if request.method =="POST":

            firstname = request.form['firstname']
            lastname = request.form['lastname']

            day = request.form['day']
            month = request.form['month']
            year = request.form['year']

            sex = request.form['sex']

            marital_status = request.form['marry']
            
            username = request.form['username']

            email = request.form['email']
            # info on the date the church was joined
            day_joined_church = request.form['day']
            month_joined_church = request.form['month']
            year_joined_church = request.form['year']

            #info on the the date of baptism 

            day_of_baptism = request.form['day_of_baptism']
            month_of_baptism = request.form['month_of_baptism']
            year_of_baptism = request.form['year_of_baptism']


            # info on department and positions held
            department = request.form['dept']
            position = request.form['position']

            department_1 = request.form['depart']
            position_1 = request.form['pos']

            #info on the service you attend
            service = request.form['service']
            status = request.form['status']

            # personal info
            location = request.form['location']
            house_number = request.form['house']
            home_town = request.form['home_town']

            update = session['username']
            
            curs,connect = connection()

                # updating the table
            # curs.execute("SELECT day_joined_church,month_joined_church,year_joined_church,department,position,department_1,postion_1,service,status,location,house_number,home_town] FROM users WHERE username = (%s)", [update])
            curs.execute("UPDATE users SET firstname = (%s),lastname = (%s), day = (%s), month= (%s), year = (%s), sex = (%s), marital_status = (%s), username = (%s), email, day_joined_church = (%s),month_joined_church= (%s),year_joined_church= (%s),day_of_baptism=(%s),month_of_baptism=(%s),year_of_baptism=(%s),department= (%s),postion= (%s),department_1= (%s),position_1= (%s),service= (%s),status= (%s),location= (%s),house_number= (%s),home_town= (%s) WHERE username = (%s)", [day_joined_church,month_joined_church,year_joined_church,day_of_baptism,month_of_baptism,year_of_baptism,department,position,department_1,position_1,service,status,location,house_number,home_town,session["username"]])
            print('it was successfull')
            connect.commit()
            curs.close()
            connect.close()
            gc.collect()
            return redirect(url_for('home'))


        return render_template('ed_profile.html', name=session['logged_in'])




@app.route('/spiritual_life1/',methods=["GET","POST"])
@login_required
def spiritual_life1():
    error=''
    try:
        curs, connect = connection()
        curs.execute('SELECT id_number, filename,file FROM books where book_id= "SPIR"')
        data = curs.fetchall()

        return render_template('spiritual_life1.html',  value = data)

    except Exception as e:
        return render_template('spiritual_life1.html', name=session['logged_in'])
    

@app.route('/sundayschool/',methods=["GET","POST"])
@login_required
def sundayschool():
    error=''
    try:
        curs, connect = connection()
        curs.execute('SELECT id_number, filename,file FROM books where book_id= "SSCH"')
        data = curs.fetchall()
        return render_template('sundayschool.html',  value = data)

    except Exception as e:
        return render_template('sundayschool.html', name=session['logged_in'])
    

@app.route('/teen/',methods=["GET","POST"])
@login_required
def teen():
    try:
        curs, connect = connection()
        curs.execute('SELECT * from announcement where Dept_code="TM"')
        data = curs.fetchall()
        
        data = reversed(data)

        return render_template('teen.html', name=session['logged_in'],value = data)

    except Exception as e:
        return render_template('teen.html', name=session['logged_in'])

@app.route('/women/',methods=["GET","POST"])
@login_required
def women():
    try:
        curs, connect = connection()
        curs.execute('SELECT * from announcement where Dept_code="WM"')
        data = curs.fetchall()
        
        data = reversed(data)



        return render_template('women.html', name=session['logged_in'], value = data)

    except Exception as e:
        return render_template('women.html', name=session['logged_in'])

     


@app.route('/youth/',methods=["GET","POST"])
@login_required
def youth():
    try:
        curs, connect = connection()
        curs.execute('SELECT * FROM announcement where Dept_code="YM"')
        data = curs.fetchall()
        
        data = reversed(data)



        return render_template('youth.html',name=session['logged_in'],value = data)

    except Exception as e:
        return render_template('youth.html', name=session['logged_in'])


@app.route("/thank_you/", methods=["GET","POST"])
def thank_you():
    return render_template('thankyou.html')

@app.route("/thank_you1/", methods=["GET","POST"])
def thank_you1():
    return render_template('thankyou1.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html')


# @socketio.on('message')
# def message(data):
#     # print(f"\n\n {data}\n\n ")
#     send({'msg':data['msg'], 'username':data['username'], 'time_stamp':strftime('%b-%d %I:%M%p ', localtime()) })


# @socketio.on('join')
# def join(data):

#     join_room(data['room'])
#     send({'msg':data['username'] + ' has joined the chatroom' } )


# @socketio.on('leave')
# def leave(data):

#     leave_room(data['room'])
#     send({'msg':data['username'] + ' has left the chatroom' })




if __name__ =="__main__":
    socketio.run(app, debug=True)

if __name__== "__main__":
    app.run(debug=True)

