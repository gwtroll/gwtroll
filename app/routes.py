from app import app
import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_reg(reg_id):
    conn = get_db_connection()
    reg = conn.execute('SELECT * FROM registrations WHERE id = ?',
                        (reg_id,)).fetchone()
    conn.close()
    if reg is None:
        abort(404)
    return reg

def query_db(query, args=(), one=False):
    cur = get_db_connection().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.route('/')
def index():     
    conn = get_db_connection()
    registrations = conn.execute('SELECT * FROM registrations').fetchall()
    conn.close()
    return render_template('index.html', registrations=registrations)

@app.route('/<int:reg_id>')
def reg(reg_id):
    reg = get_reg(reg_id)
    return render_template('reg.html', reg=reg)

@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        badgeid = request.form['badgeid']
        lodging = request.form['lodging']

        if not badgeid:
            flash('Medallion Number is required!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO registrations (fname, lname, lodging, badgeid) VALUES (?, ?, ?, ?)',
                         (fname, lname, lodging, badgeid))
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
            "SELECT * FROM registrations WHERE fname LIKE ? OR lname LIKE ? OR scaname LIKE ?",
            ('%' + search_value + '%', '%' + search_value + '%', '%' + search_value + '%'))
        return render_template('search.html', searchreg=reg)
    else:
        return render_template('search.html')