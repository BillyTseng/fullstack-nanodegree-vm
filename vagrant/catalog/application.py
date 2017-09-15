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


@app.route('/')
def showCategories():
    """Show all categories and latest items"""
    categories = session.query(Category).order_by(asc(Category.name))
    items = session.query(Item).order_by(desc(Item.id))
    return render_template(
                'categories.html', categories=categories, items=items)


@app.route('/catalog/<catalog_name>/items')
def showItems(catalog_name):
    """Shows all the items available for this category."""
    categories = session.query(Category).order_by(asc(Category.name))
    cur_category = session.query(Category).filter_by(name=catalog_name)
    for i in cur_category:
        category_id = i.id
    items = session.query(Item).filter_by(category_id=category_id)
    return render_template(
                'items.html',
                categories=categories,
                items=items,
                catalog_name=catalog_name)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
