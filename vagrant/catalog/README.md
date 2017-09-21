# Web Catalog Application
This project provided a Python script uses Flask to build a web catalog website. This website implemented CRUD functions to query a SQLite database, and it has integrated with Google sign-in to distinguish the different users with different permission to edit/delete items.

## Install Virtual Machine
  1. Download and install VirtualBox [here](https://www.virtualbox.org/wiki/Downloads).
  2. Download and install Vagrant [here](https://www.vagrantup.com/downloads.html).

## Run The Virtual Machine
  1. Download and unzip this project into the working directory.
  2. Use a terminal to type command `vagrant up` in the project directory to turn on the virtual machine. It will take a while when the first booting.
  3. Once the virtual machine is done booting, type command `vagrant ssh` on the terminal to log in the virtual machine.
  4. When you want to log out, type `exit` at the shell prompt. To turn the virtual machine off (without deleting anything), type `vagrant halt`. If you do this, you'll need to run `vagrant up` again before you can log into it.

## Execute the website backend
  1. After type command `vagrant ssh`, you can type `cd /vagrant/catalog` to navigate to the project directory in the virtual machine.
  2. Type `./application.py` at the shell prompt.

## Browse Web Catalog Application
On the web browser Chrome, navigate to `http://localhost:8000/`, it will render the application page on the browser tab.
