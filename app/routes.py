from app import app, db, login, mail
from app.forms import *
from app.models import *
from app.utils.db_utils import *
import psycopg2
import psycopg2.extras
from flask import Flask, render_template, request, url_for, flash, redirect, send_file
import os
from flask_login import current_user, login_user, logout_user, login_required
from flask_security import roles_accepted
import sqlalchemy as sa
import pandas as pd
from datetime import datetime
import re
import csv
import codecs
from flask_mail import Message

#Import pricing from CSV and set global variables
price_df = pd.read_csv('gwpricing.csv')

prereg_sat_price = int(price_df.loc[price_df['arrday'] == 'saturday', 'prereg_price'].values[0])
prereg_sun_price = int(price_df.loc[price_df['arrday'] == 'sunday', 'prereg_price'].values[0])
prereg_mon_price = int(price_df.loc[price_df['arrday'] == 'monday', 'prereg_price'].values[0])
prereg_tue_price = int(price_df.loc[price_df['arrday'] == 'tuesday', 'prereg_price'].values[0])
prereg_wed_price = int(price_df.loc[price_df['arrday'] == 'wednesday', 'prereg_price'].values[0])
prereg_thur_price = int(price_df.loc[price_df['arrday'] == 'thursday', 'prereg_price'].values[0])
prereg_fri_price = int(price_df.loc[price_df['arrday'] == 'friday', 'prereg_price'].values[0])
prereg_sat2_price = int(price_df.loc[price_df['arrday'] == 'saturday2', 'prereg_price'].values[0])
door_sat_price = int(price_df.loc[price_df['arrday'] == 'saturday', 'door_price'].values[0])
door_sun_price = int(price_df.loc[price_df['arrday'] == 'sunday', 'door_price'].values[0])
door_mon_price = int(price_df.loc[price_df['arrday'] == 'monday', 'door_price'].values[0])
door_tue_price = int(price_df.loc[price_df['arrday'] == 'tuesday', 'door_price'].values[0])
door_wed_price = int(price_df.loc[price_df['arrday'] == 'wednesday', 'door_price'].values[0])
door_thur_price = int(price_df.loc[price_df['arrday'] == 'thursday', 'door_price'].values[0])
door_fri_price = int(price_df.loc[price_df['arrday'] == 'friday', 'door_price'].values[0])
door_sat2_price = int(price_df.loc[price_df['arrday'] == 'saturday2', 'door_price'].values[0])
nmr = int(price_df.loc[price_df['arrday'] == 'saturday', 'nmr'].values[0])
opening_day = str(price_df.loc[price_df['arrday'] == 'saturday', 'arrdate'].values[0])
opening_day = int(re.search("\/(\d+)\/", opening_day).group(1)) # Remove month and year so just the day is left
regcount = 0

