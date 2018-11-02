#!/usr/bin/env python
import random
import string
import httplib2
import json
import requests
import re
from flask import Flask, render_template, request, redirect
from flask import url_for, flash, jsonify
from flask import make_response
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from database_setup import Base, Category, MenuItem, User
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from functools import wraps

template_path = '/var/www/FlaskApp/FlaskApp/templates'
app = Flask(__name__, template_folder=template_path)
#app = Flask(__name__)

#CLIENT_ID = json.loads(
#    open('client_secrets.json', 'r').read())['web']['client_id']
with app.open_resource('client_secrets.json') as f:
    CLIENT_ID = json.load(f)['web']['client_id']
APPLICATION_NAME = "Item-Catalog-App"
AccessError = "access denied"

POSTGRES = {
    'user': 'postgres',
    'pw': 'cookies2018',
    'db': 'itemcatalogappdb',
    'host': 'localhost',
    'port': '5432',
}
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:\
%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES

# Connect to Database and create database session
#engine = create_engine('sqlite:///item-catalog-db.db',
#                       connect_args={'check_same_thread': False})
#engine = create_engine('postgres:///ubuntu:cookies2018/itemcatalogappdb',
#                       connect_args={'check_same_thread': False})
engine = create_engine('postgresql://ubuntu:cookies2018@localhost/itemcatalogappdb')


Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    """ User authentification via facebook login.

        Opens pop-up with user login screen from facebook.
        User enters login data and connects with facebook.
        Facebook redirects user to item-catalog-app.
        Program recieves name, email, id from facebook profile
        and checks database for matching user profile.
        If no user profile is found, a new user is created.
        If user is found, he is logged in and
        can add category, add/edit/delete items, he created.
    """
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print("access token received %s") % access_token
    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = ("https://graph.facebook.com/oauth/access_token?"
           "grant_type=fb_exchange_token&client_id=%s&"
           "client_secret=%s&fb_exchange_token="
           "%s") % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    ''' Due to the formatting for the result from the server token
        exchange we have to
        split the token first on commas and select the first
        index which gives us the key : value
        for the server access token then we split it on colons
        to pull out the actual token value
        and replace the remaining quotes with nothing so that
        it can be used directly in the graph
        api calls'''
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = ("https://graph.facebook.com/v2.8/me?"
           "access_token=%s&fields=name,id,email") % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = ("https://graph.facebook.com/v2.8/me/picture?"
           "access_token=%s&redirect=0&height=200&width=200") % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += (
               ' " style = " \
               "width: 300px; " \
               "height: 300px; " \
               "border-radius: 150px; " \
               " -webkit-border-radius: 150px; " \
               " -moz-border-radius: 150px; " > ')

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = ("https://graph.facebook.com/%s/"
           "permissions?access_token=%s") % (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    del login_session['access_token']
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    print("you have been logged out")
    login_session['email'] = ""
    flash('successfully logged out')
    return redirect(url_for('showCategories'))


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """ User authentification via google login.

        Opens pop-up with user login screen from google.
        User enters login data and connects with google.
        Google redirects user to item-catalog-app.
        Program recieves name, email from google profile
        and checks database for matching user profile.
        If no user profile is found, a new user is created.
        If user is found, he is logged in and
        can add category, add/edit/delete items, he created.
    """

    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(
            json.dumps('Invalid state parameter.'), 401)
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
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = (("https://www.googleapis.com/"
           "oauth2/v1/tokeninfo?access_token=%s")
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
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
                   json.dumps('Current user is already connected.'),
                   200)
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

    # login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['username'] = data['email']
    # See if a user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
        print ("user created")
    login_session['user_id'] = user_id
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += (
        ' " style = " \
        "width: 300px; " \
        "height: 300px ; " \
        "border-radius: 150px; " \
        "-webkit-border-radius: 150px; " \
        "-moz-border-radius: 150px; " > ')

    flash("you are now logged in as %s" % login_session['username'])
    return output
# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
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
    except NoResultFound:
        print "User ID was not found in DB"
        return None


def checkUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return true
    except NoResultFound, e:
        print e
        return false

# DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
        # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's session.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['user_id']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash('successfully logged out')
        return redirect(url_for('showCategories'))

    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
                                 json.dumps(
                                            'Failed to revoke'
                                            'token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return redirect(url_for('showCategories'))


# check which 3-party-provider is to logout


@app.route('/disconnect')
def disconnect():
        try:
            if(login_session['facebook_id'] is not None):
                return redirect(url_for('fbdisconnect'))
            if(login_session['gplus_id'] is not None):
                return redirect(url_for('gdisconnect'))
            else:
                return redirect(url_for('showCategories'))
        except NoLoginFound, e:
                print "user login could not be verified, logout failed."
                return redirect(url_for('showCategories'))


# Decorator checks for login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in login_session:
            return f(*args, **kwargs)
        else:
            flash('You are not allowed to access there')
            return redirect('/login')
    return decorated_function


# Show all categories


@app.route('/')
def showCategories():
    """Shows all categorys and all items from catalog.

       All categories and items are loaded from the database.
       The display of the view depends on the login-status of the user.
       If the user is logged in he will be able to add items / categories.
    """
    categories = session.query(Category).order_by(asc(Category.name))
    items = session.query(MenuItem).order_by(MenuItem.id.desc())
    try:
        user_id = getUserID(login_session['email'])
        if (user_id is not None):
            return render_template('categories.html', categories=categories,
                                   items=items)
        else:
            return render_template('publiccategories.html',
                                   categories=categories,
                                   items=items)
    except:
        print ("showCategories exception!")
        return render_template('publiccategories.html',
                               categories=categories, items=items)


# Add new category

@app.route('/category/new/', methods=['GET', 'POST'])
@login_required
def newCategory():
    if request.method == 'POST':
        newCategory = Category(
                               name=re.sub("[^A-Za-z0-9,.;]", "",
                                           request.form['name']),
                               user_id=login_session['user_id'])
        session.add(newCategory)
        flash('New Category %s Successfully Created' % newCategory.name)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        return render_template('newCategory.html')


# Show all items of specific category

@app.route('/catalog/<string:category_name>/items')
def showCategory(category_name):
    category = session.query(Category).filter_by(
                                                 name=category_name
                                                 ).one_or_none()
    if category is None:
        flash('Category does not exist')
        return redirect('/')
    items = session.query(MenuItem).filter_by(category_id=category.id).all()
    creator = getUserInfo(category.user_id)
    categories = session.query(Category).order_by(asc(Category.name))
    if 'username' in login_session:
        if (login_session['user_id'] is not None):
            return render_template('selectedcategory.html',
                                   categories=categories,
                                   category=category, items=items)
        else:
            return render_template('publicselectedcategory.html',
                                   categories=categories,
                                   category=category, items=items)
    else:
        return render_template('publicselectedcategory.html',
                               categories=categories,
                               category=category, items=items)


# Add new item to catalog

@app.route('/category/additem', methods=['GET', 'POST'])
@login_required
def addItem():
    """ Creates new item.

        Checks is user is authorized to create items.
        Removes special characters from name, description
        before commiting them to the database.
    """
    allcategories = session.query(Category).all()
    creator = getUserInfo(login_session['user_id'])
    if (login_session['user_id'] is not None):
        if request.method == 'POST':
            newItem = MenuItem(name=re.sub("[^A-Za-z0-9,.;]", "",
                                           request.form['name']),
                               description=re.sub("[^A-Za-z0-9,.;]", "",
                                                  request.form['description']),
                               category_id=request.form['category_id'],
                               user_id=login_session['user_id'])
            session.add(newItem)
            session.commit()
            flash('New Item %s Successfully Created' % (newItem.name))
            return redirect(url_for('showCategories'))
        else:
            return render_template('addItem.html', allcategories=allcategories)
    else:
        return render_template('showCategories')


# Show specific Item of a category

@app.route('/catalog/<string:category_name>/<string:item_name>/',
           methods=['GET', 'POST'])
def showItem(category_name, item_name):
    category = session.query(Category).filter_by(
                                                 name=category_name
                                                 ).one_or_none()
    if category is None:
        flash('Category does not exist')
        return redirect('/')
    showItem = session.query(MenuItem).filter_by(name=item_name,
                                                 category=category
                                                 ).one_or_none()
    if showItem is None:
        flash('Item does not exist')
        return redirect('/')
    else:
        if 'username' in login_session:
            if (login_session['user_id'] == showItem.user_id):
                return render_template('showitem.html', item=showItem)
            else:
                return render_template('publicshowitem.html', item=showItem)
        else:
                return render_template('publicshowitem.html', item=showItem)


# Edit specific item

@app.route('/catalog/<string:item_name>/edit', methods=['GET', 'POST'])
@login_required
def editItem(item_name):
    """ Edit specific item.

        Function checks if user is authorized to edit item.
        If user is authorized changes are commited to database.
        Special characters are removed before commitment.
    """
    showItem = session.query(MenuItem).filter_by(name=item_name).one_or_none()
    if showItem is None:
        flash('Item does not exist')
        return redirect('/')
    else:
        allcategories = session.query(Category).all()
        if (login_session['user_id'] == showItem.user_id):
            if request.method == 'POST':
                if request.form['name']:
                    showItem.name = re.sub("[^A-Za-z0-9,.;]", "",
                                           request.form['name'])
                if request.form['description']:
                    showItem.description = re.sub("[^A-Za-z0-9,.;]", "",
                                                  request.form['description'])
                if request.form['category_id']:
                        showItem.category_id = request.form['category_id']
                showItem.user_id = showItem.user_id
                session.add(showItem)
                session.commit()
                flash('Menu Item Successfully Edited')
                return redirect(url_for('showItem',
                                category_name=showItem.category.name,
                                item_name=showItem.name))
            else:
                return render_template('edititem.html',
                                       item=showItem,
                                       allcategories=allcategories)
        else:
            return render_template('showitem.html', item=showItem)


# Delete specific item

@app.route('/catalog/<string:item_name>/delete', methods=['GET', 'POST'])
@login_required
def deleteItem(item_name):
    """ Delete specific item.

        Function checks if user is authorized to delete item.
        If user is authorized changes are commited to database.
    """
    showItem = session.query(MenuItem).filter_by(name=item_name).one_or_none()
    if showItem is None:
        flash('Item does not exist')
        return redirect('/')
    else:
        if (login_session['user_id'] == showItem.user_id):
            if request.method == 'POST' and request.form['button'] == "delete":
                session.delete(showItem)
                session.commit()
                flash('Menu Item Successfully Deleted')
                return redirect(url_for('showCategories'))
            if request.method == 'POST' and request.form['button'] == "cancel":
                return redirect(url_for('showCategories'))
            else:
                return render_template('deleteitem.html', item=showItem)
        else:
                return render_template('publicshowitem.html',
                                       category_name=showItem.category.name,
                                       item_name=showItem.name)


# Helper function to merge two dictionaries
def merge_two_dicts(x, y):
    """Given two dicts, merge them into a new dict as a shallow copy."""
    z = x.copy()
    z.update(y)
    return z


# JSON endpoint whole item catalog
@app.route('/catalog/items/JSON')
def itemsJSON():
    items = session.query(MenuItem).all()
    return jsonify(items=[i.serialize for i in items])


# JSON endpoint all items in category
@app.route('/catalog/<string:category_name>/JSON')
def itemsInCategoryJSON(category_name):
    category = session.query(Category).filter_by(
                                                 name=category_name
                                                 ).one_or_none()
    if category is None:
        flash('Category does not exist')
        return redirect('/')
    else:
        items = session.query(MenuItem).filter_by(
                                                  category_id=category.id
                                                  ).all()
        return jsonify(items=[i.serialize for i in items])


# JSON endpoint serves single item in single category
@app.route('/catalog/<string:category_name>/<string:item_name>/JSON')
def specificItemInCategoryJSON(category_name, item_name):
    category = session.query(Category).filter_by(
                                                 name=category_name
                                                 ).one_or_none()
    if category is None:
        flash('Category does not exist')
        return redirect('/')
    item = session.query(MenuItem).filter_by(category_id=category.id,
                                             name=item_name).one_or_none()
    if item is None:
        flash('Item does not exist')
        return redirect('/')
    else:
        return jsonify(item=[item.serialize])


if __name__ == '__main__':
#    app.secret_key = 'super_secret_key'
#    app.debug = True
#    app.run(host='0.0.0.0', port=8000)
	app.run()
