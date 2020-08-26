###############
### Imports ###
###############
from flask import Flask, request, render_template, session, redirect, url_for, abort, flash
import mariadb
import bcrypt
import logging
import sys
from collections import defaultdict

######################
### Main Variables ###
######################
app = Flask(__name__)

main_config = open('/skylabpanel/main.conf', 'r')
lines = main_config.readlines()


logging.basicConfig(filename='example.log',level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%m/%d %H:%M:%S')

###########################
### Database Conection ####
###########################
try:
    conn = mariadb.connect(
        user=lines[0].rstrip("\n"),
        password=lines[1].rstrip("\n"),
        host="localhost",
        port=3306,
    )
except mariadb.Error as e:
    logging.critical(f"Main - Main Conection to Database Failed! {e}")
    sys.exit(1)
except IndexError:
    logging.critical("No Database Conection Creditals Provided in /skylabpanel/main.conf !")
else:
    cur = conn.cursor()
    logging.info("Main - Main Conection to Database Successful!")

#################
### Main Page ###
#################
@app.route('/')
def basepage():
    if 'username' in session:
        return render_template('base.html')
    else:
        return render_template('login.html')

##################
### Login Page ###
##################
@app.route('/login', methods=['GET', 'POST'])
def login():
    db_username = "NO DATA"
    db_password = "NO DATA"
    ## Assign Form Data to Variables ##
    username = request.form['username'] 
    password = request.form['password']
    ## Data Validation & Hashing ##
    username = username.strip("""!"#$%&'()*+,-./[\]^`{|}~@ """) # pylint: disable=anomalous-backslash-in-string
    
    password = password.encode('utf-8')
    ## More Data Validation and Output ##
    if len(username) >= 3: # and len(password) >= 6:
        cur.execute("USE skylabpanel")
        cur.execute("SELECT username, password, account_type FROM tbl_users WHERE username = ? ", (username, ))
        myresult = cur.fetchall()
        for row in myresult:
            db_username = row[0]
            db_password = row[1].encode('utf-8')
            db_account_type = row[2]
        print (username, password)
        print (db_username, db_password)
        if username == db_username and bcrypt.checkpw(password, db_password):
            session['username'] = username
            session['account_type'] = db_account_type
            flash ("You are Logged in!", "info")
            return redirect(url_for('basepage'))
        else:
            return "<p>The data you entered was not valid<p>"
    else:
        return "<p>The data you entered was not valid<p>"

###################
### Logout Page ###
####################
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('basepage'))

######################
### User Managment ###
#######################
@app.route('/client/user-managment/users')
def user_managment():
    cur.execute("USE skylabpanel")
    cur.execute("SELECT id, username, domains, package, account_type FROM tbl_users WHERE account_type != admin")
    myresult = cur.fetchall()
    num_records = len(myresult)
    all_customers = []
    for row in myresult:
        customer = [row[0], row[1], row[2], row[3], row[4]]
        all_customers.append(customer)
        customer = []
    render_template('/client/user-managment/users.html', results=all_customers)

###########
### Run ###
###########
if __name__ == '__main__':
    app.secret_key = "Uxb&2e2e8=DjYtLWBAmb"  
    app.run(use_reloader=True, debug=True, host='0.0.0.0')