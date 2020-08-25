import mysql.connector
import subprocess
import time
import os, sys
import bcrypt


# This script must be run as root!
if not os.geteuid()==0:
    sys.exit('This script must be run as root!')


print ("""
  _____  _            _             _       _____                     _ 
 / ____|| |          | |           | |     |  __ \                   | |
| (___  | | __ _   _ | |      __ _ | |__   | |__) |__ _  _ __    ___ | |
 \___ \ | |/ /| | | || |     / _` || '_ \  |  ___// _` || '_ \  / _ \| |
 ____) ||   < | |_| || |____| (_| || |_) | | |   | (_| || | | ||  __/| |
|_____/ |_|\_\ \__, ||______|\__,_||_.__/  |_|    \__,_||_| |_| \___||_|
                __/ |                                                   
               |___/                                                    
                
""")
print ("SkyLab Panel Requires some packages to run. Its going to install then now!")
time.sleep(5)
# Update and Upgrade #
print ("Updating Your System")
subprocess.run(['bash','-c', 'apt-get update -y & apt-get upgrade -y'])

# Install Lamp #
print ("Installing Lamp")
subprocess.run(['bash','-c', 'sudo apt-get install apache2 mysql-server php libapache2-mod-php php-mysql -y'])

# Install Php my Admin, Email Dns and others #
print ("Installing Php my Admin, Email Dns and others #")
subprocess.run(['bash','-c', 'sudo apt-get install phpmyadmin letsencrypt -y'])

# Config File #
subprocess.run(['bash','-c', 'cd / & mkdir skylabpanel'])
main_config = open("/skylabpanel/main.txt", "w")
mysql_config = open("/etc/mysql/my.cnf", "a")
mysql_config.write("[mysqld]\n")
mysql_config.write("default_authentication_plugin=mysql_native_password")
# Create skylabpanel Database #
print ("\nSkyLab Panel needs to set its configration file. Follow on Screen Instructions! \n")
time.sleep(2)
mysqlrootusername = input("Enter MySQL Root Username: ")
mysqlrootpassword = input("Enter MySQL Root Password: ")
mydb = mysql.connector.connect(
    host="localhost",
    user=mysqlrootusername,
    password=mysqlrootpassword,
)
mycursor = mydb.cursor()


mycursor.execute("CREATE DATABASE skylabpanel")

# Conect to Database and add User #
mydb = mysql.connector.connect(
    host="localhost",
    user=mysqlrootusername,
    password=mysqlrootpassword,
    database="skylabpanel"
)
mycursor.execute("""CREATE TABLE tbl_users (
    id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    firstname VARCHAR(30) NOT NULL,
    lastname VARCHAR(30) NOT NULL,
    username VARCHAR(30) NOT NULL,
    password VARCHAR(100) NOT NULL,
    email VARCHAR(50),
    reg_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP)
""")

print("The Following Infomation Will be Used for Logging into SkyLab Panel(Username and Password are Case Sestive!)")
firstname = input("Please Enter your Firstname: ")
lastname = input("Please enter your Lastname: ")
username = input("Please Enter a Username(admin and root are not recommended!): ")
password = input("Please Enter a Password: ")
email = input("Please Enter an Email Adress: ")

main_config.write(username+"\n")
main_config.write(password+"\n")

password = password.encode('utf-8')
password = bcrypt.hashpw(password, bcrypt.gensalt())
email = email.strip("""!"#$%&'()*+,_/[\]^`{|}~ """) # pylint: disable=anomalous-backslash-in-string
email = email.lower()

sql = "INSERT INTO tbl_users (firstname, lastname, username, password, email) VALUES (%s, %s, %s, %s, %s)"
val = (firstname, lastname, username, password, email)
mycursor.execute(sql, val)

mycursor.execute("CREATE USER " + username + " @'localhost' IDENTIFIED BY " + password)
mydb.commit()