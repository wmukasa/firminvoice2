from sqlalchemy import desc
from flask import Flask  
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)

ENV = 'prod'
if ENV =='dev':
    app.debug =True
    app.config['SECRET_KEY']='SECRET_KEY'
    app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:ndb123@localhost/henry'
    
else:
    app.debug = False
    app.config['SECRET_KEY']='SECRET_KEY'
    app.config['DATABASE_URI']=' postgres://jfzusdnclqzlji:89e5de4724ad30ac9797baf80c1f2765d456f7cf1a70845b55375c7fbae69529@ec2-34-197-141-7.compute-1.amazonaws.com:5432/d48430s2t209bt'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False

db= SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'index'
login_manager.login_message_category = 'info'

from firm import routes