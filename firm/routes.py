import os, sys, subprocess, platform
import pdfkit
from datetime import datetime, date
from flask import Flask,render_template,request,url_for,flash,redirect, make_response 
from firm.models import User,Invoice,InvoiceLineItem,Receipt,disbursements
from firm.forms import( RegistrationForm, LoginForm,UpdateAccountForm,ReceiptForm,RequestResetForm,
                ResetPasswordForm,Invoice_Items,LapForm,MainForm,Invoice_Items2,Invoice_Items3,
                Invoice_Items4,Invoice_Items5,Invoice_Items6,Invoice_Items7,DisbursementMainForm,
                DisbursementForm)
from sqlalchemy import desc,or_
from firm import db,bcrypt,app,mail
from flask_login import login_user,current_user,logout_user,login_required
from  flask_mail import Message

#from flask_msearch import Search
#[...]
#search = Search()
#search.init_app(app)

def _get_pdfkit_config():

    if platform.system() == 'Windows':
         return pdfkit.configuration(wkhtmltopdf=os.environ.get('WKHTMLTOPDF_BINARY', 'C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe'))
    else:
         WKHTMLTOPDF_CMD = subprocess.Popen(['which', os.environ.get('WKHTMLTOPDF_BINARY', 'wkhtmltopdf')], stdout=subprocess.PIPE).communicate()[0].strip()
         return pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_CMD)
wk_options = {
        #'page-size': 'Letter',
        #'orientation': 'landscape',
        # In order to specify command-line options that are simple toggles
        # using this dict format, we give the option the value None
        'no-outline': None,
        'disable-javascript': None,
        'encoding': 'UTF-8',
        'margin-left': '0.1cm',
        'margin-right': '0.1cm',
        'margin-top': '0.1cm',
        'margin-bottom': '0.1cm',
        'lowquality': None,
}
@app.route('/invSecondPage',methods=['GET', 'POST'])
def invoiceSecondPage():
    return render_template('invSecondPage.html',title='invSecondPage')

