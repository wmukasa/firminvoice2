from datetime import datetime, date
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, PasswordField, SubmitField, 
                    FieldList,FormField,BooleanField,TextAreaField,Form,IntegerField, SelectField,)
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from wtforms import validators
from flask_login import current_user
from wtforms.widgets import Input
from firm.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    designation = StringField('Designation',
                        validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])   
    submit = SubmitField('Sign Up')

    def validate_username(self,username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')
 
    def validate_email(self,email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('SIGN IN')
    
class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    designation = StringField('Designation',
                        validators=[DataRequired()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg','png'])])
  
    submit = SubmitField('Update')

    def validate_username(self,username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')
 
    def validate_email(self,email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')  

class LapForm(Form):
    """Subform.

    CSRF is disabled for this subform (using `Form` as parent class) because
    it is never used by itself.
   
    item_name= StringField('Item name',validators=[validators.InputRequired(), validators.Length(max=100)])
    """ 
  
    notes= TextAreaField('Description',validators=[validators.InputRequired(), validators.Length(max=255)])
    disbursements =StringField('Disbursements Fees/Ug.shs')
    professional_fees =StringField('Professional Fees/Ug.shs')
    amount = StringField('Amount/Ug.shs',validators=[validators.InputRequired(), validators.Length(min=2,max=20)])

    

class MainForm(FlaskForm):
    """Parent form."""
    invoice_title= StringField('Title')
    name_to= StringField('Name of the client', validators=[validators.InputRequired(), validators.Length(max=100)])
    address_to = StringField('Address to',validators=[validators.InputRequired(), validators.Length(max=100)])
    email_to  = StringField('Email if any')  
    telephone_to = StringField('Telephone if any')
    box_number_to = StringField('P.O.BOX if any')
    terms = SelectField('Payment Terms',
                choices=[('none', 'NONE'), ('Due on Receipt', 'Due on Receipt'),('cheque', 'Cheque'),('today', 'Today'),('Mobile/Airtel Money', 'Mobile/Airtel Money')])

    issue_date = StringField('Issue Date/MM/DD/YR', validators=[validators.InputRequired(), validators.Length(max=20)])
    due_date= StringField('Due Date/MM/DD/YR',validators=[validators.InputRequired(), validators.Length(max=20)])
    vat = StringField('Tax Invoice Number ')
    laps = FieldList(
        FormField(LapForm),
        min_entries=1,
        max_entries=5
    )

class Invoice_Items(FlaskForm):
    name_to= StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    address_to = StringField('Address',validators=[DataRequired(), Length(min=2, max=20)])
    email_to  = StringField('Email if any')  
    telephone_to = StringField('Telephone if any')
    box_number_to = StringField('P.O.BOX if any')
    terms = SelectField('Payment Terms',
                choices=[('none', 'NONE'), ('due', 'Due on Receipt'),('cheque', 'Cheque'),('today', 'Today'),('Mobile/Airtel Money', 'Mobile/Airtel Money')])
    issue_date = StringField('Issue Date', validators=[DataRequired()])
    due_date= StringField('Due Date',validators=[DataRequired(), Length(min=2, max=20)])
    vat = StringField('Tax Invoice Number ')

  
    notes= TextAreaField('Description',validators=[validators.InputRequired(), validators.Length(max=255)])
    disbursements =StringField('Disbursements Fees/Ug.shs')
    professional_fees =StringField('Professional Fees/Ug.shs')
    amount = StringField('Amount/Ug.shs',validators=[validators.InputRequired(), validators.Length(min=2,max=20)])

    notes2= TextAreaField('Description',validators=[validators.InputRequired(), validators.Length(max=255)])
    disbursements2 =StringField('Disbursements Fees/Ug.shs')
    professional_fees2 =StringField('Professional Fees/Ug.shs')
    amount2 = StringField('Amount/Ug.shs',validators=[validators.InputRequired(), validators.Length(min=2,max=20)])

    submit = SubmitField('Update')
class Invoice_Items2(FlaskForm):
    name_to= StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    address_to = StringField('Address',validators=[DataRequired(), Length(min=2, max=20)])
    email_to  = StringField('Email if any')  
    telephone_to = StringField('Telephone if any')
    box_number_to = StringField('P.O.BOX if any')
    terms = SelectField('Payment Terms',
                choices=[('none', 'NONE'), ('due', 'Due on Receipt'),('cheque', 'Cheque'),('today', 'Today'),('Mobile/Airtel Money', 'Mobile/Airtel Money')])
    issue_date = StringField('Issue Date', validators=[DataRequired()])
    due_date= StringField('Due Date',validators=[DataRequired(), Length(min=2, max=20)])
    vat = StringField('Tax Invoice Number ')

  
    notes= TextAreaField('Description',validators=[validators.InputRequired(), validators.Length(max=255)])
    disbursements =StringField('Disbursements Fees/Ug.shs')
    professional_fees =StringField('Professional Fees/Ug.shs')
    amount = StringField('Amount/Ug.shs',validators=[validators.InputRequired(), validators.Length(min=2,max=20)])

    notes2= TextAreaField('Description',validators=[validators.InputRequired(), validators.Length(max=255)])
    disbursements2 =StringField('Disbursements Fees/Ug.shs')
    professional_fees2 =StringField('Professional Fees/Ug.shs')
    amount2 = StringField('Amount/Ug.shs',validators=[validators.InputRequired(), validators.Length(min=2,max=20)])
    
    notes3= TextAreaField('Description',validators=[validators.InputRequired(), validators.Length(max=255)])
    disbursements3 =StringField('Disbursements Fees/Ug.shs')
    professional_fees3 =StringField('Professional Fees/Ug.shs')
    amount3 = StringField('Amount/Ug.shs',validators=[validators.InputRequired(), validators.Length(min=2,max=20)])
    
    submit = SubmitField('Update')
class Invoice_Items3(FlaskForm):
    name_to= StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    address_to = StringField('Address',validators=[DataRequired(), Length(min=2, max=20)])
    email_to  = StringField('Email if any')  
    telephone_to = StringField('Telephone if any')
    box_number_to = StringField('P.O.BOX if any')
    terms = SelectField('Payment Terms',
                choices=[('none', 'NONE'), ('due', 'Due on Receipt'),('cheque', 'Cheque'),('today', 'Today'),('Mobile/Airtel Money', 'Mobile/Airtel Money')])
    issue_date = StringField('Issue Date', validators=[DataRequired()])
    due_date= StringField('Due Date',validators=[DataRequired(), Length(min=2, max=20)])
    vat = StringField('Tax Invoice Number ')

  
    notes= TextAreaField('Description',validators=[validators.InputRequired(), validators.Length(max=255)])
    disbursements =StringField('Disbursements Fees/Ug.shs')
    professional_fees =StringField('Professional Fees/Ug.shs')
    amount = StringField('Amount/Ug.shs',validators=[validators.InputRequired(), validators.Length(min=2,max=20)])

    notes2= TextAreaField('Description',validators=[validators.InputRequired(), validators.Length(max=255)])
    disbursements2 =StringField('Disbursements Fees/Ug.shs')
    professional_fees2 =StringField('Professional Fees/Ug.shs')
    amount2 = StringField('Amount/Ug.shs',validators=[validators.InputRequired(), validators.Length(min=2,max=20)])
    
    notes3= TextAreaField('Description',validators=[validators.InputRequired(), validators.Length(max=255)])
    disbursements3 =StringField('Disbursements Fees/Ug.shs')
    professional_fees3 =StringField('Professional Fees/Ug.shs')
    amount3 = StringField('Amount/Ug.shs',validators=[validators.InputRequired(), validators.Length(min=2,max=20)])
    
    notes4= TextAreaField('Description',validators=[validators.InputRequired(), validators.Length(max=255)])
    disbursements4 =StringField('Disbursements Fees/Ug.shs')
    professional_fees4 =StringField('Professional Fees/Ug.shs')
    amount4 = StringField('Amount/Ug.shs',validators=[validators.InputRequired(), validators.Length(min=2,max=20)])
    submit = SubmitField('Update')
class Invoice_Items4(FlaskForm):
    name_to= StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    address_to = StringField('Address',validators=[DataRequired(), Length(min=2, max=20)])
    email_to  = StringField('Email if any')  
    telephone_to = StringField('Telephone if any')
    box_number_to = StringField('P.O.BOX if any')
    terms = SelectField('Payment Terms',
                choices=[('none', 'NONE'), ('due', 'Due on Receipt'),('cheque', 'Cheque'),('today', 'Today'),('Mobile/Airtel Money', 'Mobile/Airtel Money')])
    issue_date = StringField('Issue Date', validators=[DataRequired()])
    due_date= StringField('Due Date',validators=[DataRequired(), Length(min=2, max=20)])
    vat = StringField('Tax Invoice Number ')

  
    notes= TextAreaField('Description',validators=[validators.InputRequired(), validators.Length(max=255)])
    disbursements =StringField('Disbursements Fees/Ug.shs')
    professional_fees =StringField('Professional Fees/Ug.shs')
    amount = StringField('Amount/Ug.shs',validators=[validators.InputRequired(), validators.Length(min=2,max=20)])

    notes2= TextAreaField('Description',validators=[validators.InputRequired(), validators.Length(max=255)])
    disbursements2 =StringField('Disbursements Fees/Ug.shs')
    professional_fees2 =StringField('Professional Fees/Ug.shs')
    amount2 = StringField('Amount/Ug.shs',validators=[validators.InputRequired(), validators.Length(min=2,max=20)])
    
    notes3= TextAreaField('Description',validators=[validators.InputRequired(), validators.Length(max=255)])
    disbursements3 =StringField('Disbursements Fees/Ug.shs')
    professional_fees3 =StringField('Professional Fees/Ug.shs')
    amount3 = StringField('Amount/Ug.shs',validators=[validators.InputRequired(), validators.Length(min=2,max=20)])
    
    notes4= TextAreaField('Description',validators=[validators.InputRequired(), validators.Length(max=255)])
    disbursements4 =StringField('Disbursements Fees/Ug.shs')
    professional_fees4 =StringField('Professional Fees/Ug.shs')
    amount4 = StringField('Amount/Ug.shs',validators=[validators.InputRequired(), validators.Length(min=2,max=20)])
    
    
    notes5= TextAreaField('Description',validators=[validators.InputRequired(), validators.Length(max=255)])
    disbursements5 =StringField('Disbursements Fees/Ug.shs')
    professional_fees5 =StringField('Professional Fees/Ug.shs')
    amount5 = StringField('Amount/Ug.shs',validators=[validators.InputRequired(), validators.Length(min=2,max=20)])
    submit = SubmitField('Update')