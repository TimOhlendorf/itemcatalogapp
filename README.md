
# Project Title

Item-Catalog-App 

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

The project files are available on github. 

git clone https://github.com/ubunturuby/item-catalog-app.git

## Description

The app runs a webserver with the python based flask framework. 
Users can login / logout via facebook or google.
Users who are logged in can create new items and edit or delete items they created. 
Users can add categories. 
Users who are not logged in can visit categories and item descriptions but wont be able to alter the data. 

### Prerequisites

What things you need to install the software and how to install them

python==2.7
certifi==2018.4.16
chardet==3.0.4
Click==7.0
docopt==0.6.2
Flask==1.0.2
idna==2.7
itsdangerous==0.24
Jinja2==2.10
MarkupSafe==1.0
pipreqs==0.4.9
pycodestyle==2.4.0
requests==2.19.1
SQLAlchemy==1.2.12
urllib3==1.23
Werkzeug==0.14.1
yarg==0.1.9


### Installing

If you don't already have Git installed, download Git from git-scm.com. Install the version for your operating system.

On Windows, Git will provide you with a Unix-style terminal and shell (Git Bash). (On Mac or Linux systems you can use the regular terminal program.)

VirtualBox is the software that actually runs the VM. You can download it from virtualbox.org, here. Install the platform package for your operating system. You do not need the extension pack or the SDK. You do not need to launch VirtualBox after installing it.
https://www.virtualbox.org/wiki/Download_Old_Builds_5_1

Vagrant is the software that configures the VM and lets you share files between your host computer and the VM's filesystem. You can download it from vagrantup.com. Install the version for your operating system.
https://www.vagrantup.com/downloads.html

Clone the fullstack-nanodegree-vm
git clone http://github.com/udacity/fullstack-nanodegree-vm

Using the terminal, change directory using the command cd fullstack/vagrant, then type "vagrant up" to launch your virtual machine.

Copy project from github: 
Download the project from github with 
git clone https://github.com/ubunturuby/item-catalog-app.git

Write your Flask application locally in the vagrant/catalog directory (which will automatically be synced to /vagrant/catalog within the VM)

Now that you have Vagrant up and running type vagrant ssh to log into your virtual machine (VM). Change directory to the /vagrant directory by typing cd /vagrant. This will take you to the shared folder between your virtual machine and host machine.

Setup application within the VM (python /vagrant/catalog/):

type in console: python database_setup.py

creates the database with SQLAlchemy 

type in console: python lotsofmenus.py

populates the database with dummy data 

type in console: python application.py 

runs the flask webserver on port http://localhost:8000

Access and test your application by visiting http://localhost:8000 locally

If you have to reset the database (deletes all data from database) 

python deleteall.py

## Authors

* **Tim Ohlendorf** 

