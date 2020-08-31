###############
### Imports ###
###############
from flask import Flask, request, render_template, session, redirect, url_for, abort, flash
import mariadb
import bcrypt
import logging
import sys
from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired
import functools
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
def home_page():
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
            return redirect(url_for('home_page'))
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
    return redirect(url_for('home_page'))

######################
### User Managment ###
#######################
@app.route('/client/user-management/users')
def user_managment():
    cur.execute("USE skylabpanel")
    cur.execute("SELECT user_id, username, firstname, lastname, email, account_type FROM tbl_users WHERE account_type != ?", ('admin', ))
    myresult = cur.fetchall()
    num_records = len(myresult)
    all_customers = []
    for row in myresult:
        customer = [row[0], row[1], row[2], row[3], row[4], row[5]]
        all_customers.append(customer)
        customer = []
    return render_template('/client/user-management/users.html', results=all_customers, num_records=num_records)

@app.route('/client/user-management/add-user')
def user_managment_add_user():
    return render_template('/client/user-management/user-add.html')
@app.route('/client/user-management/edit-user')
def user_managment_edit_user():
    return render_template('/client/user-management/user-edit.html')

@app.route('/client/user-management/remove-user', methods=('GET', 'POST'))
def user_managment_remove_user():
    class myform(FlaskForm):
        cur.execute("USE skylabpanel")
        cur.execute("SELECT username FROM tbl_users WHERE account_type != ?", ('admin', ))
        myresult = cur.fetchall()
        myresult = functools.reduce(lambda x,y: x+y, myresult)
        users = SelectField('User Name', choices=myresult, validators=[DataRequired()], default='cpp')
        submit = SubmitField('Submit')
    form = myform()
    if form.is_submitted():
        cur.execute("DELETE FROM tbl_users WHERE username = ?", (form.users.data, ))
        flash('User: ' + form.users.data + ' Removed', 'info')
        return redirect(url_for('user_managment'))
    return render_template('/client/user-management/remove-user.html', form=form) 

######################
### package Managment ###
#######################
@app.route('/client/package-management/packages')
def package_managment():
    cur.execute("USE skylabpanel")
    cur.execute("SELECT * FROM tbl_packages")
    myresult = cur.fetchall()
    num_records = len(myresult)
    all_packages = []
    for row in myresult:
        package = [row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]]
        all_packages.append(package)
        package = []
    return render_template('/client/package-management/packages.html', results=all_packages, num_records=num_records)

