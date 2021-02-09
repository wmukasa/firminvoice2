from datetime import datetime, date
from flask import Flask,render_template,request,url_for,flash,redirect, make_response 
from firm.models import User,Invoice,InvoiceLineItem
from firm.forms import( RegistrationForm, LoginForm,UpdateAccountForm,
                Invoice_Items,LapForm,MainForm,Invoice_Items2,Invoice_Items3,Invoice_Items4)
from firm import app
from sqlalchemy import desc
from firm import db,bcrypt
from flask_login import login_user,current_user,logout_user,login_required
import os, sys, subprocess, platform
import pdfkit

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
    #myInv = Invoice.query.paginate(page = page ,per_page=4)
    myInv = Invoice.query.order_by(Invoice.ref_number.desc()).paginate(page = page ,per_page=4)
    return render_template('dashboard.html',myInv=myInv)

@app.route('/SavedInvoice-<int:inv_id>')
@login_required
def saved_invoice(inv_id):
    subtotal = 0
    VAT =0
    grandtotal =0
    myPro =0
    inv = Invoice.query.filter( Invoice.id== inv_id).first()
    #myVat=(float(inv.vat))/100 
    item = InvoiceLineItem.query.filter_by(invoice=inv).all()
    for q in item:
        subtotal +=float(q.amount)
        #VAT is only on professional price 
        myPro +=q.professional_fees 
        VAT = (18/100)* float(myPro)
        #VAT = myVat*subtotal
        grandtotal = float(VAT+subtotal)
    #print(subtotal)
    #print(VAT)
    #(grandtotal)
    return render_template('saved_invoice.html',inv=inv,item=item,inv_id=inv_id, myPro= myPro,
                        subtotal=subtotal,grandtotal=grandtotal,VAT=VAT,len=len,title='SavedInvoice')

@app.route('/get_pdf/<inv_id>', methods=['POST'])
@login_required
def get_pdf(inv_id,options=wk_options):
    subtotal = 0
    VAT =0
    myPro =0
    grandtotal =0
    if request.method =="POST":
        inv = Invoice.query.filter( Invoice.id== inv_id).first()
        #print(inv.vat)
        #myVat=(float(inv.vat))/100
        item = InvoiceLineItem.query.filter_by(invoice=inv).all()
        for q in item:
            subtotal +=float(q.amount)
            myPro +=q.professional_fees 
            print(myPro)  
            VAT = (18/100)* float(myPro)
            grandtotal = float(VAT+subtotal)
        rendered=render_template('testing.html',myPro= myPro,
                                    subtotal=subtotal,grandtotal=grandtotal,VAT=VAT,inv=inv,item=item,len=len)
        css = ['firm/templates/testing.css']
        pdf = pdfkit.from_string(rendered,False,css=css,configuration=_get_pdfkit_config(),options=options)
        response = make_response(pdf)
        response.headers['Content-Type']='application/pdf'
        response.headers['Content-Disposition']='inline; filename='+inv_id+'.pdf'
        return response
    return redirect(url_for('saved_invoice'))

@app.route('/getProForma_pdf/<inv_id>', methods=['POST'])
@login_required
def getProForma_pdf(inv_id,options=wk_options):
    subtotal = 0
    VAT =0
    myPro =0
    grandtotal =0
    if request.method =="POST":
        inv = Invoice.query.filter( Invoice.id== inv_id).first()
        item = InvoiceLineItem.query.filter_by(invoice=inv).all()
        for q in item:
            subtotal +=float(q.amount)
            myPro +=q.professional_fees 
            VAT = (18/100)* float(myPro)
            grandtotal = float(VAT+subtotal)
        rendered=render_template('proForma.html',myPro= myPro,
                                    subtotal=subtotal,grandtotal=grandtotal,VAT=VAT,inv=inv,item=item,len=len)
        css = ['firm/templates/testing.css']
        pdf = pdfkit.from_string(rendered,False,css=css,configuration=_get_pdfkit_config(),options=options)
        response = make_response(pdf)
        response.headers['Content-Type']='application/pdf'
        response.headers['Content-Disposition']='inline; filename='+inv_id+'.pdf'
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
    form = MainForm()
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
            # Create race
            author = current_user
            ref_number = ref_number
            name_to = request.form['name_to']
            address_to = request.form['address_to']
            email_to = request.form['email_to']
            telephone_to = request.form['telephone_to']
            box_number_to = request.form['box_number_to']
            vat = request.form['vat']
            terms = request.form['terms']
            issue_date = request.form['issue_date']
            due_date = request.form['due_date']

            new_invoice = Invoice(ref_number,name_to,address_to,telephone_to,email_to,box_number_to,vat,terms,issue_date,due_date,current_user.id)

            db.session.add(new_invoice)

            for lap in form.laps.data:
                new_lap = InvoiceLineItem(**lap)

                # Add to race
                new_invoice.laps.append(new_lap)

            db.session.commit()
            return redirect(url_for('dashboard'))

    invoice = Invoice.query.all()

    return render_template(
        'invoice_items.html',
        form=form,
        invoice=invoice,
        _template=template_form
    )
