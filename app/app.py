from flask import Flask, render_template, url_for, request, redirect, session, make_response
import sqlite3 as sql
from functools import wraps
import re
import ibm_db
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import datetime, timedelta

conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=ea286ace-86c7-4d5b-8580-3fbfa46b1c66.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=31505;SECURITY=SSL;SSLServerCertificate=ssl.crt;UID=qxn78437;PWD=whNl99ZgMIttkZ80", '', '')

app = Flask(__name__)
app.secret_key = 'jackiechan'


def rewrite(url):
    view_func, view_args = app.create_url_adapter(request).match(url)
    return app.view_functions[view_func](**view_args)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def root():
    return render_template('login.html')


@app.route('/user/<id>')
# @login_required
def user_info(id):
    with sql.connect('inventorymanagement.db') as con:
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute(f'SELECT * FROM users')
        user = cur.fetchall()
    return render_template("user_info.html", user=user[0])


@app.route('/login', methods=['GET', 'POST'])
def login():
    global userid
    msg = ''

    if request.method == 'POST':
        un = request.form['username']
        pd = request.form['password_1']
        print(un, pd)
        sql = "SELECT * FROM users WHERE username =? AND password=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, un)
        ibm_db.bind_param(stmt, 2, pd)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            session['username'] = account['USERNAME']
            session['email'] = account['EMAIL']
            return redirect('/dashboard')
        else:
            msg = 'Incorrect username / password !'
        return render_template('login.html', msg=msg)
    else:
        return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    mg = ''
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        pw = request.form['password']
        sql = 'SELECT * FROM users WHERE username =?'
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, username)
        ibm_db.execute(stmt)
        acnt = ibm_db.fetch_assoc(stmt)
        if acnt:
            mg = 'Account already exits!!'
            return render_template('signup.html', meg=mg)
        else:
            insert_sql = 'INSERT INTO users (USERNAME,EMAIL,PASSWORD) VALUES (?,?,?)'
            wallet_sql = 'INSERT INTO wallet (user_email) VALUES (?)'

            pstmt = ibm_db.prepare(conn, insert_sql)
            walletStmt = ibm_db.prepare(conn, wallet_sql)

            ibm_db.bind_param(pstmt, 1, username)
            ibm_db.bind_param(pstmt, 2, email)
            ibm_db.bind_param(pstmt, 3, pw)
            ibm_db.execute(pstmt)

            ibm_db.bind_param(walletStmt, 1, email)
            ibm_db.execute(walletStmt)

            session['username'] = username
            session['email'] = email

            return redirect('/dashboard')

    else:
        return render_template("signup.html", meg=mg)


@app.route('/dashboard', methods=['POST', 'GET'])
@login_required
def dashboard():
    sql = "SELECT * FROM expenses WHERE user_email = ? ORDER BY datetime DESC LIMIT 10"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, session['email'])
    ibm_db.execute(stmt)

    expenses = []
    record = ibm_db.fetch_assoc(stmt)

    while record != False:
        expenses.append(record)
        record = ibm_db.fetch_assoc(stmt)
    return render_template('dashboard.html', expenses=expenses)


@app.route('/expense/add', methods=['POST'])
@login_required
def add_expense():
        title = request.form['title']
        description = request.form['description']
        amount = request.form['Amount']
        expenseType = int(request.form['expense-type'])

        if expenseType != 0 and expenseType != 1:
            return "<h1>Invalid input</h1>"
        
        dateTime = datetime.now()

        insert_sql = 'INSERT INTO expenses (user_email, title,description,amount, credit, datetime) VALUES (?, ?,?,?,?, ?)'
        
        if expenseType == 1:
            walletUpdateSql = 'UPDATE wallet SET balance = balance + ? WHERE user_email = ?'
        else:
            walletUpdateSql = 'UPDATE wallet SET balance = balance - ? WHERE user_email = ?'
        
        pstmt = ibm_db.prepare(conn, insert_sql)
        walletStmt = ibm_db.prepare(conn, walletUpdateSql)

        ibm_db.bind_param(pstmt, 1, session['email'])
        ibm_db.bind_param(pstmt, 2, title)
        ibm_db.bind_param(pstmt, 3, description)
        ibm_db.bind_param(pstmt, 4, amount)
        ibm_db.bind_param(pstmt, 5, expenseType == 1)
        ibm_db.bind_param(pstmt, 6, dateTime)
        ibm_db.execute(pstmt)

        ibm_db.bind_param(walletStmt, 1, amount)
        ibm_db.bind_param(walletStmt, 2, session['email'])
        ibm_db.execute(walletStmt)

        return redirect(url_for('dashboard'))


@app.route('/expense/view', methods=['POST', 'GET'])
@login_required
def view_expense():
    return render_template('view-expense.html')


@app.route('/wallet')
def wallet():
    walletSql = "SELECT balance, alert_limit FROM wallet WHERE user_email = ?"

    walletStmt = ibm_db.prepare(conn, walletSql)
    ibm_db.bind_param(walletStmt, 1, session['email'])
    ibm_db.execute(walletStmt)

    wallet = ibm_db.fetch_assoc(walletStmt)

    return render_template('wallet.html', wallet=wallet)
  

@app.route('/wallet/update-limit', methods=["GET", "POST"])
def updateWalletLimit():
#   if request.method == "GET":
#     return render_template("update-wallet.html")

#   limit =  float(request.form['limit'])

#   if limit < 0:
#     return "<h1>Invalid limit</h1>"

#   db.execute("UPDATE wallet SET wallet_limit = :limit WHERE username = :username",
#               {
#                 "limit" : limit,
#                 "username" : session['user']
#               })
#   db.commit()

#   flash('wallet updated succesfully', 'success')
  return redirect("/wallet")

@app.route('/logout')
def logout():
  session.clear()
  return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)

# ALTER TABLE stocks ALTER COLUMN ID SET GENERATED BY DEFAULT AS IDENTITY
