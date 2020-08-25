echo "SkyLab Panel is going to install some basics. It will then start install.py"
apt-get update -y
apt-get install python3 -y
apt-get install python3-pip -y
pip3 install flask
pip3 install bcrypt
pip3 install mysql.connector
python3 install.py