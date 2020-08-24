from flask import Flask, request, render_template, session, redirect, url_for, abort, flash
import mysql.connector
app = Flask(__name__)

mian_config = open('/skylabpanel/main.conf')
lines = mian_config.readlines()
mydb = mysql.connector.connect(
  host="localhost",
  auth_plugin="mysql_native_password",
  user=lines[0],
  password=lines[1],
  database="skylabpanel"
)
mycursor = mydb.cursor()
@app.route('/')
def basepage():
    if 'username' in session:
        return render_template('base.html')
    else:
        flash("You Need to Login!", "info")
        return render_template('login.html')

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
    if len(username) >= 3 and len(password) >= 6:
        sql = "SELECT UserName, Password FROM tbl_users WHERE UserName = %s"
        val = (username, )
        mycursor.execute(sql, val)
        myresult = mycursor.fetchall()
        for row in myresult:
            db_username = row[0]
            db_password = row[1].encode('utf-8')
        print (username, password)
        print (db_username, db_password)
        if username == db_username and bcrypt.checkpw(password, db_password):
            session['username'] = username
            return redirect(url_for('home'))
        else:
            return render_template('account/login.html', notifications_type="info", message="Hello World")
    else:
        return "<p>The data you entered was not valid<p>"
if __name__ == '__main__':
    app.secret_key = "Uxb&2e2e8=DjYtLWBAmb"  
    app.run(use_reloader=True, debug=True, host='0.0.0.0')