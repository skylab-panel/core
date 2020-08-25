echo "SkyLab Panel is going to install some basics. It will then start install.py"
apt-get update
apt-get install python3
apt-get install python3-pip
pip3 install flask
pip3 install bcrypt
pip3 install mysql.connector
python3 install.py