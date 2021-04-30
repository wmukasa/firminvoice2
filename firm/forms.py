from datetime import datetime, date
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, PasswordField, SubmitField,DateTimeField,
                    FieldList,FormField,BooleanField,TextAreaField,Form,IntegerField, SelectField,)
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from wtforms import validators
from flask_login import current_user
from wtforms.widgets import Input
from wtforms.fields.html5 import DateField
from firm.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=120)])
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
                           validators=[DataRequired(), Length(min=2, max=120)])
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

class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Resquest Password Reset')

    def validate_email(self,email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first. ') 

class ResetPasswordForm(FlaskForm):   
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset password')

class LapForm(Form):

    prof_heading = TextAreaField(
        'PROFESSIONAL FEES HEADING',
         validators=[validators.InputRequired(),validators.Length(max=255)]
    )
    prof_sub1= TextAreaField(
        'professional subheading1',
        validators=[validators.Length(max=100)]
    )
    prof_sub2= TextAreaField(
        'professional subheading2',[validators.Length(max=100)]
    )
    prof_sub3= TextAreaField(
        'professional subheading3',[validators.Length(max=100)]
    )
    prof_sub4= TextAreaField(
        'professional subheading4',[validators.Length(max=100)]
    )
    prof_sub5= TextAreaField(
        'professional subheading5',[validators.Length(max=100)]
    )
class MainForm(FlaskForm):
    """Parent form."""
    invoice_title= StringField('Title')
    name_to= StringField('Name of the client', validators=[validators.InputRequired(), validators.Length(max=100)])
    company_name = StringField('Company if any')
    address_to = StringField('Address to',validators=[validators.InputRequired(), validators.Length(max=100)])
    email_to  = StringField('Email if any')  
    telephone_to = StringField('Telephone if any')
    box_number_to = StringField('P.O.BOX if any')
    terms = SelectField('Payment Terms',
                choices=[('none', 'NONE'), ('Due on Receipt', 'Due on Receipt'),('cheque', 'Cheque'),('today', 'Today'),('Mobile/Airtel Money', 'Mobile/Airtel Money')])

    issue_date= DateField('Issue Date/YR/MM/DD', format="%Y-%m-%d",default=datetime.now, validators=[validators.DataRequired()])
    due_date= DateField('Due Date/YR/MM/DD', format="%Y-%m-%d",default=datetime.now, validators=[validators.DataRequired()])
    vat = StringField('Tax Invoice Number ')
    #the added infor
    professional_amount=StringField(
        'Professional amount',validators=[validators.InputRequired(), validators.Length(min=2,max=60)])
    laps = FieldList(
        FormField(LapForm),
        min_entries=1,
        max_entries=8
    )
class DisbursementForm(Form):

    disb_heading = TextAreaField(
        'DISBURSEMENT HEADING FEES',
         validators=[validators.Length(max=255)]
    )
    disb_sub1= TextAreaField(
        'Disbursement subheading1',
        validators=[ validators.Length(max=100)]
    )
    disb_sub2= TextAreaField(
        'Disbursement subheading2',[validators.Length(max=100)]
    )
    disb_sub3= TextAreaField(
        'Disbursement subheading3',[validators.Length(max=100)]
    )

    disbursement_amount=StringField('Disbursement amount' )
class DisbursementMainForm(FlaskForm):

    laps2 = FieldList(
        FormField(DisbursementForm),
        min_entries=1,
        max_entries=20
    )

class Invoice_Items(FlaskForm):
    name_to= StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    company_name = StringField('Company if any')
    address_to = StringField('Address',validators=[DataRequired(), Length(min=2, max=20)])
    email_to  = StringField('Email if any')  
    telephone_to = StringField('Telephone if any')
    box_number_to = StringField('P.O.BOX if any')
    terms = SelectField('Payment Terms',
                choices=[('none', 'NONE'), ('due', 'Due on Receipt'),('cheque', 'Cheque'),('today', 'Today'),('Mobile/Airtel Money', 'Mobile/Airtel Money')])
    issue_date= DateField('Issue Date/YR/MM/DD', format="%Y-%m-%d",default=datetime.now, validators=[validators.DataRequired()])
    due_date= DateField('Due Date/YR/MM/DD', format="%Y-%m-%d",default=datetime.now, validators=[validators.DataRequired()])
    vat = StringField('Tax Invoice Number ')

    professional_amount=StringField('Professional amount/Ug.shs')
    prof_heading =TextAreaField('Professional Description')
    prof_sub1 =StringField('professional subheading1')
    prof_sub2 =TextAreaField('professional subheading2')
    prof_sub3 =StringField('professional subheading3')
    prof_sub4 =StringField('professional subheading4')
    prof_sub5 =StringField('professional subheading5')

    disbursement_amount =StringField('Disbursement_amount/Ug.shs')
    disb_heading =TextAreaField('Professional Description')
    disb_sub1=StringField('professional subheading1')
    disb_sub2=StringField('professional subheading2')
    disb_sub3=StringField('professional subheading3')
    
    submit = SubmitField('Update')


class Invoice_Items2(FlaskForm):
    name_to= StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    company_name = StringField('Company if any')
    address_to = StringField('Address',validators=[DataRequired(), Length(min=2, max=20)])
    email_to  = StringField('Email if any')  
    telephone_to = StringField('Telephone if any')
    box_number_to = StringField('P.O.BOX if any')
    terms = SelectField('Payment Terms',
                choices=[('none', 'NONE'), ('due', 'Due on Receipt'),('cheque', 'Cheque'),('today', 'Today'),('Mobile/Airtel Money', 'Mobile/Airtel Money')])
    issue_date= DateField('Issue Date/YR/MM/DD', format="%Y-%m-%d",default=datetime.now, validators=[validators.DataRequired()])
    due_date= DateField('Due Date/YR/MM/DD', format="%Y-%m-%d",default=datetime.now, validators=[validators.DataRequired()])
    vat = StringField('Tax Invoice Number ')

    professional_desc =TextAreaField('Professional Description')
    professional_amount =StringField('Professional Amount/Ug.shs')
    disbursements_desc =TextAreaField('Disbursements Description')
    disbursements_amount =StringField('Disbursements Amount/Ug.shs')

    professional_desc2 =TextAreaField('Professional Description')
    professional_amount2 =StringField('Professional Amount/Ug.shs')
    disbursements_desc2 =TextAreaField('Disbursements Description')
    disbursements_amount2 =StringField('Disbursements Amount/Ug.shs')
    
    professional_desc3 =TextAreaField('Professional Description')
    professional_amount3 =StringField('Professional Amount/Ug.shs')
    disbursements_desc3 =TextAreaField('Disbursements Description')
    disbursements_amount3 =StringField('Disbursements Amount/Ug.shs')
    submit = SubmitField('Update')
class Invoice_Items3(FlaskForm):
    name_to= StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    company_name = StringField('Company if any')
    address_to = StringField('Address',validators=[DataRequired(), Length(min=2, max=20)])
    email_to  = StringField('Email if any')  
    telephone_to = StringField('Telephone if any')
    box_number_to = StringField('P.O.BOX if any')
    terms = SelectField('Payment Terms',
                choices=[('none', 'NONE'), ('due', 'Due on Receipt'),('cheque', 'Cheque'),('today', 'Today'),('Mobile/Airtel Money', 'Mobile/Airtel Money')])
    issue_date= DateField('Issue Date/YR/MM/DD', format="%Y-%m-%d",default=datetime.now, validators=[validators.DataRequired()])
    due_date= DateField('Due Date/YR/MM/DD', format="%Y-%m-%d",default=datetime.now, validators=[validators.DataRequired()])
    vat = StringField('Tax Invoice Number ')

  
    professional_desc =TextAreaField('Professional Description')
    professional_amount =StringField('Professional Amount/Ug.shs')
    disbursements_desc =TextAreaField('Disbursements Description')
    disbursements_amount =StringField('Disbursements Amount/Ug.shs')

    professional_desc2 =TextAreaField('Professional Description')
    professional_amount2 =StringField('Professional Amount/Ug.shs')
    disbursements_desc2 =TextAreaField('Disbursements Description')
    disbursements_amount2 =StringField('Disbursements Amount/Ug.shs')
    
    professional_desc3 =TextAreaField('Professional Description')
    professional_amount3 =StringField('Professional Amount/Ug.shs')
    disbursements_desc3 =TextAreaField('Disbursements Description')
    disbursements_amount3 =StringField('Disbursements Amount/Ug.shs')

    professional_desc4 =TextAreaField('Professional Description')
    professional_amount4 =StringField('Professional Amount/Ug.shs')
    disbursements_desc4 =TextAreaField('Disbursements Description')
    disbursements_amount4 =StringField('Disbursements Amount/Ug.shs')
    submit = SubmitField('Update')
class Invoice_Items4(FlaskForm):
    name_to= StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    company_name = StringField('Company if any')
    address_to = StringField('Address',validators=[DataRequired(), Length(min=2, max=20)])
    email_to  = StringField('Email if any')  
    telephone_to = StringField('Telephone if any')
    box_number_to = StringField('P.O.BOX if any')
    terms = SelectField('Payment Terms',
                choices=[('none', 'NONE'), ('due', 'Due on Receipt'),('cheque', 'Cheque'),('today', 'Today'),('Mobile/Airtel Money', 'Mobile/Airtel Money')])
    issue_date= DateField('Issue Date/YR/MM/DD', format="%Y-%m-%d",default=datetime.now, validators=[validators.DataRequired()])
    due_date= DateField('Due Date/YR/MM/DD', format="%Y-%m-%d",default=datetime.now, validators=[validators.DataRequired()])
    vat = StringField('Tax Invoice Number ')

  
    professional_desc =TextAreaField('Professional Description')
    professional_amount =StringField('Professional Amount/Ug.shs')
    disbursements_desc =TextAreaField('Disbursements Description')
    disbursements_amount =StringField('Disbursements Amount/Ug.shs')

    professional_desc2 =TextAreaField('Professional Description')
    professional_amount2 =StringField('Professional Amount/Ug.shs')
    disbursements_desc2 =TextAreaField('Disbursements Description')
    disbursements_amount2 =StringField('Disbursements Amount/Ug.shs')
    
    professional_desc3 =TextAreaField('Professional Description')
    professional_amount3 =StringField('Professional Amount/Ug.shs')
    disbursements_desc3 =TextAreaField('Disbursements Description')
    disbursements_amount3 =StringField('Disbursements Amount/Ug.shs')

    professional_desc4 =TextAreaField('Professional Description')
    professional_amount4 =StringField('Professional Amount/Ug.shs')
    disbursements_desc4 =TextAreaField('Disbursements Description')
    disbursements_amount4 =StringField('Disbursements Amount/Ug.shs')
    
    
    professional_desc5 =TextAreaField('Professional Description')
    professional_amount5 =StringField('Professional Amount/Ug.shs')
    disbursements_desc5 =TextAreaField('Disbursements Description')
    disbursements_amount5 =StringField('Disbursements Amount/Ug.shs')

    submit = SubmitField('Update')

class Invoice_Items5(FlaskForm):
    name_to= StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    company_name = StringField('Company if any')
    address_to = StringField('Address',validators=[DataRequired(), Length(min=2, max=20)])
    email_to  = StringField('Email if any')  
    telephone_to = StringField('Telephone if any')
    box_number_to = StringField('P.O.BOX if any')
    terms = SelectField('Payment Terms',
                choices=[('none', 'NONE'), ('due', 'Due on Receipt'),('cheque', 'Cheque'),('today', 'Today'),('Mobile/Airtel Money', 'Mobile/Airtel Money')])
    issue_date= DateField('Issue Date/YR/MM/DD', format="%Y-%m-%d",default=datetime.now, validators=[validators.DataRequired()])
    due_date= DateField('Due Date/YR/MM/DD', format="%Y-%m-%d",default=datetime.now, validators=[validators.DataRequired()])
    vat = StringField('Tax Invoice Number ')

    professional_desc =TextAreaField('Professional Description')
    professional_amount =StringField('Professional Amount/Ug.shs')
    disbursements_desc =TextAreaField('Disbursements Description')
    disbursements_amount =StringField('Disbursements Amount/Ug.shs')

    professional_desc2 =TextAreaField('Professional Description')
    professional_amount2 =StringField('Professional Amount/Ug.shs')
    disbursements_desc2 =TextAreaField('Disbursements Description')
    disbursements_amount2 =StringField('Disbursements Amount/Ug.shs')
    
    professional_desc3 =TextAreaField('Professional Description')
    professional_amount3 =StringField('Professional Amount/Ug.shs')
    disbursements_desc3 =TextAreaField('Disbursements Description')
    disbursements_amount3 =StringField('Disbursements Amount/Ug.shs')

    professional_desc4 =TextAreaField('Professional Description')
    professional_amount4 =StringField('Professional Amount/Ug.shs')
    disbursements_desc4 =TextAreaField('Disbursements Description')
    disbursements_amount4 =StringField('Disbursements Amount/Ug.shs')
    
    professional_desc5 =TextAreaField('Professional Description')
    professional_amount5 =StringField('Professional Amount/Ug.shs')
    disbursements_desc5 =TextAreaField('Disbursements Description')
    disbursements_amount5 =StringField('Disbursements Amount/Ug.shs')
   
      
    professional_desc6 =TextAreaField('Professional Description')
    professional_amount6 =StringField('Professional Amount/Ug.shs')
    disbursements_desc6 =TextAreaField('Disbursements Description')
    disbursements_amount6 =StringField('Disbursements Amount/Ug.shs')
    
    submit = SubmitField('Update')

class Invoice_Items6(FlaskForm):
    name_to= StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    company_name = StringField('Company if any')
    address_to = StringField('Address',validators=[DataRequired(), Length(min=2, max=20)])
    email_to  = StringField('Email if any')  
    telephone_to = StringField('Telephone if any')
    box_number_to = StringField('P.O.BOX if any')
    terms = SelectField('Payment Terms',
                choices=[('none', 'NONE'), ('due', 'Due on Receipt'),('cheque', 'Cheque'),('today', 'Today'),('Mobile/Airtel Money', 'Mobile/Airtel Money')])
    issue_date= DateField('Issue Date/YR/MM/DD', format="%Y-%m-%d",default=datetime.now, validators=[validators.DataRequired()])
    due_date= DateField('Due Date/YR/MM/DD', format="%Y-%m-%d",default=datetime.now, validators=[validators.DataRequired()])
    vat = StringField('Tax Invoice Number ')

  
    professional_desc =TextAreaField('Professional Description')
    professional_amount =StringField('Professional Amount/Ug.shs')
    disbursements_desc =TextAreaField('Disbursements Description')
    disbursements_amount =StringField('Disbursements Amount/Ug.shs')

    professional_desc2 =TextAreaField('Professional Description')
    professional_amount2 =StringField('Professional Amount/Ug.shs')
    disbursements_desc2 =TextAreaField('Disbursements Description')
    disbursements_amount2 =StringField('Disbursements Amount/Ug.shs')
    
    professional_desc3 =TextAreaField('Professional Description')
    professional_amount3 =StringField('Professional Amount/Ug.shs')
    disbursements_desc3 =TextAreaField('Disbursements Description')
    disbursements_amount3 =StringField('Disbursements Amount/Ug.shs')

    professional_desc4 =TextAreaField('Professional Description')
    professional_amount4 =StringField('Professional Amount/Ug.shs')
    disbursements_desc4 =TextAreaField('Disbursements Description')
    disbursements_amount4 =StringField('Disbursements Amount/Ug.shs')
    
    professional_desc5 =TextAreaField('Professional Description')
    professional_amount5 =StringField('Professional Amount/Ug.shs')
    disbursements_desc5 =TextAreaField('Disbursements Description')
    disbursements_amount5 =StringField('Disbursements Amount/Ug.shs')
   
      
    professional_desc6 =TextAreaField('Professional Description')
    professional_amount6 =StringField('Professional Amount/Ug.shs')
    disbursements_desc6 =TextAreaField('Disbursements Description')
    disbursements_amount6 =StringField('Disbursements Amount/Ug.shs')
    
    professional_desc7 =TextAreaField('Professional Description')
    professional_amount7 =StringField('Professional Amount/Ug.shs')
    disbursements_desc7 =TextAreaField('Disbursements Description')
    disbursements_amount7 =StringField('Disbursements Amount/Ug.shs')
    submit = SubmitField('Update')

class Invoice_Items7(FlaskForm):
    name_to= StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    company_name = StringField('Company if any')
    address_to = StringField('Address',validators=[DataRequired(), Length(min=2, max=20)])
    email_to  = StringField('Email if any')  
    telephone_to = StringField('Telephone if any')
    box_number_to = StringField('P.O.BOX if any')
    terms = SelectField('Payment Terms',
                choices=[('none', 'NONE'), ('due', 'Due on Receipt'),('cheque', 'Cheque'),('today', 'Today'),('Mobile/Airtel Money', 'Mobile/Airtel Money')])
    issue_date= DateField('Issue Date/YR/MM/DD', format="%Y-%m-%d",default=datetime.now, validators=[validators.DataRequired()])
    due_date= DateField('Due Date/YR/MM/DD', format="%Y-%m-%d",default=datetime.now, validators=[validators.DataRequired()])
    vat = StringField('Tax Invoice Number ')

    professional_desc =TextAreaField('Professional Description')
    professional_amount =StringField('Professional Amount/Ug.shs')
    disbursements_desc =TextAreaField('Disbursements Description')
    disbursements_amount =StringField('Disbursements Amount/Ug.shs')

    professional_desc2 =TextAreaField('Professional Description')
    professional_amount2 =StringField('Professional Amount/Ug.shs')
    disbursements_desc2 =TextAreaField('Disbursements Description')
    disbursements_amount2 =StringField('Disbursements Amount/Ug.shs')
    
    professional_desc3 =TextAreaField('Professional Description')
    professional_amount3 =StringField('Professional Amount/Ug.shs')
    disbursements_desc3 =TextAreaField('Disbursements Description')
    disbursements_amount3 =StringField('Disbursements Amount/Ug.shs')

    professional_desc4 =TextAreaField('Professional Description')
    professional_amount4 =StringField('Professional Amount/Ug.shs')
    disbursements_desc4 =TextAreaField('Disbursements Description')
    disbursements_amount4 =StringField('Disbursements Amount/Ug.shs')
    
    professional_desc5 =TextAreaField('Professional Description')
    professional_amount5 =StringField('Professional Amount/Ug.shs')
    disbursements_desc5 =TextAreaField('Disbursements Description')
    disbursements_amount5 =StringField('Disbursements Amount/Ug.shs')
   
      
    professional_desc6 =TextAreaField('Professional Description')
    professional_amount6 =StringField('Professional Amount/Ug.shs')
    disbursements_desc6 =TextAreaField('Disbursements Description')
    disbursements_amount6 =StringField('Disbursements Amount/Ug.shs')
    
    professional_desc7 =TextAreaField('Professional Description')
    professional_amount7 =StringField('Professional Amount/Ug.shs')
    disbursements_desc7 =TextAreaField('Disbursements Description')
    disbursements_amount7 =StringField('Disbursements Amount/Ug.shs')
    
    professional_desc8 =TextAreaField('Professional Description')
    professional_amount8 =StringField('Professional Amount/Ug.shs')
    disbursements_desc8 =TextAreaField('Disbursements Description')
    disbursements_amount8 =StringField('Disbursements Amount/Ug.shs')

    submit = SubmitField('Update')

class ReceiptForm(FlaskForm):
    """ReceiptForm."""
    date_created= DateField('Date', format="%Y-%m-%d",default=datetime.now)
    received_from  = StringField('Received from',validators=[validators.InputRequired(), validators.Length(max=100)])
    sum_in_words  = StringField('Sum in words',validators=[validators.InputRequired(), validators.Length(max=255)]) 
    reason = StringField('Being payment of',validators=[validators.InputRequired(), validators.Length(max=100)])
    cash_cheque = StringField('Cash/Cheque No',validators=[validators.InputRequired(), validators.Length(max=100)])
    balance = StringField('Balance')
    amount = StringField('Amount in figures', validators=[validators.InputRequired(), validators.Length(max=20)])
    
    submit = SubmitField('CreateReceipt')
    