@login.unauthorized_handler
def unauthorized_callback():
    return redirect('/login?next=' + request.path)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        if not user.active:
            flash('User is Inactive')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    regcount = reg_count()
    if request.method == "POST":
        if request.form.get('search_name'):
            search_value = request.form.get('search_name')
            print(search_value)
            if search_value is not None and search_value != '':
                if request.form.get('search_canceled'):
                    reg = query_db(
                        "SELECT * FROM registrations WHERE (fname ILIKE %s OR lname ILIKE %s OR scaname ILIKE %s) AND (invoice_status NOT IN ('DUPLICATE','SENT','UNSENT') OR invoice_status IS NULL) order by checkin DESC, lname, fname",
                        #(search_value, search_value, search_value))
                        ('%' + search_value + '%', '%' + search_value + '%', '%' + search_value + '%'))
                else:
                    reg = query_db(
                        "SELECT * FROM registrations WHERE (fname ILIKE %s OR lname ILIKE %s OR scaname ILIKE %s) AND (invoice_status NOT IN ('DUPLICATE','CANCELED','SENT','UNSENT') OR invoice_status IS NULL) order by checkin DESC, lname, fname",
                        #(search_value, search_value, search_value))
                        ('%' + search_value + '%', '%' + search_value + '%', '%' + search_value + '%'))
        elif request.form.get('invoice_number'):
            search_value = request.form.get('invoice_number')
            if request.form.get('search_canceled'):
                reg = query_db(
                    "SELECT * FROM registrations WHERE invoice_number LIKE %s AND (invoice_status NOT IN ('DUPLICATE','SENT','UNSENT') OR invoice_status IS NULL) order by checkin DESC, lname, fname",
                    ('%' + search_value + '%',))
            else:
                reg = query_db(
                    "SELECT * FROM registrations WHERE invoice_number LIKE %s AND (invoice_status NOT IN ('DUPLICATE','CANCELED','SENT','UNSENT') OR invoice_status IS NULL) order by checkin DESC, lname, fname",
                    ('%' + search_value + '%',))
        elif request.form.get('medallion'):
            search_value = request.form.get('medallion')
            reg = query_db(
                "SELECT * FROM registrations WHERE medallion = %s order by checkin DESC, lname, fname",
                (search_value,))
        else:
            return render_template('index.html', regcount=regcount)
        for r in reg:
            if r['rate_date'] is not None:
                try:
                    arrival_date = datetime.strptime(r['rate_date'], "%Y-%m-%d %H:%M:%S")
                except:
                    arrival_date = datetime.strptime(r['rate_date'], "%Y-%m-%d")
            else:
                arrival_date = datetime.strptime('01/01/1900', '%m/%d/%Y')
            if (arrival_date == datetime.strptime('03/08/2025','%m/%d/%Y') or arrival_date <= datetime.now()):
                r['rate_date'] = arrival_date
                r['ready_for_checkin'] = True
            else:
                r['rate_date'] = arrival_date
                r['ready_for_checkin'] = False
        return render_template('index.html', searchreg=reg, regcount=regcount)
    else:
        return render_template('index.html', regcount=regcount)

