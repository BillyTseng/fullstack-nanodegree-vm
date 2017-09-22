# Web Catalog Application
This project presented a Python script uses Flask to build a web catalog website. This website provided functions to create, read, update, and delete to query a SQLite database, and it has integrated with Google sign-in to distinguish the different users with different permission to edit/delete items. Also, this project implemented JSON API endpoints to help users to obtain the structured data of full catalog or an arbitrary item in the catalog.

## Install Virtual Machine
  1. Download and install VirtualBox [here](https://www.virtualbox.org/wiki/Downloads).
  2. Download and install Vagrant [here](https://www.vagrantup.com/downloads.html).

## Run The Virtual Machine
  1. Go to [here](https://github.com/BillyTseng/fullstack-nanodegree-vm). Download and unzip this project into the working directory.
  2. Use a unix-style terminal to type command `vagrant up` in the project directory to turn on the virtual machine. It will take a while when the first booting.
  3. Once the virtual machine is done booting, type command `vagrant ssh` on the terminal to log in the virtual machine.
  4. When you want to log out, type `exit` at the shell prompt. To turn the virtual machine off (without deleting anything), type `vagrant halt`. If you do this, you'll need to run `vagrant up` again before you can log into it.

## Create Google Client ID & Secret
  1. Go to https://console.developers.google.com/apis to create and get the client ID and client secret.
  2. Download your credential JSON file and replace the old `/vagrant/catalog/client_secrets.json`.
  3. Go to line 19 of `/vagrant/catalog/templates/header.html`  
  and line 14 of `/vagrant/catalog/templates/login.html` to replace YOURID with the Google client ID.

## Execute the website backend
  1. After type command `vagrant ssh`, you can type `cd /vagrant/catalog` to navigate to the project directory in the virtual machine.
  2. Type `./application.py` at the shell prompt.

## Browse Web Catalog Application
On the web browser Chrome, navigate to `http://localhost:8000/`, it will render the application page on the browser tab.

## JSON API Endpoints
  1. Type `http://localhost:8000/catalog/JSON` to view full catalog information.
  2. Type `http://localhost:8000/catalog/<int:item_id>/JSON` to view an item information.  
     For example, `http://localhost:8000/catalog/12/JSON` will show the data as below:  
     ```
     {
       "item": {
         "description": "Stephen Vincent Strange",
         "id": 12,
         "name": "Dr. Strange"
       }
     }
     ```