@app.route('/',methods=['GET', 'POST'])
@app.route("/Login",methods=['GET', 'POST'])
def index():
    #if current_user.is_authenticated:
        #return redirect(url_for('dashboard'))
    form= LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user,remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash(f'Login Unsuccessful. Please check email and password', 'danger') 
    return render_template('login.html',title='Login',form=form)

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data,email=form.email.data, designation= form.designation.data,password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created as ! You can now log in', 'success')
        return redirect(url_for('index'))
    return render_template('register.html', title='Register', form=form)
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/account",methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.designation = form.designation.data
        db.session.commit()
        flash('Your account has been updated!','success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.designation.data = current_user.designation

    return render_template('account.html', title='User account',form =form)

@app.route('/Manage Invoices')
@login_required
def dashboard():
    page = request.args.get('page',1,type=int)
    myInv = Invoice.query.order_by(Invoice.ref_number.desc()).paginate(page = page ,per_page=6)
    return render_template('dashboard.html',myInv=myInv )


@app.route("/search",methods=['GET','POST'])
def mySearch():
    page = request.args.get('page',1,type=int)
    myInv = Invoice.query.order_by(Invoice.ref_number.desc()).paginate(page = page ,per_page=6)
    if request.method =='POST' and 'tag' in request.form:
        tag = request.form["tag"]
        search = "%{}%".format(tag)
        myInv = Invoice.query.filter(or_(Invoice.name_to.like(search),
                                        Invoice.ref_number.like(search))).paginate(page=page,per_page=6)
        return render_template('dashboard.html',myInv=myInv,tag=tag)
    return render_template('dashboard.html',myInv=myInv)

@app.route('/Manage Receipts')
@login_required
def ourReceipts():
    page = request.args.get('page',1,type=int)
    #myInv = Invoice.query.paginate(page = page ,per_page=4)
    myRpt = Receipt.query.order_by(Receipt.receipt_number.desc()).paginate(page = page ,per_page=4)
    return render_template('ourReceiptPage.html',myRpt=myRpt )

@app.route('/SavedInvoice-<int:inv_id>')
@login_required
def saved_invoice(inv_id):
    subtotal_pr = 0
    subtotal_db = 0
    VAT =0
    grandtotal =0
    myPro =0
    inv = Invoice.query.filter( Invoice.id== inv_id).first()
    item = InvoiceLineItem.query.filter_by(invoice=inv).all()
    dis = disbursements.query.filter_by(invoice=inv).all()
    #VAT is only on professional price    
    VAT = (18/100)* float(inv.professional_amount)
    subtotal_pr = float(VAT+inv.professional_amount)
    for q in dis:
        subtotal_db +=float(q.disbursement_amount)
    grandtotal = subtotal_pr+subtotal_db 
    '''
    return render_template('saved_invoice.html',inv=inv,item=item,inv_id=inv_id, myPro= myPro,
                        subtotal=subtotal,grandtotal=grandtotal,VAT=VAT,len=len,title='SavedInvoice')
    '''
    return render_template('invSecondPage.html',inv=inv,item=item,inv_id=inv_id, myPro= myPro,
                        subtotal_pr=subtotal_pr,subtotal_db=subtotal_db,dis=dis,
                        grandtotal=grandtotal ,VAT=VAT,len=len,title='SavedInvoice')

@app.route('/get_pdf/<inv_id>', methods=['POST'])
@login_required
def get_pdf(inv_id,options=wk_options):
    subtotal_pr = 0   
    subtotal_db = 0
    VAT =0
    grandtotal =0
    myPro =0
    if request.method =="POST":
        inv = Invoice.query.filter( Invoice.id== inv_id).first()
        item = InvoiceLineItem.query.filter_by(invoice=inv).all()
        dis = disbursements.query.filter_by(invoice=inv).all()
        #VAT is only on professional price    
        VAT = (18/100)* float(inv.professional_amount)
        subtotal_pr = float(VAT+inv.professional_amount) 
        for q in dis:
            subtotal_db +=float(q.disbursement_amount)
        grandtotal = subtotal_pr+subtotal_db 
        #newLookInvoice.html
        rendered=render_template('testing2.html',inv=inv,item=item,inv_id=inv_id, myPro= myPro,
                        subtotal_pr=subtotal_pr,subtotal_db=subtotal_db,dis=dis,
                        grandtotal=grandtotal ,VAT=VAT,len=len)
        css = ['firm/static/css/testing.css']
        pdf = pdfkit.from_string(rendered,False,css=css,configuration=_get_pdfkit_config(),options=options)
        response = make_response(pdf)
        response.headers['Content-Type']='application/pdf'
        response.headers['Content-Disposition']='inline; filename=TaxInvoice'+inv_id+'.pdf'
        return response
    return redirect(url_for('saved_invoice'))

@app.route('/get_pdf/<inv_id>', methods=['POST'])
@login_required
def get_pdf2(inv_id,options=wk_options):
    subtotal_pr = 0   
    subtotal_db = 0
    VAT =0
    grandtotal =0
    myPro =0
    if request.method =="POST":
        inv = Invoice.query.filter( Invoice.id== inv_id).first()
        item = InvoiceLineItem.query.filter_by(invoice=inv).all()
        dis = disbursements.query.filter_by(invoice=inv).all()
        #VAT is only on professional price    
        VAT = (18/100)* float(inv.professional_amount)
        subtotal_pr = float(VAT+inv.professional_amount) 
        for q in dis:
            subtotal_db +=float(q.disbursement_amount)
        grandtotal = subtotal_pr+subtotal_db 
        #newLookInvoice.html
        rendered=render_template('newLookInvoice.html.html',inv=inv,item=item,inv_id=inv_id, myPro= myPro,
                        subtotal_pr=subtotal_pr,subtotal_db=subtotal_db,dis=dis,
                        grandtotal=grandtotal ,VAT=VAT,len=len)
        css = ['firm/static/css/testing.css']
        pdf = pdfkit.from_string(rendered,False,css=css,configuration=_get_pdfkit_config(),options=options)
        response = make_response(pdf)
        response.headers['Content-Type']='application/pdf'
        response.headers['Content-Disposition']='inline; filename=NewTaxInvoice'+inv_id+'.pdf'
        return response
    return redirect(url_for('saved_invoice'))

@app.route('/getProForma_pdf/<inv_id>', methods=['POST'])
@login_required
def getProForma_pdf(inv_id,options=wk_options):

    subtotal_pr = 0
    subtotal_db = 0
    VAT =0
    grandtotal =0
    myPro =0
    inv = Invoice.query.filter( Invoice.id== inv_id).first()

    if request.method =="POST":
        inv = Invoice.query.filter( Invoice.id== inv_id).first()
        item = InvoiceLineItem.query.filter_by(invoice=inv).all()
        dis = disbursements.query.filter_by(invoice=inv).all()
        #VAT is only on professional price    
        VAT = (18/100)* float(inv.professional_amount)
        subtotal_pr = float(VAT+inv.professional_amount) 
        for q in dis:
            subtotal_db +=float(q.disbursement_amount)
        grandtotal = subtotal_pr+subtotal_db 
        rendered=render_template('proForma2.html',inv=inv,item=item,inv_id=inv_id, myPro= myPro,
                                                subtotal_pr=subtotal_pr,subtotal_db=subtotal_db,dis=dis,
                                                grandtotal=grandtotal ,VAT=VAT,len=len)
        css = ['firm/static/css/testing.css']
        pdf = pdfkit.from_string(rendered,False,css=css,configuration=_get_pdfkit_config(),options=options)
        response = make_response(pdf)
        response.headers['Content-Type']='application/pdf'
        response.headers['Content-Disposition']='inline; filename=ProFormaInvoice'+inv_id+'.pdf'
        return response
    return redirect(url_for('saved_invoice'))

def export_pdf(request):
    id = request.POST.get('id', '')
    path_wk = r'D:\SoftWare\wkhtmltopdf\bin\wkhtmltopdf.exe' # Installation location
    config = pdfkit.configuration(wkhtmltopdf=path_wk)
    with open('test.html', 'r', encoding='utf-8') as f:
        pdfkit.from_file(f, 'invoice.pdf', configuration=config)
    file = open('test.pdf', 'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/pdf'
    response['Content-Disposition'] = 'attachment;filename="invoice.pdf"'
    return response

@app.route('/Create Invoice', methods=['GET', 'POST'])
@login_required
def create_invoice():
    #form = MainForm()
    form = MainForm()
    #template_form = LapForm(prefix='laps-_-')
    template_form = LapForm(prefix='laps-_-')

    try:
        get_id = Invoice.query.order_by(desc('id')).first()
        x: int = get_id.id + 1
        y = date.today().strftime("%y%m")
        if get_id:
            ref_number = "" + y + str(x).zfill(3) + ""
    except:
        ref_number = str(date.today().strftime("%y%m") + str(1).zfill(3))
    finally:
        if form.validate_on_submit():
                author = current_user
                ref_number = ref_number
                name_to = request.form['name_to']
                address_to = request.form['address_to']
                email_to = request.form['email_to']
                telephone_to = request.form['telephone_to']
                company_name = request.form['company_name']
                box_number_to = request.form['box_number_to']
                vat = request.form['vat']
                terms = request.form['terms']
                issue_date = request.form['issue_date']
                due_date = request.form['due_date']
                bank = request.form['bank']
                bank_branch = request.form['bank_branch']
                swift_code = request.form['swift_code']
                account_number = request.form['account_number']
                professional_amount = request.form['professional_amount']
                new_invoice = Invoice(ref_number,name_to,address_to,telephone_to,company_name,email_to,box_number_to,vat,terms,
                                        issue_date,due_date,bank,bank_branch,swift_code,account_number,professional_amount,current_user.id)
                db.session.add(new_invoice)
                for lap in form.laps.data:
                    new_lap = InvoiceLineItem(**lap)
                    # Add to race
                    new_invoice.laps.append(new_lap)
                db.session.commit()
                return redirect(url_for('disbursement'))
        #invoice = Invoice.query.all()

    return render_template(
        'invoice_items.html',
        #'creating_items.html',
        #'create_disbur.html',
        form=form,
        #invoice=invoice,
        _template=template_form
    )
@app.route('/disbursement', methods=['GET', 'POST'])
#@login_required
def disbursement():
    form = DisbursementMainForm()
    template_form = DisbursementForm(prefix='laps2-_-')
    if form.validate_on_submit():
        # Create rac
        get_id = Invoice.query.order_by(desc('id')).first()
        for lap in form.laps2.data:
            new_lap = disbursements(**lap)
            # Add to race
            #print(get_id)
            get_id.laps2.append(new_lap)
            
        #db.session.add(new_lap)
        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template(
        'disbursement.html',
        form=form,
        #races=races,
        _template=template_form
    )

#for second template during creating
@app.route('/ProformaInvoice-<int:inv_id>')
@login_required
def proform_invoice(inv_id):
    subtotal_pr = 0
    subtotal_db = 0
    VAT =0
    grandtotal =0
    myPro =0
    inv = Invoice.query.filter( Invoice.id== inv_id).first()

    print(inv.professional_amount)
    item = InvoiceLineItem.query.filter_by(invoice=inv).all()
    dis = disbursements.query.filter_by(invoice=inv).all()
    #VAT is only on professional price    
    VAT = (18/100)* float(inv.professional_amount)
    subtotal_pr = float(VAT+inv.professional_amount)
    for q in dis:
        subtotal_db +=float(q.disbursement_amount)
    grandtotal = subtotal_pr+subtotal_db 
    '''
    return render_template('proforma_invoice.html',inv=inv,item=item,VAT=VAT,myPro=myPro,
                        subtotal=subtotal,grandtotal=grandtotal,len=len,title='Pro forma Invoice')
    '''
    return render_template('proforma_invoice2.html',inv=inv,item=item,inv_id=inv_id, myPro= myPro,
                        subtotal_pr=subtotal_pr,subtotal_db=subtotal_db,dis=dis,
                        grandtotal=grandtotal ,VAT=VAT,len=len,title='Pro forma Invoice')

@app.route("/Invoice-<int:inv_id>-Update", methods=['GET', 'POST'])
@login_required
def update_invoice(inv_id):
    today = date.today()
    updt_inv = Invoice.query.get_or_404(inv_id)
    item = InvoiceLineItem.query.filter_by(invoice=updt_inv).all()
    dis = disbursements.query.filter_by(invoice=updt_inv).all()
    form1=Invoice_Items()
    try:
        get_id = Invoice.query.order_by(desc('id')).first()
        x: int = get_id.id + 1
        y = date.today().strftime("%y%m")
        if get_id:
            ref_number = "" + y + str(x).zfill(3) + ""
    except:
        ref_number = str(date.today().strftime("%y%m") + str(1).zfill(3))
    finally:

        if request.method == 'POST':
        #if form.validate_on_submit(): 
            ref_number = ref_number
            updt_inv.name_to = form1.name_to.data 
            updt_inv.address_to = form1.address_to.data 
            updt_inv.email_to = form1.email_to.data
            updt_inv.company_name = form1.company_name.data 
            updt_inv.telephone_to = form1.telephone_to.data 
            updt_inv.box_number_to = form1.box_number_to.data 
            updt_inv.vat = form1.vat.data 
            updt_inv.terms = form1.terms.data 
            updt_inv.issue_date = form1.issue_date.data
            updt_inv.due_date = form1.due_date.data 
            updt_inv.bank = form1.bank.data   
            updt_inv.bank_branch = form1.bank_branch.data   
            updt_inv.swift_code = form1.swift_code.data   
            updt_inv.account_number = form1.account_number.data     
            updt_inv.professional_amount = form1.professional_amount.data   
            for p in item: 
                p.prof_heading = form1.prof_heading.data
                p.prof_sub1 = form1.prof_sub1.data
                p.prof_sub2 = form1.prof_sub2.data
                p.prof_sub3 = form1.prof_sub3.data
                p.prof_sub4 = form1.prof_sub4.data
                p.prof_sub5 = form1.prof_sub5.data
            for q in dis:
                if ((dis.index(q)) == 0):
                    q.disbursement_amount =form1.disbursement_amount.data
                    q.disb_heading=form1.disb_heading.data 
                    q.disb_sub1=form1.disb_sub1.data 
                    q.disb_sub2=form1.disb_sub2.data 
                    q.disb_sub3=form1.disb_sub3.data 

                if ((dis.index(q)) == 1):
                    q.disbursement_amount =form1.disbursement_amount2.data
                    q.disb_heading=form1.disb_heading2.data 
                    q.disb_sub1=form1.disb_sub12.data 
                    q.disb_sub2=form1.disb_sub22.data 
                    q.disb_sub3=form1.disb_sub32.data
                if ((dis.index(q)) == 2):
                    q.disbursement_amount =form1.disbursement_amount3.data
                    q.disb_heading=form1.disb_heading3.data 
                    q.disb_sub1=form1.disb_sub13.data 
                    q.disb_sub2=form1.disb_sub23.data 
                    q.disb_sub3=form1.disb_sub33.data 
                if ((dis.index(q)) == 3):
                    q.disbursement_amount =form1.disbursement_amount4.data
                    q.disb_heading=form1.disb_heading4.data 
                    q.disb_sub1=form1.disb_sub14.data 
                    q.disb_sub2=form1.disb_sub24.data 
                    q.disb_sub3=form1.disb_sub34.data
                if ((dis.index(q)) == 4):
                    q.disbursement_amount =form1.disbursement_amount5.data
                    q.disb_heading=form1.disb_heading5.data 
                    q.disb_sub1=form1.disb_sub15.data 
                    q.disb_sub2=form1.disb_sub25.data 
                    q.disb_sub3=form1.disb_sub35.data 
                if ((dis.index(q)) == 5):
                    q.disbursement_amount =form1.disbursement_amount6.data
                    q.disb_heading=form1.disb_heading6.data 
                    q.disb_sub1=form1.disb_sub16.data 
                    q.disb_sub2=form1.disb_sub26.data 
                    q.disb_sub3=form1.disb_sub36.data
            db.session.commit()
            flash('Your log has been updated!', 'success')
            return redirect(url_for('saved_invoice',inv_id=inv_id,today=today))
        elif request.method == 'GET':
        
            form1.name_to.data = updt_inv.name_to
            form1.address_to.data  = updt_inv.address_to
            form1.email_to.data  = updt_inv.email_to
            form1.telephone_to.data= updt_inv.telephone_to
            form1.company_name.data = updt_inv.company_name
            form1.box_number_to.data = updt_inv.box_number_to
            #form1.ref_number.data = updt_inv.ref_number
            form1.terms.data = updt_inv.terms
            form1.issue_date.data = updt_inv.issue_date
            form1.due_date.data = updt_inv.due_date
            form1.vat.data = updt_inv.vat
            form1.bank.data = updt_inv.bank
            form1.bank_branch.data = updt_inv.bank_branch
            form1.swift_code.data = updt_inv.swift_code
            form1.account_number.data = updt_inv.account_number
            form1.professional_amount.data = updt_inv.professional_amount
            #print(len(item))
            for p in item:
                #print(p.id,p.invoice_id)
                form1.prof_heading.data = p.prof_heading
                form1.prof_sub1.data = p.prof_sub1
                form1.prof_sub2.data = p.prof_sub2
                form1.prof_sub3.data = p.prof_sub3
                form1.prof_sub4.data = p.prof_sub4
                form1.prof_sub5.data = p.prof_sub5
            for q in dis:
                if ((dis.index(q)) == 0):
                    form1.disbursement_amount.data = q.disbursement_amount
                    form1.disb_heading.data = q.disb_heading
                    form1.disb_sub1.data = q.disb_sub1
                    form1.disb_sub2.data = q.disb_sub2
                    form1.disb_sub3.data = q.disb_sub3
                if ((dis.index(q)) == 1):
                    form1.disbursement_amount2.data = q.disbursement_amount
                    form1.disb_heading2.data = q.disb_heading
                    form1.disb_sub12.data = q.disb_sub1
                    form1.disb_sub22.data = q.disb_sub2
                    form1.disb_sub32.data = q.disb_sub3
                if ((dis.index(q)) == 2):
                    form1.disbursement_amount3.data = q.disbursement_amount
                    form1.disb_heading3.data = q.disb_heading
                    form1.disb_sub13.data = q.disb_sub1
                    form1.disb_sub23data = q.disb_sub2
                    form1.disb_sub33.data = q.disb_sub3
                if ((dis.index(q)) == 3):
                    form1.disbursement_amount4.data = q.disbursement_amount
                    form1.disb_heading4.data = q.disb_heading
                    form1.disb_sub14.data = q.disb_sub1
                    form1.disb_sub24.data = q.disb_sub2
                    form1.disb_sub34.data = q.disb_sub3
                if ((dis.index(q)) == 4):
                    form1.disbursement_amount5.data = q.disbursement_amount
                    form1.disb_heading5.data = q.disb_heading
                    form1.disb_sub15.data = q.disb_sub1
                    form1.disb_sub25.data = q.disb_sub2
                    form1.disb_sub35.data = q.disb_sub3
                if ((dis.index(q)) == 5):
                    form1.disbursement_amount6.data = q.disbursement_amount
                    form1.disb_heading6.data = q.disb_heading
                    form1.disb_sub16.data = q.disb_sub1
                    form1.disb_sub26.data = q.disb_sub2
                    form1.disb_sub36.data = q.disb_sub3
    return render_template('invoice_update.html',updt_inv=updt_inv,item=item,dis=dis,inv_id=inv_id,
                            form1=form1,len=len,title='Update Invoice')
#this ends the  updating system so far 

@app.route("/Invoice2-<int:inv_id>-Update", methods=['GET', 'POST'])
@login_required
def update_invoice2(inv_id):
    today = date.today()
    updt_inv = Invoice.query.get_or_404(inv_id)
    item = InvoiceLineItem.query.filter_by(invoice=updt_inv).all()
    dis = disbursements.query.filter_by(invoice=updt_inv).all()
    form2=Invoice_Items2()
    
    try:
        get_id = Invoice.query.order_by(desc('id')).first()
        x: int = get_id.id + 1
        y = date.today().strftime("%y%m")
        if get_id:
            ref_number = "" + y + str(x).zfill(3) + ""
    except:
        ref_number = str(date.today().strftime("%y%m") + str(1).zfill(3))
    finally:
        if request.method == 'POST':
            ref_number = ref_number
            updt_inv.name_to = form2.name_to.data 
            updt_inv.address_to = form2.address_to.data 
            updt_inv.email_to = form2.email_to.data 
            updt_inv.company_name = form2.company_name.data
            updt_inv.telephone_to = form2.telephone_to.data 
            updt_inv.box_number_to = form2.box_number_to.data 
            updt_inv.vat = form2.vat.data 
            updt_inv.terms = form2.terms.data 
            updt_inv.issue_date = form2.issue_date.data
            updt_inv.due_date = form2.due_date.data
            updt_inv.bank = form2.bank.data   
            updt_inv.bank_branch = form2.bank_branch.data   
            updt_inv.swift_code = form2.swift_code.data   
            updt_inv.account_number = form2.account_number.data   
            updt_inv.professional_amount = form2.professional_amount.data   
            for p in item:
                if ((item.index(p)) == 0):
                    p.prof_heading = form2.prof_heading.data
                    p.prof_sub1 = form2.prof_sub1.data
                    p.prof_sub2 = form2.prof_sub2.data
                    p.prof_sub3 = form2.prof_sub3.data
                    p.prof_sub4 = form2.prof_sub4.data
                    p.prof_sub5 = form2.prof_sub5.data
                if ((item.index(p)) == 1):
                    p.prof_heading = form2.prof_heading2.data
                    p.prof_sub1 = form2.prof_sub12.data
                    p.prof_sub2 = form2.prof_sub22.data
                    p.prof_sub3 = form2.prof_sub32.data
                    p.prof_sub4 = form2.prof_sub42.data
                    p.prof_sub5 = form2.prof_sub52.data
            for q in dis:
                q.disbursement_amount =form2.disbursement_amount.data
                q.disb_heading=form2.disb_heading.data 
                q.disb_sub1=form2.disb_sub1.data 
                q.disb_sub2=form2.disb_sub2.data 
                q.disb_sub3=form2.disb_sub3.data 
        
            db.session.commit()
            flash('Your log has been updated!', 'success')
            return redirect(url_for('saved_invoice',inv_id=inv_id,today=today))
        elif request.method == 'GET':
        
            form2.name_to.data = updt_inv.name_to
            form2.address_to.data  = updt_inv.address_to
            form2.email_to.data  = updt_inv.email_to
            form2.company_name.data = updt_inv.company_name
            form2.telephone_to.data= updt_inv.telephone_to
            form2.terms.data = updt_inv.terms
            form2.issue_date.data = updt_inv.issue_date
            form2.due_date.data = updt_inv.due_date
            form2.box_number_to.data = updt_inv.box_number_to
            form2.vat.data = updt_inv.vat
            form2.bank.data = updt_inv.bank
            form2.bank_branch.data = updt_inv.bank_branch
            form2.swift_code.data = updt_inv.swift_code
            form2.account_number.data = updt_inv.account_number  
            form2.professional_amount.data = updt_inv.professional_amount
            for p in item:
                #print(p.id,p.invoice_id)
                if ((item.index(p)) == 0):
                    form2.prof_heading.data = p.prof_heading
                    form2.prof_sub1.data = p.prof_sub1
                    form2.prof_sub2.data = p.prof_sub2
                    form2.prof_sub3.data = p.prof_sub3
                    form2.prof_sub4.data = p.prof_sub4
                    form2.prof_sub5.data = p.prof_sub5
                if ((item.index(p)) == 1):
                    form2.prof_heading2.data = p.prof_heading
                    form2.prof_sub12.data = p.prof_sub1
                    form2.prof_sub22.data = p.prof_sub2
                    form2.prof_sub32.data = p.prof_sub3
                    form2.prof_sub42.data = p.prof_sub4
                    form2.prof_sub52.data = p.prof_sub5
            for q in dis:
                form2.disbursement_amount.data = q.disbursement_amount
                form2.disb_heading.data = q.disb_heading
                form2.disb_sub1.data = q.disb_sub1
                form2.disb_sub2.data = q.disb_sub2
                form2.disb_sub3.data = q.disb_sub3

    return render_template('invoice_update.html',updt_inv=updt_inv,item=item,dis=dis,inv_id=inv_id,
                            form2=form2,len=len,title='Update Invoice')
                        
@app.route("/Invoice3-<int:inv_id>-Update", methods=['GET', 'POST'])
@login_required
def update_invoice3(inv_id):
    today = date.today()
    updt_inv = Invoice.query.get_or_404(inv_id)
    item = InvoiceLineItem.query.filter_by(invoice=updt_inv).all()
    dis = disbursements.query.filter_by(invoice=updt_inv).all()
    form3=Invoice_Items3()
    try:
        get_id = Invoice.query.order_by(desc('id')).first()
        x: int = get_id.id + 1
        y = date.today().strftime("%y%m")
        if get_id:
            ref_number = "" + y + str(x).zfill(3) + ""
    except:
        ref_number = str(date.today().strftime("%y%m") + str(1).zfill(3))
    finally:
        if request.method == 'POST':
            ref_number = ref_number
            updt_inv.name_to = form3.name_to.data 
            updt_inv.address_to = form3.address_to.data 
            updt_inv.email_to = form3.email_to.data
            updt_inv.company_name = form3.company_name.data 
            updt_inv.telephone_to = form3.telephone_to.data 
            updt_inv.box_number_to = form3.box_number_to.data 
            updt_inv.vat = form3.vat.data 
            updt_inv.terms = form3.terms.data 
            updt_inv.issue_date = form3.issue_date.data
            updt_inv.due_date = form3.due_date.data 
            updt_inv.bank = form3.bank.data   
            updt_inv.bank_branch = form3.bank_branch.data   
            updt_inv.swift_code = form3.swift_code.data   
            updt_inv.account_number = form3.account_number.data   
            updt_inv.professional_amount = form2.professional_amount.data 
            updt_inv.professional_amount = form3.professional_amount.data   

            for p in item:
                if ((item.index(p)) == 0):
                    p.prof_heading = form3.prof_heading.data
                    p.prof_sub1 = form3.prof_sub1.data
                    p.prof_sub2 = form3.prof_sub2.data
                    p.prof_sub3 = form3.prof_sub3.data
                    p.prof_sub4 = form3.prof_sub4.data
                    p.prof_sub5 = form3.prof_sub5.data
                if ((item.index(p)) == 1):
                    p.prof_heading = form3.prof_heading2.data
                    p.prof_sub1 = form3.prof_sub12.data
                    p.prof_sub2 = form3.prof_sub22.data
                    p.prof_sub3 = form3.prof_sub32.data
                    p.prof_sub4 = form3.prof_sub42.data
                    p.prof_sub5 = form3.prof_sub52.data
                if ((item.index(p)) == 2):
                    p.prof_heading = form3.prof_heading2.data
                    p.prof_sub1 = form3.prof_sub13.data
                    p.prof_sub2 = form3.prof_sub23.data
                    p.prof_sub3 = form3.prof_sub33.data
                    p.prof_sub4 = form3.prof_sub43.data
                    p.prof_sub5 = form3.prof_sub53.data
            for q in dis:
                q.disbursement_amount =form3.disbursement_amount.data
                q.disb_heading=form3.disb_heading.data 
                q.disb_sub1=form3.disb_sub1.data 
                q.disb_sub2=form3.disb_sub2.data 
                q.disb_sub3=form3.disb_sub3.data 
            db.session.commit()
            flash('Your log has been updated!', 'success')
            return redirect(url_for('saved_invoice',inv_id=inv_id,today=today))
        elif request.method == 'GET':
        
            form3.name_to.data = updt_inv.name_to
            form3.address_to.data  = updt_inv.address_to
            form3.email_to.data  = updt_inv.email_to
            form3.company_name.data = updt_inv.company_name
            form3.telephone_to.data= updt_inv.telephone_to
            #form3.ref_number.data = updt_inv.ref_number
            form3.terms.data = updt_inv.terms
            form3.issue_date.data = updt_inv.issue_date
            form3.due_date.data = updt_inv.due_date
            form3.box_number_to.data = updt_inv.box_number_to
            form3.vat.data = updt_inv.vat 
            form3.bank.data = updt_inv.bank
            form3.bank_branch.data = updt_inv.bank_branch
            form3.swift_code.data = updt_inv.swift_code
            form3.account_number.data = updt_inv.account_number
            form3.professional_amount.data = updt_inv.professional_amount  
            for p in item:
                if ((item.index(p)) == 0):
                    form3.prof_heading.data = p.prof_heading
                    form3.prof_sub1.data = p.prof_sub1
                    form3.prof_sub2.data = p.prof_sub2
                    form3.prof_sub3.data = p.prof_sub3
                    form3.prof_sub4.data = p.prof_sub4
                    form3.prof_sub5.data = p.prof_sub5
                if ((item.index(p)) == 1):
                    form3.prof_heading2.data = p.prof_heading
                    form3.prof_sub12.data = p.prof_sub1
                    form3.prof_sub22.data = p.prof_sub2
                    form3.prof_sub32.data = p.prof_sub3
                    form3.prof_sub42.data = p.prof_sub4
                    form3.prof_sub52.data = p.prof_sub5
                if ((item.index(p)) == 2):
                    form3.prof_heading3.data = p.prof_heading
                    form3.prof_sub13.data = p.prof_sub1
                    form3.prof_sub23.data = p.prof_sub2
                    form3.prof_sub33.data = p.prof_sub3
                    form3.prof_sub43.data = p.prof_sub4
                    form3.prof_sub53.data = p.prof_sub5
            for q in dis:
               form3.disbursement_amount.data = q.disbursement_amount
               form3.disb_heading.data = q.disb_heading
               form3.disb_sub1.data = q.disb_sub1
               form3.disb_sub2.data = q.disb_sub2
               form3.disb_sub3.data = q.disb_sub3
    return render_template('invoice_update.html',updt_inv=updt_inv,item=item,dis=dis,inv_id=inv_id,
                            form3=form3,len=len,title='Update Invoice')
@app.route("/Invoice4-<int:inv_id>-Update", methods=['GET', 'POST'])
@login_required
def update_invoice4(inv_id):
    today = date.today()
    updt_inv = Invoice.query.get_or_404(inv_id)
    item = InvoiceLineItem.query.filter_by(invoice=updt_inv).all()
    dis = disbursements.query.filter_by(invoice=updt_inv).all()
    form4=Invoice_Items4()
    try:
        get_id = Invoice.query.order_by(desc('id')).first()
        x: int = get_id.id + 1
        y = date.today().strftime("%y%m")
        if get_id:
            ref_number = "" + y + str(x).zfill(3) + ""
    except:
        ref_number = str(date.today().strftime("%y%m") + str(1).zfill(3))
    finally:
        if request.method == 'POST':
            ref_number =ref_number
            updt_inv.name_to = form4.name_to.data 
            updt_inv.address_to = form4.address_to.data 
            updt_inv.email_to = form4.email_to.data
            updt_inv.company_name = form4.company_name.data 
            updt_inv.telephone_to = form4.telephone_to.data 
            updt_inv.box_number_to = form4.box_number_to.data 
            updt_inv.vat = form4.vat.data 
            updt_inv.terms = form4.terms.data 
            updt_inv.issue_date = form4.issue_date.data
            updt_inv.due_date = form4.due_date.data 
            updt_inv.bank = form4.bank.data   
            updt_inv.bank_branch = form4.bank_branch.data   
            updt_inv.swift_code = form4.swift_code.data   
            updt_inv.account_number = form4.account_number.data   
            updt_inv.professional_amount = form4.professional_amount.data   
            for p in item:
                if ((item.index(p)) == 0):
                    p.prof_heading = form4.prof_heading.data
                    p.prof_sub1 = form4.prof_sub1.data
                    p.prof_sub2 = form4.prof_sub2.data
                    p.prof_sub3 = form4.prof_sub3.data
                    p.prof_sub4 = form4.prof_sub4.data
                    p.prof_sub5 = form4.prof_sub5.data
                if ((item.index(p)) == 1):
                    p.prof_heading = form4.prof_heading2.data
                    p.prof_sub1 = form4.prof_sub12.data
                    p.prof_sub2 = form4.prof_sub22.data
                    p.prof_sub3 = form4.prof_sub32.data
                    p.prof_sub4 = form4.prof_sub42.data
                    p.prof_sub5 = form4.prof_sub52.data
                if ((item.index(p)) == 2):
                    p.prof_heading = form4.prof_heading3.data
                    p.prof_sub1 = form4.prof_sub13.data
                    p.prof_sub2 = form4.prof_sub23.data
                    p.prof_sub3 = form4.prof_sub33.data
                    p.prof_sub4 = form4.prof_sub43.data
                    p.prof_sub5 = form4.prof_sub53.data
                if ((item.index(p)) == 3):
                    p.prof_heading = form4.prof_heading4.data
                    p.prof_sub1 = form4.prof_sub14.data
                    p.prof_sub2 = form4.prof_sub24.data
                    p.prof_sub3 = form4.prof_sub34.data
                    p.prof_sub4 = form4.prof_sub44.data
                    p.prof_sub5 = form4.prof_sub54.data
            for q in dis:
                q.disbursement_amount =form4.disbursement_amount.data
                q.disb_heading=form4.disb_heading.data 
                q.disb_sub1=form4.disb_sub1.data 
                q.disb_sub2=form4.disb_sub2.data 
                q.disb_sub3=form4.disb_sub3.data 
            db.session.commit()
            flash('Your log has been updated!', 'success')
            return redirect(url_for('saved_invoice',inv_id=inv_id,today=today))
        elif request.method == 'GET':
        
            form4.name_to.data = updt_inv.name_to
            form4.address_to.data  = updt_inv.address_to
            form4.email_to.data  = updt_inv.email_to
            form4.company_name.data = updt_inv.company_name
            form4.telephone_to.data= updt_inv.telephone_to
            form4.terms.data = updt_inv.terms
            form4.issue_date.data = updt_inv.issue_date
            form4.due_date.data = updt_inv.due_date
            form4.box_number_to.data = updt_inv.box_number_to
            form4.vat.data = updt_inv.vat 
            form4.bank.data = updt_inv.bank
            form4.bank_branch.data = updt_inv.bank_branch
            form4.swift_code.data = updt_inv.swift_code
            form4.account_number.data = updt_inv.account_number
            form4.professional_amount.data = updt_inv.professional_amount
            for p in item:
                #print(p.id,p.invoice_id)
                if ((item.index(p)) == 0):
                    form4.prof_heading.data = p.prof_heading
                    form4.prof_sub1.data = p.prof_sub1
                    form4.prof_sub2.data = p.prof_sub2
                    form4.prof_sub3.data = p.prof_sub3
                    form4.prof_sub4.data = p.prof_sub4
                    form4.prof_sub5.data = p.prof_sub5
                if ((item.index(p)) == 1):
                    form4.prof_heading2.data = p.prof_heading
                    form4.prof_sub12.data = p.prof_sub1
                    form4.prof_sub22.data = p.prof_sub2
                    form4.prof_sub32.data = p.prof_sub3
                    form4.prof_sub42.data = p.prof_sub4
                    form4.prof_sub52.data = p.prof_sub5
                if ((item.index(p)) == 2):
                    form4.prof_heading3.data = p.prof_heading
                    form4.prof_sub13.data = p.prof_sub1
                    form4.prof_sub23.data = p.prof_sub2
                    form4.prof_sub33.data = p.prof_sub3
                    form4.prof_sub43.data = p.prof_sub4
                    form4.prof_sub53.data = p.prof_sub5
                if ((item.index(p)) == 3):
                    form4.prof_heading4.data = p.prof_heading
                    form4.prof_sub14.data = p.prof_sub1
                    form4.prof_sub24.data = p.prof_sub2
                    form4.prof_sub34.data = p.prof_sub3
                    form4.prof_sub44.data = p.prof_sub4
                    form4.prof_sub54.data = p.prof_sub5
            for q in dis:
               form4.disbursement_amount.data = q.disbursement_amount
               form4.disb_heading.data = q.disb_heading
               form4.disb_sub1.data = q.disb_sub1
               form4.disb_sub2.data = q.disb_sub2
               form4.disb_sub3.data = q.disb_sub3

    return render_template('invoice_update.html',updt_inv=updt_inv,item=item,dis=dis,inv_id=inv_id,
                            form4=form4,len=len,title='Update Invoice')

@app.route("/Invoice5-<int:inv_id>-Update", methods=['GET', 'POST'])
@login_required
def update_invoice5(inv_id):
    today = date.today()
    updt_inv = Invoice.query.get_or_404(inv_id)
    item = InvoiceLineItem.query.filter_by(invoice=updt_inv).all()
    dis = disbursements.query.filter_by(invoice=updt_inv).all()
    form5=Invoice_Items5()
    try:
        get_id = Invoice.query.order_by(desc('id')).first()
        x: int = get_id.id + 1
        y = date.today().strftime("%y%m")
        if get_id:
            ref_number = "" + y + str(x).zfill(3) + ""
    except:
        ref_number = str(date.today().strftime("%y%m") + str(1).zfill(3))
    finally:
        if request.method == 'POST':
            updt_inv.name_to = form5.name_to.data 
            updt_inv.address_to = form5.address_to.data 
            updt_inv.email_to = form5.email_to.data 
            updt_inv.company_name = form5.company_name.data
            updt_inv.telephone_to = form5.telephone_to.data 
            updt_inv.box_number_to = form5.box_number_to.data 
            updt_inv.vat = form5.vat.data  
            updt_inv.terms = form5.terms.data 
            updt_inv.issue_date = form5.issue_date.data
            updt_inv.due_date = form5.due_date.data 
            updt_inv.bank = form5.bank.data   
            updt_inv.bank_branch = form5.bank_branch.data   
            updt_inv.swift_code = form5.swift_code.data   
            updt_inv.account_number = form5.account_number.data   
            updt_inv.professional_amount = form5.professional_amount.data   
            for p in item:
                #print(p.id,p.invoice_id)
                if ((item.index(p)) == 0):
                    form5.prof_heading.data = p.prof_heading
                    form5.prof_sub1.data = p.prof_sub1
                    form5.prof_sub2.data = p.prof_sub2
                    form5.prof_sub3.data = p.prof_sub3
                    form5.prof_sub4.data = p.prof_sub4
                    form5.prof_sub5.data = p.prof_sub5
                if ((item.index(p)) == 1):
                    form5.prof_heading2.data = p.prof_heading
                    form5.prof_sub12.data = p.prof_sub1
                    form5.prof_sub22.data = p.prof_sub2
                    form5.prof_sub32.data = p.prof_sub3
                    form5.prof_sub42.data = p.prof_sub4
                    form5.prof_sub52.data = p.prof_sub5
                if ((item.index(p)) == 2):
                    form5.prof_heading3.data = p.prof_heading
                    form5.prof_sub13.data = p.prof_sub1
                    form5.prof_sub23.data = p.prof_sub2
                    form5.prof_sub33.data = p.prof_sub3
                    form5.prof_sub43.data = p.prof_sub4
                    form5.prof_sub53.data = p.prof_sub5
                if ((item.index(p)) == 3):
                    form5.prof_heading4.data = p.prof_heading
                    form5.prof_sub14.data = p.prof_sub1
                    form5.prof_sub24.data = p.prof_sub2
                    form5.prof_sub34.data = p.prof_sub3
                    form5.prof_sub44.data = p.prof_sub4
                    form5.prof_sub54.data = p.prof_sub5
                if ((item.index(p)) == 4):
                    form5.prof_heading5.data = p.prof_heading
                    form5.prof_sub15.data = p.prof_sub1
                    form5.prof_sub25.data = p.prof_sub2
                    form5.prof_sub35.data = p.prof_sub3
                    form5.prof_sub45.data = p.prof_sub4
                    form5.prof_sub55.data = p.prof_sub5

            for q in dis:
                    q.disbursement_amount =form5.disbursement_amount.data
                    q.disb_heading=form5.disb_heading.data 
                    q.disb_sub1=form5.disb_sub1.data 
                    q.disb_sub2=form5.disb_sub2.data 
                    q.disb_sub3=form5.disb_sub3.data 
            db.session.commit()
            flash('Your log has been updated!', 'success')
            return redirect(url_for('saved_invoice',inv_id=inv_id,today=today))
        elif request.method == 'GET':
        
            form5.name_to.data = updt_inv.name_to
            form5.address_to.data  = updt_inv.address_to
            form5.email_to.data  = updt_inv.email_to
            form5.company_name.data =  updt_inv.company_name
            form5.telephone_to.data= updt_inv.telephone_to
            form5.terms.data = updt_inv.terms
            form5.issue_date.data = updt_inv.issue_date
            form5.due_date.data = updt_inv.due_date
            form5.box_number_to.data = updt_inv.box_number_to
            form5.vat.data = updt_inv.vat 
            form5.bank.data = updt_inv.bank
            form5.bank_branch.data = updt_inv.bank_branch
            form5.swift_code.data = updt_inv.swift_code
            form5.account_number.data = updt_inv.account_number
            form5.professional_amount.data=updt_inv.professional_amount
            for p in item:
                if ((item.index(p)) == 0):
                    form5.prof_heading.data = p.prof_heading
                    form5.prof_sub1.data = p.prof_sub1
                    form5.prof_sub2.data = p.prof_sub2
                    form5.prof_sub3.data = p.prof_sub3
                    form5.prof_sub4.data = p.prof_sub4
                    form5.prof_sub5.data = p.prof_sub5
                if ((item.index(p)) == 1):
                    form5.prof_heading2.data = p.prof_heading
                    form5.prof_sub12.data = p.prof_sub1
                    form5.prof_sub22.data = p.prof_sub2
                    form5.prof_sub32.data = p.prof_sub3
                    form5.prof_sub42.data = p.prof_sub4
                    form5.prof_sub52.data = p.prof_sub5
                if ((item.index(p)) == 2):
                    form5.prof_heading3.data = p.prof_heading
                    form5.prof_sub13.data = p.prof_sub1
                    form5.prof_sub23.data = p.prof_sub2
                    form5.prof_sub33.data = p.prof_sub3
                    form5.prof_sub43.data = p.prof_sub4
                    form5.prof_sub53.data = p.prof_sub5
                if ((item.index(p)) == 3):
                    form5.prof_heading4.data = p.prof_heading
                    form5.prof_sub14.data = p.prof_sub1
                    form5.prof_sub24.data = p.prof_sub2
                    form5.prof_sub34.data = p.prof_sub3
                    form5.prof_sub44.data = p.prof_sub4
                    form5.prof_sub54.data = p.prof_sub5

                if ((item.index(p)) == 4):
                    form5.prof_heading5.data = p.prof_heading
                    form5.prof_sub15.data = p.prof_sub1
                    form5.prof_sub25.data = p.prof_sub2
                    form5.prof_sub35.data = p.prof_sub3
                    form5.prof_sub45.data = p.prof_sub4
                    form5.prof_sub55.data = p.prof_sub5

            for q in dis:
               form5.disbursement_amount.data = q.disbursement_amount
               form5.disb_heading.data = q.disb_heading
               form5.disb_sub1.data = q.disb_sub1
               form5.disb_sub2.data = q.disb_sub2
               form5.disb_sub3.data = q.disb_sub3
    return render_template('invoice_update.html',updt_inv=updt_inv,item=item,dis=dis,inv_id=inv_id,
                            form5=form5,len=len,title='Update Invoice')

@app.route("/Invoice6-<int:inv_id>-Update", methods=['GET', 'POST'])
@login_required
def update_invoice6(inv_id):
    today = date.today()
    updt_inv = Invoice.query.get_or_404(inv_id)
    item = InvoiceLineItem.query.filter_by(invoice=updt_inv).all()
    form6=Invoice_Items5()
    try:
        get_id = Invoice.query.order_by(desc('id')).first()
        x: int = get_id.id + 1
        y = date.today().strftime("%y%m")
        if get_id:
            ref_number = "" + y + str(x).zfill(3) + ""
    except:
        ref_number = str(date.today().strftime("%y%m") + str(1).zfill(3))
    finally:
        if request.method == 'POST':
            updt_inv.name_to = form6.name_to.data 
            updt_inv.address_to = form6.address_to.data 
            updt_inv.email_to = form6.email_to.data 
            updt_inv.company_name = form6.company_name.data
            updt_inv.telephone_to = form6.telephone_to.data 
            updt_inv.box_number_to = form6.box_number_to.data 
            updt_inv.vat = form6.vat.data  
            updt_inv.terms = form6.terms.data 
            updt_inv.issue_date = form6.issue_date.data
            updt_inv.due_date = form6.due_date.data   
            for p in item:
                if ((item.index(p)) == 0):
                    p.professional_desc = form6.professional_desc.data
                    p.professional_amount = form6.professional_amount.data
                    p.disbursements_desc = form6.disbursements_desc.data
                    p.disbursements_amount = form6.disbursements_amount.data
                if ((item.index(p)) == 1):
                    p.professional_desc = form6.professional_desc2.data
                    p.professional_amount = form6.professional_amount2.data
                    p.disbursements_desc = form6.disbursements_desc2.data
                    p.disbursements_amount = form6.disbursements_amount2.data
                if ((item.index(p)) == 2):
                    p.professional_desc = form6.professional_desc3.data
                    p.professional_amount = form6.professional_amount3.data
                    p.disbursements_desc = form6.disbursements_desc3.data
                    p.disbursements_amount = form6.disbursements_amount3.data
                if ((item.index(p)) == 3):
                    p.professional_desc = form6.professional_desc4.data
                    p.professional_amount = form6.professional_amount4.data
                    p.disbursements_desc = form6.disbursements_desc4.data
                    p.disbursements_amount = form6.disbursements_amount4.data
                if ((item.index(p)) == 4):
                    p.professional_desc = form6.professional_desc5.data
                    p.professional_amount = form6.professional_amount5.data
                    p.disbursements_desc = form6.disbursements_desc5.data
                    p.disbursements_amount = form6.disbursements_amount5.data
                if ((item.index(p)) == 5):
                    p.professional_desc = form6.professional_desc6.data
                    p.professional_amount = form6.professional_amount6.data
                    p.disbursements_desc = form6.disbursements_desc6.data
                    p.disbursements_amount = form6.disbursements_amount6.data
            db.session.commit()
            flash('Your log has been updated!', 'success')
            return redirect(url_for('saved_invoice',inv_id=inv_id,today=today))
        elif request.method == 'GET':
        
            form6.name_to.data = updt_inv.name_to
            form6.address_to.data  = updt_inv.address_to
            form6.email_to.data  = updt_inv.email_to
            form6.company_name.data =  updt_inv.company_name
            form6.telephone_to.data= updt_inv.telephone_to
            form6.terms.data = updt_inv.terms
            form6.issue_date.data = updt_inv.issue_date
            form6.due_date.data = updt_inv.due_date
            form6.box_number_to.data = updt_inv.box_number_to
            form6.vat.data = updt_inv.vat 
            for p in item:
                #print(p.id,p.invoice_id)
                if ((item.index(p)) == 0):
                    form6.professional_desc.data = p.professional_desc
                    form6.professional_amount.data = p.professional_amount
                    form6.disbursements_desc.data = p.disbursements_desc
                    form6.disbursements_amount.data = p.disbursements_amount
                if ((item.index(p)) == 1):
                    form6.professional_desc2.data = p.professional_desc
                    form6.professional_amount2.data = p.professional_amount
                    form6.disbursements_desc2.data = p.disbursements_desc
                    form6.disbursements_amount2.data = p.disbursements_amount
                if ((item.index(p)) == 2):
                    form6.professional_desc3.data = p.professional_desc
                    form6.professional_amount3.data = p.professional_amount
                    form6.disbursements_desc3.data = p.disbursements_desc
                    form6.disbursements_amount3.data = p.disbursements_amount
                if ((item.index(p)) == 3):
                    form6.professional_desc4.data = p.professional_desc
                    form6.professional_amount4.data = p.professional_amount
                    form6.disbursements_desc4.data = p.disbursements_desc
                    form6.disbursements_amount4.data = p.disbursements_amount

                if ((item.index(p)) == 4):
                    form6.professional_desc5.data = p.professional_desc
                    form6.professional_amount5.data = p.professional_amount
                    form6.disbursements_desc5.data = p.disbursements_desc
                    form6.disbursements_amount5.data = p.disbursements_amount
                if ((item.index(p)) == 5):
                    form6.professional_desc6.data = p.professional_desc
                    form6.professional_amount6.data = p.professional_amount
                    form6.disbursements_desc6.data = p.disbursements_desc
                    form6.disbursements_amount6.data = p.disbursements_amount

    return render_template('invoice_update.html',updt_inv=updt_inv,item=item,inv_id=inv_id,
                            form6=form6,len=len,title='Update Invoice')
@app.route("/Invoice7-<int:inv_id>-Update", methods=['GET', 'POST'])
@login_required
def update_invoice7(inv_id):
    today = date.today()
    updt_inv = Invoice.query.get_or_404(inv_id)
    item = InvoiceLineItem.query.filter_by(invoice=updt_inv).all()
    form7=Invoice_Items6()
    try:
        get_id = Invoice.query.order_by(desc('id')).first()
        x: int = get_id.id + 1
        y = date.today().strftime("%y%m")
        if get_id:
            ref_number = "" + y + str(x).zfill(3) + ""
    except:
        ref_number = str(date.today().strftime("%y%m") + str(1).zfill(3))
    finally:
        if request.method == 'POST':
            updt_inv.name_to = form7.name_to.data 
            updt_inv.address_to = form7.address_to.data 
            updt_inv.email_to = form7.email_to.data 
            updt_inv.company_name = form7.company_name.data
            updt_inv.telephone_to = form7.telephone_to.data 
            updt_inv.box_number_to = form7.box_number_to.data 
            updt_inv.vat = form7.vat.data  
            updt_inv.terms = form7.terms.data 
            updt_inv.issue_date = form7.issue_date.data
            updt_inv.due_date = form7.due_date.data   
            for p in item:
                if ((item.index(p)) == 0):
                    p.professional_desc = form7.professional_desc.data
                    p.professional_amount = form7.professional_amount.data
                    p.disbursements_desc = form7.disbursements_desc.data
                    p.disbursements_amount = form7.disbursements_amount.data
                if ((item.index(p)) == 1):
                    p.professional_desc = form7.professional_desc2.data
                    p.professional_amount = form7.professional_amount2.data
                    p.disbursements_desc = form7.disbursements_desc2.data
                    p.disbursements_amount = form7.disbursements_amount2.data
                if ((item.index(p)) == 2):
                    p.professional_desc = form7.professional_desc3.data
                    p.professional_amount = form7.professional_amount3.data
                    p.disbursements_desc = form7.disbursements_desc3.data
                    p.disbursements_amount = form7.disbursements_amount3.data
                if ((item.index(p)) == 3):
                    p.professional_desc = form7.professional_desc4.data
                    p.professional_amount = form7.professional_amount4.data
                    p.disbursements_desc = form7.disbursements_desc4.data
                    p.disbursements_amount = form7.disbursements_amount4.data
                if ((item.index(p)) == 4):
                    p.professional_desc = form7.professional_desc5.data
                    p.professional_amount = form7.professional_amount5.data
                    p.disbursements_desc = form7.disbursements_desc5.data
                    p.disbursements_amount = form7.disbursements_amount5.data
                if ((item.index(p)) == 5):
                    p.professional_desc = form7.professional_desc6.data
                    p.professional_amount = form7.professional_amount6.data
                    p.disbursements_desc = form7.disbursements_desc6.data
                    p.disbursements_amount = form7.disbursements_amount6.data
                if ((item.index(p)) == 6):
                    p.professional_desc = form7.professional_desc7.data
                    p.professional_amount = form7.professional_amount7.data
                    p.disbursements_desc = form7.disbursements_desc7.data
                    p.disbursements_amount = form7.disbursements_amount7.data
            db.session.commit()
            flash('Your log has been updated!', 'success')
            return redirect(url_for('saved_invoice',inv_id=inv_id,today=today))
        elif request.method == 'GET':
        
            form7.name_to.data = updt_inv.name_to
            form7.address_to.data  = updt_inv.address_to
            form7.email_to.data  = updt_inv.email_to
            form7.company_name.data =  updt_inv.company_name
            form7.telephone_to.data= updt_inv.telephone_to
            form7.terms.data = updt_inv.terms
            form7.issue_date.data = updt_inv.issue_date
            form7.due_date.data = updt_inv.due_date
            form7.box_number_to.data = updt_inv.box_number_to
            form7.vat.data = updt_inv.vat 
            for p in item:
                #print(p.id,p.invoice_id)
                if ((item.index(p)) == 0):
                    form7.professional_desc.data = p.professional_desc
                    form7.professional_amount.data = p.professional_amount
                    form7.disbursements_desc.data = p.disbursements_desc
                    form7.disbursements_amount.data = p.disbursements_amount
                if ((item.index(p)) == 1):
                    form7.professional_desc2.data = p.professional_desc
                    form7.professional_amount2.data = p.professional_amount
                    form7.disbursements_desc2.data = p.disbursements_desc
                    form7.disbursements_amount2.data = p.disbursements_amount
                if ((item.index(p)) == 2):
                    form7.professional_desc3.data = p.professional_desc
                    form7.professional_amount3.data = p.professional_amount
                    form7.disbursements_desc3.data = p.disbursements_desc
                    form7.disbursements_amount3.data = p.disbursements_amount
                if ((item.index(p)) == 3):
                    form7.professional_desc4.data = p.professional_desc
                    form7.professional_amount4.data = p.professional_amount
                    form7.disbursements_desc4.data = p.disbursements_desc
                    form7.disbursements_amount4.data = p.disbursements_amount

                if ((item.index(p)) == 4):
                    form7.professional_desc5.data = p.professional_desc
                    form7.professional_amount5.data = p.professional_amount
                    form7.disbursements_desc5.data = p.disbursements_desc
                    form7.disbursements_amount5.data = p.disbursements_amount
                if ((item.index(p)) == 5):
                    form7.professional_desc6.data = p.professional_desc
                    form7.professional_amount6.data = p.professional_amount
                    form7.disbursements_desc6.data = p.disbursements_desc
                    form7.disbursements_amount6.data = p.disbursements_amount
                if ((item.index(p)) == 6):
                    form7.professional_desc7.data = p.professional_desc
                    form7.professional_amount7.data = p.professional_amount
                    form7.disbursements_desc7.data = p.disbursements_desc
                    form7.disbursements_amount7.data = p.disbursements_amount
    return render_template('invoice_update.html',updt_inv=updt_inv,item=item,inv_id=inv_id,
                            form7=form7,len=len,title='Update Invoice')

@app.route("/Invoice8-<int:inv_id>-Update", methods=['GET', 'POST'])
@login_required
def update_invoice8(inv_id):
    today = date.today()
    updt_inv = Invoice.query.get_or_404(inv_id)
    item = InvoiceLineItem.query.filter_by(invoice=updt_inv).all()
    form8=Invoice_Items7()
    try:
        get_id = Invoice.query.order_by(desc('id')).first()
        x: int = get_id.id + 1
        y = date.today().strftime("%y%m")
        if get_id:
            ref_number = "" + y + str(x).zfill(3) + ""
    except:
        ref_number = str(date.today().strftime("%y%m") + str(1).zfill(3))
    finally:
        if request.method == 'POST':
            updt_inv.name_to = form8.name_to.data 
            updt_inv.address_to = form8.address_to.data 
            updt_inv.email_to = form8.email_to.data 
            updt_inv.company_name = form8.company_name.data
            updt_inv.telephone_to = form8.telephone_to.data 
            updt_inv.box_number_to = form8.box_number_to.data 
            updt_inv.vat = form8.vat.data  
            updt_inv.terms = form8.terms.data 
            updt_inv.issue_date = form8.issue_date.data
            updt_inv.due_date = form8.due_date.data   
            for p in item:
                if ((item.index(p)) == 0):
                    p.professional_desc = form8.professional_desc.data
                    p.professional_amount = form8.professional_amount.data
                    p.disbursements_desc = form8.disbursements_desc.data
                    p.disbursements_amount = form8.disbursements_amount.data
                if ((item.index(p)) == 1):
                    p.professional_desc = form8.professional_desc2.data
                    p.professional_amount = form8.professional_amount2.data
                    p.disbursements_desc = form8.disbursements_desc2.data
                    p.disbursements_amount = form8.disbursements_amount2.data
                if ((item.index(p)) == 2):
                    p.professional_desc = form8.professional_desc3.data
                    p.professional_amount = form8.professional_amount3.data
                    p.disbursements_desc = form8.disbursements_desc3.data
                    p.disbursements_amount = form8.disbursements_amount3.data
                if ((item.index(p)) == 3):
                    p.professional_desc = form8.professional_desc4.data
                    p.professional_amount = form8.professional_amount4.data
                    p.disbursements_desc = form8.disbursements_desc4.data
                    p.disbursements_amount = form8.disbursements_amount4.data
                if ((item.index(p)) == 4):
                    p.professional_desc = form8.professional_desc5.data
                    p.professional_amount = form8.professional_amount5.data
                    p.disbursements_desc = form8.disbursements_desc5.data
                    p.disbursements_amount = form8.disbursements_amount5.data
                if ((item.index(p)) == 5):
                    p.professional_desc = form8.professional_desc6.data
                    p.professional_amount = form8.professional_amount6.data
                    p.disbursements_desc = form8.disbursements_desc6.data
                    p.disbursements_amount = form8.disbursements_amount6.data
                if ((item.index(p)) == 6):
                    p.professional_desc = form8.professional_desc7.data
                    p.professional_amount = form8.professional_amount7.data
                    p.disbursements_desc = form8.disbursements_desc7.data
                    p.disbursements_amount = form8.disbursements_amount7.data
                if ((item.index(p)) == 7):
                    p.professional_desc = form8.professional_desc7.data
                    p.professional_amount = form8.professional_amount7.data
                    p.disbursements_desc = form8.disbursements_desc7.data
                    p.disbursements_amount = form8.disbursements_amount7.data
            db.session.commit()
            flash('Your log has been updated!', 'success')
            return redirect(url_for('saved_invoice',inv_id=inv_id,today=today))
        elif request.method == 'GET':
        
            form8.name_to.data = updt_inv.name_to
            form8.address_to.data  = updt_inv.address_to
            form8.email_to.data  = updt_inv.email_to
            form8.company_name.data =  updt_inv.company_name
            form8.telephone_to.data= updt_inv.telephone_to
            form8.terms.data = updt_inv.terms
            form8.issue_date.data = updt_inv.issue_date
            form8.due_date.data = updt_inv.due_date
            form8.box_number_to.data = updt_inv.box_number_to
            form8.vat.data = updt_inv.vat 
            for p in item:
                #print(p.id,p.invoice_id)
                if ((item.index(p)) == 0):
                    form8.professional_desc.data = p.professional_desc
                    form8.professional_amount.data = p.professional_amount
                    form8.disbursements_desc.data = p.disbursements_desc
                    form8.disbursements_amount.data = p.disbursements_amount
                if ((item.index(p)) == 1):
                    form8.professional_desc2.data = p.professional_desc
                    form8.professional_amount2.data = p.professional_amount
                    form8.disbursements_desc2.data = p.disbursements_desc
                    form8.disbursements_amount2.data = p.disbursements_amount
                if ((item.index(p)) == 2):
                    form8.professional_desc3.data = p.professional_desc
                    form8.professional_amount3.data = p.professional_amount
                    form8.disbursements_desc3.data = p.disbursements_desc
                    form8.disbursements_amount3.data = p.disbursements_amount
                if ((item.index(p)) == 3):
                    form8.professional_desc4.data = p.professional_desc
                    form8.professional_amount4.data = p.professional_amount
                    form8.disbursements_desc4.data = p.disbursements_desc
                    form8.disbursements_amount4.data = p.disbursements_amount

                if ((item.index(p)) == 4):
                    form8.professional_desc5.data = p.professional_desc
                    form8.professional_amount5.data = p.professional_amount
                    form8.disbursements_desc5.data = p.disbursements_desc
                    form8.disbursements_amount5.data = p.disbursements_amount
                if ((item.index(p)) == 5):
                    form8.professional_desc6.data = p.professional_desc
                    form8.professional_amount6.data = p.professional_amount
                    form8.disbursements_desc6.data = p.disbursements_desc
                    form8.disbursements_amount6.data = p.disbursements_amount
                if ((item.index(p)) == 6):
                    form8.professional_desc7.data = p.professional_desc
                    form8.professional_amount7.data = p.professional_amount
                    form8.disbursements_desc7.data = p.disbursements_desc
                    form8.disbursements_amount7.data = p.disbursements_amount
                if ((item.index(p)) == 7):
                    form8.professional_desc8.data = p.professional_desc
                    form8.professional_amount8.data = p.professional_amount
                    form8.disbursements_desc8.data = p.disbursements_desc
                    form8.disbursements_amount8.data = p.disbursements_amount

    return render_template('invoice_update.html',updt_inv=updt_inv,item=item,inv_id=inv_id,
                            form8=form8,len=len,title='Update Invoice')

@app.route("/Invoice-<int:inv_id>-Delete", methods=['POST'])
@login_required
def delete_invoice(inv_id):
#https://esmithy.net/2020/06/20/sqlalchemy-cascade-delete/
    #updt_inv = Invoice.query.filter_by(id=inv_id).first()
    updt_inv = Invoice.query.get(inv_id)
    item = InvoiceLineItem.query.filter_by(invoice=updt_inv).all()
    #for inv in item.invoice:
    for our_item in item:
        db.session.delete(our_item)
    db.session.delete(updt_inv)
    db.session.commit()
    flash('Your Invoice has been Deleted!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/CreateReceipt',methods=['GET', 'POST'])
@login_required
def Create_Receipt():
    form = ReceiptForm(request.form)
    try:
        get_id = Receipt.query.order_by(desc('id')).first()
        x: int = get_id.id + 1
        y = date.today().strftime("%y%m")
        if get_id:
            receipt_number = "" + y + str(x).zfill(3) + ""
    except:
        receipt_number = str(date.today().strftime("%y%m") + str(1).zfill(3))  
    finally:
    
        #if form.is_submitted():
            #print ("submitted")

        #if form.validate():
            #print ("valid")
        #print(form.errors)
        if form.validate_on_submit():
            receiptAuthor = current_user
            receipt_number = receipt_number
            date_created = request.form['date_created']
            received_from = request.form['received_from']
            sum_in_words = request.form['sum_in_words']
            reason = request.form['reason']
            cash_cheque = request.form['cash_cheque']
            balance  = request.form['balance']
            amount = request.form['amount']
            print(current_user.id)
            print(receiptAuthor,receipt_number,received_from,sum_in_words,reason,cash_cheque,balance,amount)
            new_receipt = Receipt(receipt_number,date_created,received_from,sum_in_words,reason,cash_cheque,balance,amount,current_user.id)
            db.session.add(new_receipt)
            db.session.commit()
            return redirect(url_for('ourReceipts'))
    #receipt = Receipt.query.all()
    return render_template('create_receipt.html',form=form,)

@app.route('/Receipt-<int:rpt_id>')
@login_required
def receipt(rpt_id):
    rpt = Receipt.query.filter( Receipt.id== rpt_id).first()
    return render_template('receipt.html',rpt_id=rpt_id,rpt=rpt)

@app.route("/Receipt-<int:rpt_id>-Update", methods=['GET', 'POST'])
@login_required
def update_receipt(rpt_id):
    updt_rpt = Receipt.query.get_or_404(rpt_id)
    form=ReceiptForm()
    try:
        get_id = Receipt.query.order_by(desc('id')).first()
        x: int = get_id.id + 1
        y = date.today().strftime("%y%m")
        if get_id:
            receipt_number = "" + y + str(x).zfill(3) + ""
    except:
        receipt_number = str(date.today().strftime("%y%m") + str(1).zfill(3))
    finally:
        if request.method == 'POST':

            receipt_number = receipt_number
            updt_rpt.date_created = form.date_created.data
            updt_rpt.received_from = form.received_from.data
            updt_rpt.sum_in_words = form.sum_in_words.data 
            updt_rpt.reason = form.reason.data
            updt_rpt.cash_cheque = form.cash_cheque.data
            updt_rpt.balance = form.balance.data
            updt_rpt.amount = form.amount.data
            db.session.commit()
            flash('Your receipt has been updated!', 'success')
            return redirect(url_for('receipt',rpt_id=rpt_id))
        elif request.method == 'GET':
        
            form.date_created.data = updt_rpt.date_created
            form.received_from.data  = updt_rpt.received_from
            form.sum_in_words.data  = updt_rpt.sum_in_words
            form.reason.data= updt_rpt.reason
            form.cash_cheque.data = updt_rpt.cash_cheque
            form.balance.data = updt_rpt.balance
            form.amount.data = updt_rpt.amount
    return render_template('receipt_update.html',updt_rpt=updt_rpt,rpt_id=rpt_id,form=form,title='Update Receipt')

@app.route("/Receipt-<int:rpt_id>-Delete", methods=['POST'])
@login_required
def delete_receipt(rpt_id):
    dt_rpt = Receipt.query.get_or_404(rpt_id)
    db.session.delete(dt_rpt)
    db.session.commit()
    flash('Your Invoice has been Deleted!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/Receipt_get_pdf/<rpt_id>', methods=['POST'])
@login_required
def receipt_pdf(rpt_id,options=wk_options):
    if request.method =="POST":
        rpt = Receipt.query.filter( Receipt.id== rpt_id).first()
        rendered=render_template('receiptPdf2.html',rpt=rpt)
        css = ['firm/static/css/testing_2.css']
        pdf = pdfkit.from_string(rendered,False,css=css,configuration=_get_pdfkit_config(),options=options)
        response = make_response(pdf)
        response.headers['Content-Type']='application/pdf'
        response.headers['Content-Disposition']='inline; filename=Receipt'+rpt_id+'.pdf'
        return response
    return redirect(url_for('receipt'))

@app.route("/searchReceipts",methods=['GET','POST'])
def receiptSearch():
    page = request.args.get('page',1,type=int)
    myRpt = Receipt.query.order_by(Receipt.receipt_number.desc()).paginate(page = page ,per_page=4)
    if request.method =='POST' and 'tag2' in request.form:
        tag2 = request.form["tag2"]
        search = "%{}%".format(tag2)
        myRpt = Receipt.query.filter(or_(Receipt.received_from.like(search),
                                        Receipt.receipt_number.like(search))).paginate(page=page,per_page=4)
        return render_template('ourReceiptPage.html',myRpt=myRpt,tag2=tag2)
    return render_template('ourReceiptPage.html',myRpt=myRpt)

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', 
                    sender='firm2.herokuapp.com/',
                     recipients=[user.email])
    msg.body = f''' To reset your password, visit the following link: 
{url_for('reset_token',token=token, _external = True)}

If you did not make this request then simply ignore this email and no change will be made.
'''
    mail.send(msg)

@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        send_reset_email(user)
        flash ('An email has been sent with instructions to reset your password.','info')
        return redirect(url_for('index'))
    return render_template('reset_request.html',title ='Reset Password', form = form)

@app.route("/reset_password-<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You can now log in', 'success')
        return redirect(url_for('index'))
    return render_template('reset_token.html',title ='Reset Password', form = form)

@app.route("/Documentation")
def doc():
    return render_template('docs.html',title ='Readme')