@app.route('/upload', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin')
def upload():
    if request.method == 'POST':   
        # msg = Message(
        #     subject="Hello",
        #     sender="carl.cox.primary@gmail.com",
        #     recipients=["carl.cox.primary@gmail.com"],
        # )
        # msg.html = "<b>testing</b>"
        # mail.send(msg)
        # f = request.files['file'] 
        # f.save(f.filename)

        # s = os.environ['AZURE_POSTGRESQL_CONNECTIONSTRING']
        # conndict = dict(item.split("=") for item in s.split(" "))
        # connstring = "postgresql+psycopg2://" + conndict["user"] + ":" + conndict["password"] + "@" + conndict["host"] + ":5432/" + conndict["dbname"] 
        # engine=db.create_engine(connstring)
        # metadata = db.MetaData()
        # registrations = db.Table('registrations', metadata)

        # root_path = os.path.dirname(os.path.dirname( __file__ ))
        # df = pd.read_csv(os.path.join(root_path,f.filename))


        # # Rename columns from CSV to match DB - order is important
        # df.columns = ['event_id','event_name','order_id','reg_date_time','medallion','fname','lname','scaname_bad','acc_member_id','acc_exp_date','event_ticket','price_paid','order_price','lodging','pay_type','prereg_status','kingdom','regid','scaname','mbr_num_exp','requests','waiver1','waiver2']
        # df = df.drop(columns=['event_id','event_name','scaname_bad','acc_member_id','acc_exp_date','order_price','waiver1','waiver2']) # Remove unwanted columns from the import

        # df[['rate_age']] = df['event_ticket'].str.extract('(Child|18\+|Heirs|K\/Q|Royals)', expand=True) # Split rate, age and arival date from single field
        # df[['rate_mbr']] = df['event_ticket'].str.extract('(Member|Non-Member)', expand=True) # Split rate, age and arival date from single field
        # df[['rate_date']] = df['event_ticket'].str.extract('Arriving (\d+)', expand=True) # Split rate, age and arival date from single field

        # df[['mbr_num']] = df['mbr_num_exp'].str.extract('^(\d{4,})', expand=True) # Extract member number 
        # df['lodging'] = df['lodging'].str.extract('(.*)\s\(\$') # Remove price from camping groups


        # # Import data to DB
        # df.to_sql('registrations', engine, if_exists= 'append', index=False)

        # # Adjust regid for at-the-door registrations
        # conn = psycopg2.connect(os.environ["AZURE_POSTGRESQL_CONNECTIONSTRING"])
        # cur = conn.cursor()
        # cur.execute ('ALTER SEQUENCE registrations_regid_seq RESTART WITH 60001;')
        # conn.commit()
        # conn.close()
        flash("SUCCESS!")
        return redirect(url_for('index'))
    return render_template('upload.html')

@app.route('/full_signature_export', methods=('GET', 'POST'))
@login_required
@roles_accepted('Admin','Department Head','Invoices')
def full_export():
    regs = query_db("SELECT * FROM registrations WHERE signature IS NOT NULL")
    return render_template('full_export_images.html', regs=regs)

@app.route('/reports', methods=['GET', 'POST'])
@login_required
@roles_accepted('Admin','Department Head','Invoices')
def reports():
    form = ReportForm()
    s = os.environ['AZURE_POSTGRESQL_CONNECTIONSTRING']
    conndict = dict(item.split("=") for item in s.split(" "))
    connstring = "postgresql+psycopg2://" + conndict["user"] + ":" + conndict["password"] + "@" + conndict["host"] + ":5432/" + conndict["dbname"] 
    engine=db.create_engine(connstring)
    
    file = 'test_' + str(datetime.now().isoformat(' ', 'seconds').replace(" ", "_")) + '.xlsx'
    #if form.dt_start.data is not None:
    start_date = form.dt_start.data
    #if form.dt_end.data is not None:
    end_date = form.dt_end.data
   
    report_type = form.report_type.data

    if report_type == 'full_signatue_export':
        regs = query_db("SELECT * FROM registrations WHERE signature IS NOT NULL")
        return render_template('full_export_images.html', regs=regs)
    
    if report_type == 'full_export':

        file = 'full_export_' + str(datetime.now().isoformat(' ', 'seconds').replace(" ", "_").replace(":","-")) + '.csv'

        rptquery = "SELECT * FROM registrations"
        df = pd.read_sql_query(rptquery, engine)
        base_price_list = []
        nmr_list = []
        for index, row in df.iterrows():
            if row['rate_mbr'] == 'Non-Member' and row['price_calc'] != 0 and row['rate_age'].__contains__('18+'):
                base_price_list.append(row['price_calc'] - 10)
                nmr_list.append(10)
            else:
                base_price_list.append(row['price_calc'])
                nmr_list.append(0)
        df['nmr'] = nmr_list
        df['base_price'] = base_price_list
        path1 = './reports/' + file
        path2 = '../reports/' + file
        
        df.to_csv(path1)
        return send_file(path2)
        
    if report_type == 'full_checkin_report':
        if form.validate_on_submit():

            file = 'full_checkin_report_' + str(datetime.now().isoformat(' ', 'seconds').replace(" ", "_").replace(":","-")) + '.xlsx'

            rptquery = "SELECT * FROM registrations WHERE checkin::date BETWEEN {} and {}"
            rptquery = rptquery.format('%(start_date)s', '%(end_date)s')
            params = {'start_date':start_date, 'end_date':end_date}
            df = pd.read_sql_query(rptquery, engine, params=params)
            path1 = './reports/' + file
            path2 = '../reports/' + file
            
            writer = pd.ExcelWriter(path1, engine='xlsxwriter')
            df.to_excel(writer, sheet_name='Report' ,index = False)
            worksheet = writer.sheets['Report']
            writer.close()
            return send_file(path2)
    
    if report_type == 'at_door_count':
        if form.validate_on_submit():
            file = 'at_door_count_' + str(datetime.now().isoformat(' ', 'seconds').replace(" ", "_").replace(":","-")) + '.xlsx'

            rptquery = "SELECT count(*), sum(price_calc) FROM registrations WHERE checkin::date BETWEEN {} and {} and prereg_status is Null"
            rptquery = rptquery.format('%(start_date)s', '%(end_date)s')
            params = {'start_date':start_date, 'end_date':end_date}
            df = pd.read_sql_query(rptquery, engine, params=params)
            rptquery = "SELECT count(*), sum(price_calc) FROM registrations WHERE checkin::date BETWEEN {} and {} and prereg_status = {}"
            rptquery = rptquery.format('%(start_date)s', '%(end_date)s', '%(prereg_status)s')
            params = {'start_date':start_date, 'end_date':end_date, 'prereg_status':"SUCCEEDED"}
            df = df.merge(pd.read_sql_query(rptquery, engine, params=params), how='outer')

            path1 = './reports/' + file
            path2 = '../reports/' + file

            writer = pd.ExcelWriter(path1, engine='xlsxwriter')

            df.to_excel(writer, sheet_name='Report' ,index = False, startcol=1)
            workbook = writer.book
            worksheet = writer.sheets["Report"]           
            worksheet.write('A2', "At the Door")
            worksheet.write('A3', "Pre-Reg")
            worksheet.write('C1', "Income Total")

            writer.close()
            return send_file(path2)
    
    if report_type == 'kingdom_count':

        file = 'kingdom_count_' + str(datetime.now().isoformat(' ', 'seconds').replace(" ", "_").replace(":","-")) + '.xlsx'

        df = pd.read_sql("SELECT kingdom, checkin::date, COUNT(regid) FROM registrations WHERE checkin IS NOT NULL GROUP BY kingdom, checkin", engine)
        df_pivot = df.pivot_table(index='kingdom', columns='checkin', values='count', dropna=False)

        path1 = './reports/' + file
        path2 = '../reports/' + file

        writer = pd.ExcelWriter(path1, engine='xlsxwriter')

        # df_pivot.to_excel(writer, sheet_name='Report' ,index = True)

        out = df_pivot.assign(Total=df_pivot.sum(axis=1))
        out = pd.concat([out, out.sum().to_frame('Total').T])
        out.to_excel(writer, sheet_name='Report', index = True)
        workbook = writer.book
        worksheet = writer.sheets["Report"]

        writer.close()
        return send_file(path2)

    if report_type == 'earlyon':

        file = 'earlyon_list_' + str(datetime.now().isoformat(' ', 'seconds').replace(" ", "_").replace(":","-")) + '.xlsx'

        df = pd.read_sql("SELECT regid, invoice_status, fname, lname, scaname, email, kingdom, lodging FROM registrations WHERE early_on = true and invoice_status = 'PAID'", engine)

        df_obj = df.select_dtypes('object')

        df[df_obj.columns] = df_obj.apply(lambda x: x.str.strip())

        path1 = './reports/' + file
        path2 = '../reports/' + file

        writer = pd.ExcelWriter(path1, engine='xlsxwriter')

        df.to_excel(writer, sheet_name='Report' ,index = False)

        writer.close()
        return send_file(path2)

    if report_type == 'ghost_report':

        file = 'ghost_report_' + str(datetime.now().isoformat(' ', 'seconds').replace(" ", "_").replace(":","-")) + '.xlsx'

        rptquery = "SELECT invoice_number, regid, fname, lname, scaname, rate_age, lodging, invoice_status, checkin FROM registrations WHERE prereg_status = {} AND checkin IS NULL ORDER BY lodging"
        rptquery = rptquery.format('%(prereg_status)s')
        params = {'prereg_status':"SUCCEEDED"}
        df = pd.read_sql_query(rptquery, engine, params=params)
        path1 = './reports/' + file
        path2 = '../reports/' + file

        writer = pd.ExcelWriter(path1, engine='xlsxwriter')

        df.to_excel(writer, sheet_name='Report' ,index = False)
        writer.close()
        return send_file(path2)

    if report_type == 'royal_registrations':

        file = 'royal_registrations_' + str(datetime.now().isoformat(' ', 'seconds').replace(" ", "_").replace(":","-")) + '.xlsx'

        df = pd.read_sql("SELECT * FROM registrations WHERE rate_age = 'Royals'", engine)

        path1 = './reports/' + file
        path2 = '../reports/' + file

        writer = pd.ExcelWriter(path1, engine='xlsxwriter')

        df.to_excel(writer, sheet_name='Report' ,index = False)

        writer.close()
        return send_file(path2)

    if report_type == 'land_pre-reg':

        file = 'land_pre-reg_' + str(datetime.now().isoformat(' ', 'seconds').replace(" ", "_").replace(":","-")) + '.xlsx'

        df = pd.read_sql("SELECT lodging, invoice_number, regid, fname, lname, scaname, rate_age, invoice_status FROM registrations WHERE invoice_status = 'PAID' ORDER BY lodging, invoice_number", engine)

        path1 = './reports/' + file
        path2 = '../reports/' + file

        writer = pd.ExcelWriter(path1, engine='xlsxwriter')

        df.to_excel(writer, sheet_name='Report' ,index = False)

        writer.close()
        return send_file(path2)


    if report_type == 'paypal_paid_export':

        file = 'paypal_paid_export_' + str(datetime.now().isoformat(' ', 'seconds').replace(" ", "_").replace(":","-")) + '.csv'

        rptquery = "SELECT invoice_number, invoice_email, invoice_status, invoice_payment_date, rate_mbr, rate_age, price_paid, paypal_donation_amount, notes FROM registrations WHERE invoice_status = 'PAID'"
        df = pd.read_sql_query(rptquery, engine)
        base_price_list = []
        nmr_list = []
        for index, row in df.iterrows():
            if row['rate_mbr'] == 'Non-Member' and row['price_paid'] != 0 and row['rate_age'].__contains__('18+'):
                base_price_list.append(row['price_paid'] - 10 - row['paypal_donation_amount'])
                nmr_list.append(10)
            else:
                base_price_list.append(row['price_paid'] - row['paypal_donation_amount'])
                nmr_list.append(0)
        df['nmr'] = nmr_list
        df['base_price'] = base_price_list
        path1 = './reports/' + file
        path2 = '../reports/' + file
        
        df.to_csv(path1)
        return send_file(path2)
    
    if report_type == 'paypal_canceled_export':

        file = 'paypal_cenceled_export_' + str(datetime.now().isoformat(' ', 'seconds').replace(" ", "_").replace(":","-")) + '.csv'

        rptquery = "SELECT invoice_number, invoice_email, invoice_status, invoice_payment_date, rate_mbr, rate_age, price_paid, price_due, paypal_donation_amount, notes FROM registrations WHERE invoice_status = 'CANCELED'"
        df = pd.read_sql_query(rptquery, engine)
        base_price_list = []
        nmr_list = []
        for index, row in df.iterrows():

            if row['price_paid'] != 0:
                if row['rate_mbr'] == 'Non-Member' and row['price_paid'] != 0 and row['rate_age'].__contains__('18+'):
                    base_price_list.append(row['price_paid'] - 10 - row['paypal_donation_amount'])
                    nmr_list.append(10)
                else:
                    base_price_list.append(row['price_paid'] - row['paypal_donation_amount'])
                    nmr_list.append(0)
            else:
                if row['rate_mbr'] == 'Non-Member' and row['price_due'] != 0 and row['rate_age'].__contains__('18+'):
                    base_price_list.append(row['price_due'] - 10 - row['paypal_donation_amount'])
                    nmr_list.append(10)
                else:
                    base_price_list.append(row['price_due'] - row['paypal_donation_amount'])
                    nmr_list.append(0)
        df['nmr'] = nmr_list
        df['base_price'] = base_price_list
        path1 = './reports/' + file
        path2 = '../reports/' + file
        
        df.to_csv(path1)
        return send_file(path2)
    
    if report_type == 'paypal_recon_export':


        invoice_nums = []
        paypal_invoice_nums = []
        counts = []
        counts_obj = {}
        dirty_obj = {}
        errors = []

        paypal_recon_file = request.files['paypal_file']

        merchant_df = pd.read_csv('merchant_fees.csv')
        merchant_dict = merchant_df.to_dict(orient='records')
        merchant_dict_exclude = {}

        for merchant in merchant_dict:
            for col in merchant:
                if not isinstance(merchant[col], int):
                     merchant[col] = float(merchant[col])
                merchant_dict_exclude[merchant['Invoice Number']] = merchant

        # csv_reader = csv.DictReader(paypal_recon_file)
        csv_reader = csv.DictReader(codecs.iterdecode(paypal_recon_file, 'utf-8'))

        for row in csv_reader:
            for col in row:
                if row[col].strip().startswith('$'):
                    row[col] = row[col].strip().replace("$","").replace("(","").replace(")","").replace(",","").replace("-","").replace("'",'').replace('"','')
                    if row[col].strip() != '':
                        row[col] = float(row[col].strip())
                    else: 
                        row[col] = 0
            dirty_obj[row['Invoice Number']] = row
            invoice_nums.append("'"+str(row['Invoice Number'])+"'")
            paypal_invoice_nums.append(str(row['Invoice Number']))

        for row in dirty_obj:
            counts_obj[row] = {
                'Date':None,
                'Time':None,
                'Name':'',
                'From Email Address':'',
                'Invoice Number':'',
                'Gross':0.00,
                'Fee':0.00,
                'Net':0.00,
                'Balance':0.00,
                'price_paid':0.00,
                'paypal_donation_amount':0.00,
                'nmr':0,
                'base_price':0.00,
                'expected_fee':0.00,
                'is_merchant':False,
                'To Email Address':'',
                'Transaction ID':'',
                'CounterParty Status':'',
                'Address Status':'',
                'Item Title':'',
                'Reference Txn ID':'',
                'Receipt ID':'',
                'Contact Phone Number':'',
                'Subject':'',
                'Payment Source':''
            }
            for col in dirty_obj[row].keys():
                if col == '\ufeff"Date"':
                    counts_obj[row]['Date'] = dirty_obj[row][col]
                if col not in ['TimeZone','Status','Currency','Note','Card Type','Type','Transaction Event Code','Balance Impact','\ufeff"Date"']:
                    if col in ['Gross','Fee','Net']:
                        dirty_obj[row][col] = dirty_obj[row][col].strip().replace("$","").replace("(","").replace(")","").replace(",","").replace("-","").replace("'",'')
                        counts_obj[row][col.strip()] = float(dirty_obj[row][col].strip())
                    else:
                        counts_obj[row][col.strip()] = dirty_obj[row][col]

        invoice_nums_str = ','.join(invoice_nums)

        file = 'paypal_recon_export_' + str(datetime.now().isoformat(' ', 'seconds').replace(" ", "_").replace(":","-")) + '.xlsx'

        rptquery = f"SELECT invoice_number, invoice_email, invoice_status, invoice_payment_date, rate_mbr, rate_age, price_paid, paypal_donation_amount FROM registrations WHERE pay_type = 'paypal' AND (invoice_status = 'PAID' or invoice_status = 'CANCELED') AND invoice_number IN ({invoice_nums_str})"
        df = pd.read_sql_query(rptquery, engine)
        base_price_list = []
        nmr_list = [] 
        checks_list = []
        found_invoices = []

        for index, row in df.iterrows():
            found_invoices.append(row['invoice_number'])
            if row['rate_mbr'] == 'Non-Member' and row['price_paid'] != 0 and row['rate_age'].__contains__('18+'):
                base_price_list.append(row['price_paid'] - 10 - row['paypal_donation_amount'])
                nmr_list.append(10)
                row['base_price'] = row['price_paid'] - 10 - row['paypal_donation_amount']
                row['nmr'] = 10
            else:
                base_price_list.append(row['price_paid'] - row['paypal_donation_amount'])
                nmr_list.append(0)
                row['base_price'] = row['price_paid'] - row['paypal_donation_amount']
                row['nmr'] = 0

            if row['invoice_number'] not in counts_obj:
                obj = {'price_paid':float(row['price_paid']),'paypal_donation_amount':row['paypal_donation_amount'],'nmr':row['nmr'],'base_price':row['base_price']}
                counts_obj[row['invoice_number']] = obj
            else:
                counts_obj[row['invoice_number']]['price_paid'] += round(float(row['price_paid']),2)
                counts_obj[row['invoice_number']]['paypal_donation_amount'] += row['paypal_donation_amount']
                counts_obj[row['invoice_number']]['nmr'] += row['nmr']
                counts_obj[row['invoice_number']]['base_price'] += row['base_price']

        df['nmr'] = nmr_list
        df['base_price'] = base_price_list

        for obj in counts_obj:
            if obj != '' and obj is not None:
                if int(obj) in merchant_dict_exclude:
                    counts_obj[obj]['price_paid'] = merchant_dict_exclude[int(obj)]['Gross']
                    counts_obj[obj]['expected_fee'] = merchant_dict_exclude[int(obj)]['Fee']
                    counts_obj[obj]['is_merchant'] = True
                else:
                    if counts_obj[obj]['price_paid'] != 0:
                        expected_fee = round(counts_obj[obj]['price_paid'] * 0.0199 + 0.49,2)
                    else:
                        expected_fee = 0.00
                    counts_obj[obj]['expected_fee'] = expected_fee
                    if counts_obj[obj]['price_paid'] != counts_obj[obj]['Gross']:
                        errors.append({"Invoice Number":obj,'Error':"GROSS DOES NOT MATCH PRICE PAID",'PayPal': counts_obj[obj]['Gross'],'Export':counts_obj[obj]['price_paid'],'Email':counts_obj[obj]['From Email Address']})
                    if expected_fee != counts_obj[obj]['Fee']:
                        errors.append({"Invoice Number":obj,'Error':"EXPECTED FEE DOES NOT MATCH PAYPAL",'PayPal': counts_obj[obj]['Fee'],'Export':expected_fee,'Email':counts_obj[obj]['From Email Address']})
                counts.append(counts_obj[obj])
        
        rptquery = f"SELECT invoice_number, invoice_email, invoice_status, invoice_payment_date, rate_mbr, rate_age, price_paid, paypal_donation_amount FROM registrations WHERE pay_type = 'check' AND invoice_status = 'PAID'"
        df = pd.read_sql_query(rptquery, engine)

        for index, row in df.iterrows():
            if row['rate_mbr'] == 'Non-Member' and row['price_paid'] != 0 and row['rate_age'].__contains__('18+'):
                base_price_list.append(row['price_paid'] - 10 - row['paypal_donation_amount'])
                nmr_list.append(10)
                row['base_price'] = row['price_paid'] - 10 - row['paypal_donation_amount']
                row['nmr'] = 10
            else:
                base_price_list.append(row['price_paid'] - row['paypal_donation_amount'])
                nmr_list.append(0)
                row['base_price'] = row['price_paid'] - row['paypal_donation_amount']
                row['nmr'] = 0
            checks_list.append(row)
        
        unmatched_invoices = []
        for paypal_invoice_num in paypal_invoice_nums:
            if paypal_invoice_num not in found_invoices and paypal_invoice_num != '':
                rptquery = f"SELECT invoice_number, invoice_email, invoice_status, invoice_payment_date, rate_mbr, rate_age, price_paid, paypal_donation_amount FROM registrations WHERE pay_type = 'paypal' AND invoice_status = 'PAID' AND invoice_number LIKE '%%{paypal_invoice_num}%%'"
                df = pd.read_sql_query(rptquery, engine)
                for index, row in df.iterrows():
                    if row['rate_mbr'] == 'Non-Member' and row['price_paid'] != 0 and row['rate_age'].__contains__('18+'):
                        row['base_price'] = row['price_paid'] - 10 - row['paypal_donation_amount']
                        row['nmr'] = 10
                    else:
                        row['base_price'] = row['price_paid'] - row['paypal_donation_amount']
                        row['nmr'] = 0
                    row['paypal_match'] = paypal_invoice_num
                    row['Gross'] = counts_obj[paypal_invoice_num]['Gross']
                    row['Fee'] = counts_obj[paypal_invoice_num]['Fee']
                    row['Net'] = counts_obj[paypal_invoice_num]['Net']
                    unmatched_invoices.append(row)
        

        path1 = './reports/' + file
        path2 = '../reports/' + file
        
        writer = pd.ExcelWriter(path1, engine='xlsxwriter')
        
        pd.DataFrame(counts).to_excel(writer, sheet_name='Report' ,index = True)
        pd.DataFrame(unmatched_invoices).to_excel(writer, sheet_name='Partial Match' ,index = True)
        pd.DataFrame(errors).to_excel(writer, sheet_name='Errors' ,index = True)
        pd.DataFrame(checks_list).to_excel(writer,sheet_name='Checks',index=True)

        writer.close()
        return send_file(path2)
    
    if report_type == 'atd_export':

        file = 'paypal_paid_export_' + str(datetime.now().isoformat(' ', 'seconds').replace(" ", "_").replace(":","-")) + '.csv'

        rptquery = "SELECT checkin, rate_mbr, rate_age, notes, price_paid, pay_type, atd_paid, atd_pay_type, paypal_donation_amount FROM registrations WHERE checkin::date BETWEEN {} and {}"
        rptquery = rptquery.format('%(start_date)s', '%(end_date)s')
        params = {'start_date':start_date, 'end_date':end_date}
        df = pd.read_sql_query(rptquery, engine, params=params)

        base_price_list = []
        nmr_list = []
        for index, row in df.iterrows():
            if row['rate_mbr'] == 'Non-Member' and row['atd_paid'] != 0 and row['rate_age'].__contains__('18+'):
                base_price_list.append(row['atd_paid'] - 10 - row['paypal_donation_amount'])
                nmr_list.append(10)
            else:
                base_price_list.append(row['atd_paid'] - row['paypal_donation_amount'])
                nmr_list.append(0)
        df['nmr'] = nmr_list
        df['base_price'] = base_price_list
        path1 = './reports/' + file
        path2 = '../reports/' + file
        
        df.to_csv(path1)
        return send_file(path2)
    
    if report_type == 'log_export':

        file = 'log_export_' + str(datetime.now().isoformat(' ', 'seconds').replace(" ", "_").replace(":","-")) + '.csv'

        rptquery = "SELECT id, regid, userid, (SELECT username FROM users WHERE users.id = reglogs.userid), timestamp, action FROM reglogs"
        df = pd.read_sql_query(rptquery, engine)

        path1 = './reports/' + file
        path2 = '../reports/' + file
        
        df.to_csv(path1)
        return send_file(path2)

    if report_type == 'minor_waivers':
        file = 'minor_waivers_' + str(datetime.now().isoformat(' ', 'seconds').replace(" ", "_").replace(":","-")) + '.csv'

        rptquery = "SELECT regid, fname, lname, minor_waiver FROM registrations WHERE minor_waiver IS NOT NULL"
        df = pd.read_sql_query(rptquery, engine)

        path1 = './reports/' + file
        path2 = '../reports/' + file
        
        df.to_csv(path1)
        return send_file(path2)

    return render_template('reports.html', form=form)