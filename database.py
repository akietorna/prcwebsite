from flask import Flask
from flask_mysqldb import MySQLdb
import MySQLdb.cursors


#app=Flask(__name__)


#app.config['SECRET_KEY'] = 'hispresence123@'

def connection():
    connect = MySQLdb.connect(HOST = "ekagbodjive.mysql.pythonanywhere-services.com",
                              USER = "ekagbodjive",
                              PASSWD = "hispresence123@",
                              DB = "prcwebsite")
# innitializing the cursor 
    curs = connect.cursor()

    return curs , connect





