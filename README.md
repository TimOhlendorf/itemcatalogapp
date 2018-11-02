
# Project Title

Item-Catalog-App 

## Getting Started

The project is an Item-Catalog-App with Flask-Framework and a Postgres-DB, which runs on an Apache Webserver via WSGI.
At the moment the authentification via 3rd-Party-Provider Facebook and Google are not working, because of the requirement of HTTPS, which is mandatory.  

The project files are available on github. 

git clone https://github.com/ubunturuby/itemcatalogapp.git


## Server

IP  == 18.196.125.229 

URL == http://18.196.125.229


## Description

The app runs a webserver with the python based flask framework. 
Users can login / logout via facebook or google.
Users who are logged in can create new items and edit or delete items they created. 
Users can add categories. 
Users who are not logged in can visit categories and item descriptions but wont be able to alter the data. 

### Prerequisites

What things you need to install the software and how to install them


GlobalEnvironment
blinker      1.3
Click        7.0
cryptography 1.2.3
enum34       1.1.2
Flask        1.0.2
idna         2.0
ipaddress    1.0.16
itsdangerous 1.1.0
Jinja2       2.10
MarkupSafe   1.0
pip          18.1
pyasn1       0.1.9
pyinotify    0.9.6
pyOpenSSL    0.15.1
setuptools   20.7.0
six          1.10.0
virtualenv   16.0.0
Werkzeug     0.14.1
wheel        0.29.0


VirtualEnvironment (venv folder) 
certifi        2018.10.15
chardet        3.0.4
Click          7.0
Flask          1.0.2
httplib2       0.11.3
idna           2.7
itsdangerous   1.1.0
Jinja2         2.10
MarkupSafe     1.0
oauth2client   4.1.3
pip            18.1
psycopg2       2.7.5
pyasn1         0.4.4
pyasn1-modules 0.2.2
requests       2.20.0
rsa            4.0
setuptools     40.5.0
six            1.11.0
SQLAlchemy     1.2.12
urllib3        1.24
virtualenv     16.0.0
Werkzeug       0.14.1
wheel          0.32.2


### Important commands
#### restart apache2 webserver 
sudo service apache2 restart
#### error Log on webserver 
sudo nano /var/log/apache2/error.log
#### activate virtualenvironment
source venv/bin/activate

#### restart posgresql
sudo /etc/init.d/postgresql restart
#### activate virtualenvironment 
source venv/bin/activate


### Installing

If you don't already have Git installed, download Git from git-scm.com. Install the version for your operating system.

On Windows, Git will provide you with a Unix-style terminal and shell (Git Bash). (On Mac or Linux systems you can use the regular terminal program.)

Copy project from github: 
Download the project from github with https://github.com/ubunturuby/itemcatalogapp.git

Copy Files in /var/www/FlaskApp/FlaskApp

Folder structure should look like this: 
FlaskApp
    FlaskApp
        static
        templates
        venv 
        __init__.py
    flaskapp.wsgi

type in console: python database_setup.py

creates the database with SQLAlchemy 

type in console: python lotsofmenus.py

populates the database with dummy data 

type in console: python __init__.py

runs the flask webserver on port 80 

If you have to reset the database (deletes all data from database) 

python deleteall.py

## Authors

* **Tim Ohlendorf** 

