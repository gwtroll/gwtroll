from app import app
import psycopg2
import psycopg2.extras
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort

def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="gwtroll-database",
        user="gwtroll-database",
        password="GWTr0ll2024!")
        #user=os.environ["DB_USERNAME"],
        #password=os.environ["DB_PASSWORD"])
    #cur = conn.cursor()


    #conn.row_factory = sqlite3.Row
    return conn

def get_reg(reg_id):
    conn= get_db_connection()
    cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    cur.execute('SELECT * FROM registrations WHERE id = %s;', (reg_id,))
    reg = cur.fetchone()
    conn.close()
    if reg is None:
        abort(404)
    return reg

def query_db(query, args=(), one=False):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv

@app.route('/')
def index():     
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    cur.execute('SELECT * FROM registrations;')
    registrations = cur.fetchall()
    conn.close()
    for reg in registrations:
        print(reg)
    return render_template('index.html', registrations=registrations)

@app.route('/<int:reg_id>', methods=('GET', 'POST'))
def reg(reg_id):
    if request.method == 'POST':
        return redirect(url_for('checkin', reg_id=reg_id))
    else:
        reg = get_reg(reg_id)
    return render_template('reg.html', reg=reg)

@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        scaname = request.form['scaname']
        lodging = request.form['lodging']

        if not lodging:
            flash('Lodging is required!')
        else:
            conn = get_db_connection()
            cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
            cur.execute('INSERT INTO registrations (fname, lname, scaname, lodging) VALUES (%s, %s, %s, %s);',
                         (fname, lname, scaname, lodging))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template(
        'create.html',
        lodgingdata=[{'lodging': "Open Camping"}, {'lodging': "Ansteorra - Namron"}, {'lodging': "RV"},
                    {'lodging': 'Nova'}, {'lodging': "Ansteorra - Northkeep"}])

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == "POST":
        search_value = request.form.get('search_name')
        print(search_value)
        reg = query_db(
            "SELECT * FROM registrations WHERE fname LIKE %s OR lname LIKE %s OR scaname LIKE %s",
            ('%' + search_value + '%', '%' + search_value + '%', '%' + search_value + '%'))
        return render_template('search.html', searchreg=reg)
    else:
        return render_template('search.html')

@app.route('/checkin', methods=['GET', 'POST'])
def checkin():
    reg_id = request.args['reg_id']
    reg = get_reg(reg_id)
        
    if request.method == 'POST':
        medallion = request.form['medallion']

        if not medallion:
            flash('Medallion is required!')
        else:
            conn = get_db_connection()
            cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
            cur.execute('UPDATE registrations SET medallion = %s WHERE id = %s;',
                         (medallion, reg_id))
            conn.commit()
            conn.close()
            return redirect(url_for('reg', reg_id=reg_id))

    return render_template('checkin.html', reg=reg)