#for second template during creating
@app.route('/ProformaInvoice-<int:inv_id>')
@login_required
def proform_invoice(inv_id):
    subtotal = 0
    grandtotal =0
    myPro = 0
    VAT=0
    inv = Invoice.query.filter( Invoice.id== inv_id).first()
    item = InvoiceLineItem.query.filter_by(invoice=inv).all()
    for q in item:
        subtotal +=float(q.amount)
        myPro +=(q.professional_fees)   
        VAT = (18/100)* float(myPro)
        print(VAT)
        #VAT = myVat*subtotal
        grandtotal = float(VAT+subtotal)
    #print(subtotal)
    #print(VAT)
    #(grandtotal)
    return render_template('proforma_invoice.html',inv=inv,item=item,VAT=VAT,myPro=myPro,
                        subtotal=subtotal,grandtotal=grandtotal,len=len,title='Pro forma Invoice')
    
@app.route("/Invoice-<int:inv_id>-Update", methods=['GET', 'POST'])
@login_required
def update_invoice(inv_id):
    today = date.today()
    updt_inv = Invoice.query.get_or_404(inv_id)
    #print(updt_inv)
    #print(updt_inv.name_to)
    item = InvoiceLineItem.query.filter_by(invoice=updt_inv).all()
    #for p in item:
        #print (p.item_name)
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
            updt_inv.telephone_to = form1.telephone_to.data 
            updt_inv.box_number_to = form1.box_number_to.data 
            updt_inv.vat = form1.vat.data 
            updt_inv.terms = form1.terms.data 
            updt_inv.issue_date = form1.issue_date.data
            updt_inv.due_date = form1.due_date.data   
            for p in item: 
                p.notes = form1.notes.data
                p.disbursements = form1.disbursements.data
                p.professional_fees = form1.professional_fees.data
                p.amount = form1.amount.data
        
            db.session.commit()
            flash('Your log has been updated!', 'success')
            return redirect(url_for('saved_invoice',inv_id=inv_id,today=today))
        elif request.method == 'GET':
        
            form1.name_to.data = updt_inv.name_to
            form1.address_to.data  = updt_inv.address_to
            form1.email_to.data  = updt_inv.email_to
            form1.telephone_to.data= updt_inv.telephone_to
            form1.box_number_to.data = updt_inv.box_number_to
            #form1.ref_number.data = updt_inv.ref_number
            form1.terms.data = updt_inv.terms
            form1.issue_date.data = updt_inv.issue_date
            form1.due_date.data = updt_inv.due_date
            form1.vat.data = updt_inv.vat
            #print(len(item))
            for p in item:
                #print(p.id,p.invoice_id)
                form1.notes.data = p.notes
                form1.disbursements.data = p.disbursements
                form1.professional_fees.data = p.professional_fees
                form1.amount.data = p.amount
    return render_template('invoice_update.html',updt_inv=updt_inv,item=item,inv_id=inv_id,
                            form1=form1,len=len,title='Update Invoice')

