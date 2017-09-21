#! /usr/bin/env python

from flask import Flask, render_template, request, redirect, jsonify
from flask import url_for, flash, make_response
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Category, Base, Item, User
from flask import session as login_session

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
import random
import string


app = Flask(__name__)


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Web Catalog Application"


# Connect to Database and create database session
engine = create_engine('sqlite:///category_item_withuser.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/login')
def showLogin():
    """Create anti-forgery state token"""
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """Login via google."""
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 402)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
                        json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output1 = ''
    output1 += '<h1>Welcome, '
    output1 += login_session['username']
    output1 += '!</h1>'
    output1 += '<img src="'
    output1 += login_session['picture']
    output1 += ' " style = "width: 300px; height: 300px;'
    output1 += 'border-radius: 150px;'
    output1 += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output1


@app.route('/gdisconnect')
def gdisconnect():
    """Logout from google."""
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(
                        json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # print 'In gdisconnect access token is %s', access_token
    # print 'User name is: '
    # print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token={}'.format(
                                                login_session['access_token'])
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    # print 'result is '
    # print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        return render_template('logout.html')
    else:
        response = make_response(
                    json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# User Helper Functions
def createUser(login_session):
    if not login_session['username']:  # check username is not empty
        username = login_session['email'].split("@")[0]
    else:
        username = login_session['username']

    newUser = User(name=username, email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Utility functions
def getCatalogNameByID(category_id):
    """getCatalogNameByID takes a category_id as a parameter.
        Executes the query and returns the name of the category.
        args:
            category_id - an id of category.
        returns:
            the name of the category.
    """
    new_categorie = session.query(Category).filter_by(id=category_id).one()
    return new_categorie.name


def isLogin():
    """isLogin return boolean to describe current status of login session.
        returns:
            True: the user is logined.
            False: the user is logouted.
    """
    if 'username' not in login_session:
        print "is NOT Login!!!"
        return False
    else:
        print "is Login!!!"
        return True


# Web page handlers
@app.route('/catalog.json')
def restaurantsJSON():
    """ JSON APIs to view Catalog Information"""
    list = []
    categories = session.query(Category).all()
    for category in categories:
        items = session.query(Item).filter_by(category_id=category.id).all()
        dict = category.serialize
        dict['Item'] = [r.serialize for r in items]
        list.append(dict)
    return jsonify(categories=list)


@app.route('/')
def showCategories():
    """Show all categories and latest items"""
    categories = session.query(Category).order_by(asc(Category.name))
    items = session.query(Item).order_by(desc(Item.id))
    if 'username' not in login_session:
        return render_template(
                'public_categories.html', categories=categories,
                items=items, is_login=isLogin())
    else:
        return render_template(
                'categories.html', categories=categories,
                items=items, is_login=isLogin())


@app.route('/catalog/<catalog_name>/items')
def showItems(catalog_name):
    """Shows all the items available for this category."""
    categories = session.query(Category).order_by(asc(Category.name))
    cur_category = session.query(Category).filter_by(name=catalog_name).one()
    items = session.query(Item).filter_by(category_id=cur_category.id)
    return render_template(
                'items.html',
                categories=categories, items=items,
                catalog_name=catalog_name, is_login=isLogin())


@app.route('/catalog/<catalog_name>/<int:item_id>/<item_name>')
def showItemInfo(catalog_name, item_name, item_id):
    """Show specific information of this item."""
    item = session.query(Item).filter_by(id=item_id).one()
    creator = getUserInfo(item.user_id)
    if 'username' not in login_session or creator.id != login_session[
                                                                    'user_id']:
        return render_template(
                'public_iteminfo.html',
                catalog_name=catalog_name, item_name=item.name,
                info=item.description, item_id=item_id, is_login=isLogin())
    else:
        return render_template(
                'iteminfo.html',
                catalog_name=catalog_name, item_name=item.name,
                info=item.description, item_id=item_id, is_login=isLogin())


@app.route('/catalog/new', methods=['GET', 'POST'])
def newItem():
    """Create a new item"""
    if 'username' not in login_session:
        return redirect('/login')
    categories = session.query(Category).order_by(asc(Category.name))
    if request.method == 'POST':
        newItem = Item(
            name=request.form['name'], description=request.form['description'],
            category_id=request.form['categories'],
            user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        catalog_name = getCatalogNameByID(newItem.category_id)
        flash('New Menu %s Item Successfully Created' % (newItem.name))
        return redirect(url_for('showItems', catalog_name=catalog_name))
    else:
        return render_template(
                    'newitem.html', categories=categories, is_login=isLogin())


@app.route(
    '/catalog/<catalog_name>/<int:item_id>/<item_name>/edit',
    methods=['GET', 'POST'])
def editItem(catalog_name, item_name, item_id):
    """Edit information of item."""
    if 'username' not in login_session:
        return redirect('/login')
    categories = session.query(Category).order_by(asc(Category.name))
    editedItem = session.query(Item).filter_by(id=item_id).one()

    alert = ""
    alert += "<script>function myFunction() {alert('You are not authorized to"
    alert += " edit this item. Please add your own item in order to edit it."
    alert += "');}</script><body onload='myFunction()''>"
    if login_session['user_id'] != editedItem.user_id:
        return alert

    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['categories']:
            editedItem.category_id = request.form['categories']
            catalog_name = getCatalogNameByID(editedItem.category_id)
        session.add(editedItem)
        session.commit()
        flash('Item Successfully Edited')
        return redirect(url_for(
                'showItemInfo',
                catalog_name=catalog_name,
                item_name=editedItem.name, item_id=editedItem.id))
    else:
        return render_template(
            'edititem.html', item=editedItem, categories=categories,
            is_login=isLogin())


@app.route(
    '/catalog/<catalog_name>/<int:item_id>/<item_name>/delete',
    methods=['GET', 'POST'])
def deleteItem(catalog_name, item_id, item_name):
    """Delete a item"""
    if 'username' not in login_session:
        return redirect('/login')
    itemToDelete = session.query(Item).filter_by(id=item_id).one()
    alert = ""
    alert += "<script>function myFunction() {alert('You are not authorized to"
    alert += " delete this item. Please create your own item."
    alert += "');}</script><body onload='myFunction()''>"
    if login_session['user_id'] != itemToDelete.user_id:
        return alert
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Menu Item Successfully Deleted')
        return redirect(url_for('showItems', catalog_name=catalog_name))
    else:
        return render_template(
                    'deleteitem.html', item=itemToDelete, is_login=isLogin())


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
