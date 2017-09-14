#! /usr/bin/env python

from flask import Flask, render_template, request, redirect, jsonify
from flask import url_for, flash
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Category, Base, Item
from flask import session as login_session

app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('sqlite:///category_item.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Show all categories and latest items
@app.route('/')
def showCategories():
    categories = session.query(Category).order_by(asc(Category.name))
    items = session.query(Item).order_by(desc(Item.id))
    return render_template(
                'categories.html', categories=categories, items=items)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