@app.route("/Invoice2-<int:inv_id>-Update", methods=['GET', 'POST'])
@login_required
def update_invoice2(inv_id):
    today = date.today()
    updt_inv = Invoice.query.get_or_404(inv_id)
    item = InvoiceLineItem.query.filter_by(invoice=updt_inv).all()
    form2=Invoice_Items()
    
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
            updt_inv.telephone_to = form2.telephone_to.data 
            updt_inv.box_number_to = form2.box_number_to.data 
            updt_inv.vat = form2.vat.data 
            updt_inv.terms = form2.terms.data 
            updt_inv.issue_date = form2.issue_date.data
            updt_inv.due_date = form2.due_date.data 
           
            for p in item:
                if ((item.index(p)) == 0):
                    p.notes = form2.notes.data
                    p.disbursements = form2.disbursements.data
                    p.professional_fees = form2.professional_fees.data
                    p.amount = form2.amount.data
                if ((item.index(p)) == 1):
                    p.notes = form2.notes2.data
                    p.disbursements = form2.disbursements2.data
                    p.professional_fees = form2.professional_fees2.data
                    p.amount = form2.amount2.data
        
            db.session.commit()
            flash('Your log has been updated!', 'success')
            return redirect(url_for('saved_invoice',inv_id=inv_id,today=today))
        elif request.method == 'GET':
        
            form2.name_to.data = updt_inv.name_to
            form2.address_to.data  = updt_inv.address_to
            form2.email_to.data  = updt_inv.email_to
            form2.telephone_to.data= updt_inv.telephone_to
            form2.terms.data = updt_inv.terms
            form2.issue_date.data = updt_inv.issue_date
            form2.due_date.data = updt_inv.due_date
            form2.box_number_to.data = updt_inv.box_number_to
            form2.vat.data = updt_inv.vat  
            for p in item:
                #print(p.id,p.invoice_id)
                if ((item.index(p)) == 0):
                    form2.notes.data = p.notes
                    form2.disbursements.data = p.disbursements
                    form2.professional_fees.data = p.professional_fees
                    form2.amount.data = p.amount
                if ((item.index(p)) == 1):
                    form2.notes2.data = p.notes
                    form2.disbursements2.data = p.disbursements
                    form2.professional_fees2.data = p.professional_fees
                    form2.amount2.data = p.amount

    return render_template('invoice_update.html',updt_inv=updt_inv,item=item,inv_id=inv_id,
                            form2=form2,len=len,title='Update Invoice')
@app.route("/Invoice3-<int:inv_id>-Update", methods=['GET', 'POST'])
@login_required
def update_invoice3(inv_id):
    today = date.today()
    updt_inv = Invoice.query.get_or_404(inv_id)
    item = InvoiceLineItem.query.filter_by(invoice=updt_inv).all()
    form3=Invoice_Items2()
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
            updt_inv.telephone_to = form3.telephone_to.data 
            updt_inv.box_number_to = form3.box_number_to.data 
            updt_inv.vat = form3.vat.data 
            updt_inv.terms = form3.terms.data 
            updt_inv.issue_date = form3.issue_date.data
            updt_inv.due_date = form3.due_date.data   
            for p in item:
                if ((item.index(p)) == 0):
                    p.notes = form3.notes.data
                    p.disbursements = form3.disbursements.data
                    p.professional_fees = form3.professional_fees.data
                    p.amount = form3.amount.data
                if ((item.index(p)) == 1):
                    p.notes = form3.notes2.data
                    p.disbursements = form3.disbursements2.data
                    p.professional_fees = form3.professional_fees2.data
                    p.amount = form3.amount2.data
                if ((item.index(p)) == 2):
                    p.notes = form3.notes3.data
                    p.disbursements = form3.disbursements3.data
                    p.professional_fees = form3.professional_fees3.data
                    p.amount = form3.amount3.data
            db.session.commit()
            flash('Your log has been updated!', 'success')
            return redirect(url_for('saved_invoice',inv_id=inv_id,today=today))
        elif request.method == 'GET':
        
            form3.name_to.data = updt_inv.name_to
            form3.address_to.data  = updt_inv.address_to
            form3.email_to.data  = updt_inv.email_to
            form3.telephone_to.data= updt_inv.telephone_to
            #form3.ref_number.data = updt_inv.ref_number
            form3.terms.data = updt_inv.terms
            form3.issue_date.data = updt_inv.issue_date
            form3.due_date.data = updt_inv.due_date
            form3.box_number_to.data = updt_inv.box_number_to
            form3.vat.data = updt_inv.vat 
            for p in item:
                #print(p.id,p.invoice_id)
                if ((item.index(p)) == 0):
                    form3.notes.data = p.notes
                    form3.disbursements.data = p.disbursements
                    form3.professional_fees.data = p.professional_fees
                    form3.amount.data = p.amount
                if ((item.index(p)) == 1):
                    form3.notes2.data = p.notes
                    form3.disbursements2.data = p.disbursements
                    form3.professional_fees2.data = p.professional_fees
                    form3.amount2.data = p.amount
                if ((item.index(p)) == 2):
                    form3.notes3.data = p.notes
                    form3.disbursements3.data = p.disbursements
                    form3.professional_fees3.data = p.professional_fees
                    form3.amount3.data = p.amount
    return render_template('invoice_update.html',updt_inv=updt_inv,item=item,inv_id=inv_id,
                            form3=form3,len=len,title='Update Invoice')
