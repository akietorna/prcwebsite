from flask import Flask
from flask_mysqldb import MySQLdb
import MySQLdb.cursors


#app=Flask(__name__)


#app.config['SECRET_KEY'] = 'hispresence123@'

def connection():
    connect = MySQLdb.connect( host = 'ekagbodjive.mysql.pythonanywhere-services.com',
                              user = 'ekagbodjive',
                              passwd = 'hispresence123@',
                              db = "ekagbodjive$default")
# innitializing the cursor 
    curs = connect.cursor()

    return curs , connect





