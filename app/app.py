from flask import Flask, render_template, redirect, request, session, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://gibsqbxqelvght:bd2af40fd3a7372a4da33e7090e7606349d24f661df710450123851701b84fe8@ec2-44-209-186-51.compute-1.amazonaws.com:5432/dcrlivg5r4ajd1'
app.config['SECRET_KEY'] = 'mysecret'

engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
db = scoped_session(sessionmaker(bind = engine))


@app.route('/')
def index():
  return render_template('index.html')


@app.route('/login')
def login():
  session['user'] = 'mathan'
  return render_template('login.html')

@app.route('/register')
def register():
  return render_template('register.html')

@app.route('/wallet')
def wallet():
  wallet = db.execute("SELECT balance, wallet_limit FROM wallet WHERE username = :username",
              {
                "username": session['user']
              }).fetchone()

  return render_template('wallet.html', wallet=wallet)
  

@app.route('/wallet/update-limit', methods=["GET", "POST"])
def updateWalletLimit():
  if request.method == "GET":
    return render_template("update-wallet.html")

  limit =  float(request.form['limit'])

  if limit < 0:
    return "<h1>Invalid limit</h1>"

  db.execute("UPDATE wallet SET wallet_limit = :limit WHERE username = :username",
              {
                "limit" : limit,
                "username" : session['user']
              })
  db.commit()

  flash('wallet updated succesfully', 'success')
  return redirect("/wallet")

@app.route('/logout')
def logout():
  session.clear()
  return redirect('/')