@app.route("/Invoice4-<int:inv_id>-Update", methods=['GET', 'POST'])
@login_required
def update_invoice4(inv_id):
    today = date.today()
    updt_inv = Invoice.query.get_or_404(inv_id)
    item = InvoiceLineItem.query.filter_by(invoice=updt_inv).all()
    form4=Invoice_Items3()
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
            updt_inv.telephone_to = form4.telephone_to.data 
            updt_inv.box_number_to = form4.box_number_to.data 
            updt_inv.vat = form4.vat.data 
            updt_inv.terms = form4.terms.data 
            updt_inv.issue_date = form4.issue_date.data
            updt_inv.due_date = form4.due_date.data   
            for p in item:
                if ((item.index(p)) == 0):
                    p.notes = form4.notes.data
                    p.disbursements = form4.disbursements.data
                    p.professional_fees = form4.professional_fees.data
                    p.amount = form4.amount.data
                if ((item.index(p)) == 1):
                    p.notes = form4.notes2.data
                    p.disbursements = form4.disbursements2.data
                    p.professional_fees = form4.professional_fees2.data
                    p.amount = form4.amount2.data
                if ((item.index(p)) == 2):
                    p.notes = form4.notes3.data
                    p.disbursements = form4.disbursements3.data
                    p.professional_fees = form4.professional_fees3.data
                    p.amount = form4.amount3.data
                if ((item.index(p)) == 3):
                    p.notes = form4.notes4.data
                    p.disbursements = form4.disbursements4.data
                    p.professional_fees = form4.professional_fees4.data
                    p.amount = form4.amount4.data
            db.session.commit()
            flash('Your log has been updated!', 'success')
            return redirect(url_for('saved_invoice',inv_id=inv_id,today=today))
        elif request.method == 'GET':
        
            form4.name_to.data = updt_inv.name_to
            form4.address_to.data  = updt_inv.address_to
            form4.email_to.data  = updt_inv.email_to
            form4.telephone_to.data= updt_inv.telephone_to
            form4.terms.data = updt_inv.terms
            form4.issue_date.data = updt_inv.issue_date
            form4.due_date.data = updt_inv.due_date
            form4.box_number_to.data = updt_inv.box_number_to
            form4.vat.data = updt_inv.vat 
            for p in item:
                #print(p.id,p.invoice_id)
                if ((item.index(p)) == 0):
                    form4.notes.data = p.notes
                    form4.disbursements.data = p.disbursements
                    form4.professional_fees.data = p.professional_fees
                    form4.amount.data = p.amount
                if ((item.index(p)) == 1):
                    form4.notes2.data = p.notes
                    form4.disbursements2.data = p.disbursements
                    form4.professional_fees2.data = p.professional_fees
                    form4.amount2.data = p.amount
                if ((item.index(p)) == 2):
                    form4.notes3.data = p.notes
                    form4.disbursements3.data = p.disbursements
                    form4.professional_fees3.data = p.professional_fees
                    form4.amount3.data = p.amount
                if ((item.index(p)) == 3):
                    form4.notes4.data = p.notes
                    form4.disbursements4.data = p.disbursements
                    form4.professional_fees4.data = p.professional_fees
                    form4.amount4.data = p.amount

    return render_template('invoice_update.html',updt_inv=updt_inv,item=item,inv_id=inv_id,
                            form4=form4,len=len,title='Update Invoice')