@app.route('/client/package-management/add-package',  methods=('GET', 'POST'))
def package_managment_add_package():
    class add_package_form(FlaskForm):
        package_name = StringField('Package Name', validators=[DataRequired()])
        package_cost = DecimalField('Package Price', validators=[DataRequired()]) 
        max_domains = IntegerField('Max Number of Domains')
        max_sub_domains = IntegerField('Max Number of Sub Domains')
        max_storage = IntegerField('Max Ammout of Storage ')
        max_ftp_accounts = IntegerField('Max Number of FTP Accounts ')
        max_databases = IntegerField('Max Number of Databases ')
        max_email_accounts = IntegerField('Max Number of Email Accounts')
        submit = SubmitField('Submit')

    form = add_package_form()
    if form.is_submitted():
        cur.execute("USE skylabpanel")
        cur.execute("""INSERT INTO tbl_packages(
            package_name, 
            package_cost, 
            max_domains, 
            max_sub_domains, 
            max_storage, 
            max_ftp_accounts, 
            max_databases,
            max_email_accounts)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (form.package_name.data, 
            form.package_cost.data, 
            form.max_domains.data, 
            form.max_sub_domains.data, 
            form.max_storage.data, 
            form.max_ftp_accounts.data, 
            form.max_databases.data, 
            form.max_email_accounts.data))
        flash('Package: ' + form.package_name.data + ' Added', 'info')
        return redirect(url_for('package_managment'))
    return render_template('/client/package-management/add-package.html', form=form)
@app.route('/client/package-management/edit-package', methods=('GET', 'POST'))
def package_managment_edit_package():
    class edit_package_form_p1(FlaskForm):
        cur.execute("USE skylabpanel")
        cur.execute("SELECT package_name FROM tbl_packages")
        myresult = cur.fetchall()
        myresult = functools.reduce(lambda x,y: x+y, myresult)
        package_name = SelectField(u'Select Package', choices=myresult, validators=[DataRequired()])
        submit = SubmitField('Submit')
    form = edit_package_form_p1()
    if form.is_submitted():
        package_managment_edit_package.package_name = form.package_name.data
        return redirect(url_for('package_managment_edit_package_1'))
    return render_template('/client/package-management/edit-package.html', form=form)

@app.route('/client/package-management/edit-package-1', methods=('GET', 'POST'))
def package_managment_edit_package_1():
    cur.execute("USE skylabpanel")
    cur.execute("SELECT package_cost, max_domains, max_sub_domains, max_storage, max_ftp_accounts, max_databases, max_email_accounts FROM tbl_packages WHERE package_name = ?", ( package_managment_edit_package.package_name , ))
    myresult = cur.fetchall()
    myresult = functools.reduce(lambda x,y: x+y, myresult)    
    class edit_package_form_p2(FlaskForm):
            package_cost = DecimalField('Package Price', validators=[DataRequired()], default=myresult[0]) 
            max_domains = IntegerField('Max Number of Domains', default=myresult[1])
            max_sub_domains = IntegerField('Max Number of Sub Domains', default=myresult[2])
            max_storage = IntegerField('Max Ammout of Storage ', default=myresult[3])
            max_ftp_accounts = IntegerField('Max Number of FTP Accounts ', default=myresult[4])
            max_databases = IntegerField('Max Number of Databases ', default=myresult[5])
            max_email_accounts = IntegerField('Max Number of Email Accounts', default=myresult[6])
            submit = SubmitField('Submit')
    form = edit_package_form_p2()
    if form.is_submitted():
        cur.execute("UPDATE tbl_packages SET package_cost = ?, max_domains = ?, max_sub_domains = ?, max_storage = ?, max_ftp_accounts = ?, max_databases = ?, max_email_accounts = ? WHERE package_name = ?", (form.package_cost.data, form.max_domains.data, form.max_sub_domains.data, form.max_storage.data, form.max_ftp_accounts.data, form.max_databases.data, form.max_email_accounts.data, package_managment_edit_package.package_name))
        flash('Package: ' + package_managment_edit_package.package_name + ' Updated', 'info')
        return redirect(url_for('package_managment'))
    return render_template('/client/package-management/edit-package-1.html', form=form)

@app.route('/client/package-management/remove-package', methods=('GET', 'POST'))
def package_managment_remove_package():
    class remove_package_form(FlaskForm):
        cur.execute("USE skylabpanel")
        cur.execute("SELECT package_name FROM tbl_packages")
        myresult = cur.fetchall()
        myresult = functools.reduce(lambda x,y: x+y, myresult)
        packages = SelectField(u'Select Package', choices=myresult, validators=[DataRequired()], default='cpp')
        submit = SubmitField('Submit')
    form = remove_package_form()
    if form.is_submitted():
        cur.execute("DELETE FROM tbl_packages WHERE package_name = ?", (form.packages.data, ))
        flash('Package: ' + form.packages.data + ' Removed', 'info')
        return redirect(url_for('package_managment'))
    return render_template('/client/package-management/remove-package.html', form=form) 

##########################
### Database Managment ###
##########################
@app.route('/client/database-management/databases')
def database_management():
    cur.execute("USE skylabpanel")
    cur.execute("SELECT Db, Host, User from mysql.db WHERE Db NOT IN (?, ?)", ('phpmyadmin', 'skylabpanel'))
    myresult = cur.fetchall()
    num_records = len(myresult)
    all_databases = []
    for row in myresult:
        database = [row[0].decode("utf-8"), row[1].decode("utf-8"), row[2].decode("utf-8")]
        all_databases.append(database)
        database = []
    return render_template('/client/database-management/databases.html', results=all_databases, num_records=num_records)

@app.route('/client/database-management/add-database' , methods=('GET', 'POST'))
def database_management_add_database():
    class add_database_form(FlaskForm):
        db_name = StringField('Database Name')
        submit = SubmitField('Submit')
    form = add_database_form()
    if form.is_submitted():
        db_name = session['username'] + "_"+ form.db_name.data
        print(db_name)
        cur.execute("CREATE DATABASE IF NOT EXISTS " + db_name)
        cur.execute("USE " + db_name)
        cur.execute("GRANT ALL PRIVILEGES ON * TO " + session['username'] +"@'localhost' WITH GRANT OPTION;")
        flash('Database: ' + db_name + ' Added', 'info')
        return redirect(url_for('database_management'))
    return render_template('/client/database-management/add-database.html', form=form)
###########
### Run ###
###########
if __name__ == '__main__':
    app.secret_key = "Uxb&2e2e8=DjYtLWBAmb"  
    app.run(use_reloader=True, debug=True, host='0.0.0.0')