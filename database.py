from flask import Flask
from flask_mysqldb import MySQLdb
import MySQLdb.cursors


#app=Flask(__name__)


#app.config['SECRET_KEY'] = 'hispresence123@'

def connection():
    connect = MySQLdb.connect(host = "127.0.0.1",
                              user = "ekagbodjive$default",
                              passwd = "hispresence123@",
                              db = "prcwebsite")
# innitializing the cursor 
    curs = connect.cursor()

    return curs , connect