@app.route("/Invoice5-<int:inv_id>-Update", methods=['GET', 'POST'])
@login_required
def update_invoice5(inv_id):
    today = date.today()
    updt_inv = Invoice.query.get_or_404(inv_id)
    item = InvoiceLineItem.query.filter_by(invoice=updt_inv).all()
    form5=Invoice_Items4()
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
            updt_inv.telephone_to = form5.telephone_to.data 
            updt_inv.box_number_to = form5.box_number_to.data 
            updt_inv.vat = form5.vat.data  
            updt_inv.terms = form5.terms.data 
            updt_inv.issue_date = form5.issue_date.data
            updt_inv.due_date = form5.due_date.data   
            for p in item:
                if ((item.index(p)) == 0):
                    p.notes = form5.notes.data
                    p.disbursements = form5.disbursements.data
                    p.professional_fees = form5.professional_fees.data
                    p.amount = form5.amount.data
                if ((item.index(p)) == 1):
                    p.notes = form5.notes2.data
                    p.disbursements = form5.disbursements2.data
                    p.professional_fees = form5.professional_fees2.data
                    p.amount = form5.amount2.data
                if ((item.index(p)) == 2):
                    p.notes = form5.notes3.data
                    p.disbursements = form5.disbursements3.data
                    p.professional_fees = form5.professional_fees3.data
                    p.amount = form5.amount3.data
                if ((item.index(p)) == 3):
                    p.notes = form5.notes4.data
                    p.disbursements = form5.disbursements4.data
                    p.professional_fees = form5.professional_fees4.data
                    p.amount = form5.amount4.data
                if ((item.index(p)) == 4):
                    p.notes = form5.notes5.data
                    p.disbursements = form5.disbursements5.data
                    p.professional_fees = form5.professional_fees5.data
                    p.amount = form5.amount5.data
            db.session.commit()
            flash('Your log has been updated!', 'success')
            return redirect(url_for('saved_invoice',inv_id=inv_id,today=today))
        elif request.method == 'GET':
        
            form5.name_to.data = updt_inv.name_to
            form5.address_to.data  = updt_inv.address_to
            form5.email_to.data  = updt_inv.email_to
            form5.telephone_to.data= updt_inv.telephone_to
            form5.terms.data = updt_inv.terms
            form5.issue_date.data = updt_inv.issue_date
            form5.due_date.data = updt_inv.due_date
            form5.box_number_to.data = updt_inv.box_number_to
            form5.vat.data = updt_inv.vat 
            for p in item:
                #print(p.id,p.invoice_id)
                if ((item.index(p)) == 0):
                    form5.notes.data = p.notes
                    form5.disbursements.data = p.disbursements
                    form5.professional_fees.data = p.professional_fees
                    form5.amount.data = p.amount

                if ((item.index(p)) == 1):
                    form5.notes2.data = p.notes
                    form5.disbursements2.data = p.disbursements
                    form5.professional_fees2.data = p.professional_fees
                    form5.amount2.data = p.amount

                if ((item.index(p)) == 2):
                    form5.notes3.data = p.notes
                    form5.disbursements3.data = p.disbursements
                    form5.professional_fees3.data = p.professional_fees
                    form5.amount3.data = p.amount

                if ((item.index(p)) == 3):
                    form5.notes4.data = p.notes
                    form5.disbursements4.data = p.disbursements
                    form5.professional_fees4.data = p.professional_fees
                    form5.amount4.data = p.amount

                if ((item.index(p)) == 4):
                    form5.notes5.data = p.notes
                    form5.disbursements5.data = p.disbursements
                    form5.professional_fees5.data = p.professional_fees
                    form5.amount5.data = p.amount

    return render_template('invoice_update.html',updt_inv=updt_inv,item=item,inv_id=inv_id,
                            form5=form5,len=len,title='Update Invoice')

@app.route("/Invoice-<int:inv_id>-Update", methods=['POST'])
@login_required
def delete_invoice(inv_id):
    updt_inv = Invoice.query.get_or_404(inv_id)
    item = InvoiceLineItem.query.filter_by(invoice=updt_inv).all()
    db.session.delete(updt_inv)
    db.session.commit()
    flash('Your Invoice has been Deleted!', 'success')
    return redirect(url_for('saved_invoice.html'))
