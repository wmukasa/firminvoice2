from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app,abort
from firm import db,login_manager,app
from flask_login import UserMixin,current_user
from firm import admin
from flask_admin.contrib.sqla import ModelView

@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))

class User(db.Model,UserMixin):
      __tablename__ = 'users'
      id = db.Column(db.Integer, primary_key=True)
      username = db.Column(db.String(120), unique=True, nullable=False)
      email = db.Column(db.String(120), unique=True, nullable=False)
      designation = db.Column(db.String(120), nullable=False)
      image_file = db.Column(db.String(120), nullable=False, default='default.jpg')
      password = db.Column(db.String(60), nullable=False)
      is_admin = db.Column(db.Boolean,default = True)
      invoice = db.relationship('Invoice',backref='author', lazy=True)
      receipt = db.relationship('Receipt',backref='receiptAuthor', lazy=True)
      def get_reset_token(self,expires_sec = 1800):
        s = Serializer(current_app.config['SECRET_KEY'],expires_sec)
        return s.dumps({'user_id':self.id}).decode('utf-8')
      @staticmethod
      def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY']) 
        try:
          user_id = s.loads(token)['user_id']
        except:
          return None
        return User.query.get(user_id) 
      def __repr__(self):
        return f" User('{self.username}','{self.email}','{self.designation}','{self.image_file}')"

class Invoice(db.Model):
    __tablename__ = 'invoice' 
    id = db.Column(db.Integer, primary_key=True)
    #ref_number = db.Column(db.Integer,unique=True, nullable=False)
    ref_number = db.Column(db.String(),nullable=False)
    name_to = db.Column(db.String(200),  nullable=False)
    company_name = db.Column(db.String(200),  nullable=True)
    address_to = db.Column(db.String, nullable=False)

    telephone_to = db.Column(db.String, nullable=True)
    email_to = db.Column(db.String, nullable=True)
    box_number_to = db.Column(db.String, nullable=True)
    terms = db.Column(db.String,nullable=False)
    issue_date = db.Column(db.Date, nullable=False)
    due_date =db.Column(db.Date,nullable=False)
    vat = db.Column(db.String, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable= False)

    def get_last_id():

        qry = Invoice.query.order_by(Invoice.id.desc()).first()
        x = qry.id
        ym = date.today().strftime("%y%m")
        q_custom_id = "" + ym + str(x).zfill(3) + ""

        return q_custom_id

    def __init__(self,ref_number,name_to,address_to,telephone_to,company_name,email_to, box_number_to,vat,terms,issue_date,due_date,user_id):
        self.ref_number = ref_number
        self.name_to = name_to
        self.address_to = address_to
        self.telephone_to = telephone_to
        self.company_name=company_name
        self.email_to=email_to 
        self.box_number_to = box_number_to
        self.vat= vat
        self.terms=terms
        self.issue_date =issue_date
        self.due_date=due_date
        self.user_id=user_id


class InvoiceLineItem(db.Model):
    __tablename__ = 'line_items' 
    id = db.Column(db.Integer, primary_key=True)
    notes = db.Column(db.String(255), nullable=False)
    disbursements =db.Column(db.Float, default='0.0')
    professional_fees =db.Column(db.Float, default='0.0')
    amount = db.Column(db.Float, nullable=False)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
        # Relationship
    invoice = db.relationship(
        'Invoice',
        backref=db.backref('laps', lazy='dynamic', collection_class=list)

    )
class Receipt(db.Model):
    __tablename__ = 'receipts'
    id = db.Column(db.Integer, primary_key=True)
    receipt_number = db.Column(db.String(),nullable=False)
    date_created = db.Column(db.Date,default=datetime.now)
    received_from = db.Column(db.String(120), nullable=False)
    sum_in_words = db.Column(db.String(120), nullable=False)
    reason = db.Column(db.String(255), nullable=False)
    cash_cheque = db.Column(db.String(),nullable=False)
    balance = db.Column(db.String(20),nullable=False)
    amount = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable= False)

    def get_last_id():

        qry = Receipt.query.order_by(Invoice.id.desc()).first()
        x = qry.id
        ym = date.today().strftime("%y%m")
        q_custom_id = "" + ym + str(x).zfill(3) + ""

        return q_custom_id

    def __init__(self,receipt_number,date_created,received_from,sum_in_words,reason,cash_cheque,balance,amount,user_id):
        self.receipt_number = receipt_number
        self.date_created= date_created
        self.received_from = received_from
        self.sum_in_words = sum_in_words
        self.reason=reason
        self.cash_cheque = cash_cheque
        self.balance= balance
        self.amount=amount
        self.user_id=user_id
class Controller(ModelView):
  def is_accessible(self):
    if current_user.is_admin == True:
      return current_user.is_authenticated
    else:
      return abort(404)
    return current_user.is_authenticated
  def not_auth(self):
    return 'You are not authorized to access the Admin Dashboard'

admin.add_view(Controller(User,db.session))
admin.add_view(Controller(Invoice,db.session))
admin.add_view(Controller(InvoiceLineItem,db.session))
admin.add_view(Controller(Receipt,db.session))