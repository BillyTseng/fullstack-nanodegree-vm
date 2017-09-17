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
    cur_category = session.query(Category).filter_by(name=catalog_name).one()
    items = session.query(Item).filter_by(category_id=cur_category.id)
    return render_template(
                'items.html',
                categories=categories,
                items=items,
                catalog_name=catalog_name)


@app.route('/catalog/<catalog_name>/<int:item_id>/<item_name>')
def showItemInfo(catalog_name, item_name, item_id):
    """Show specific information of this item."""
    item = session.query(Item).filter_by(id=item_id).one()
    return render_template(
                'iteminfo.html',
                catalog_name=catalog_name,
                item_name=item.name, info=item.description, item_id=item_id)


@app.route(
    '/catalog/<catalog_name>/<int:item_id>/<item_name>/edit',
    methods=['GET', 'POST'])
def editItem(catalog_name, item_name, item_id):
    """Edit information of item."""
    categories = session.query(Category).order_by(asc(Category.name))
    editedItem = session.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['categories']:
            editedItem.category_id = request.form['categories']
            new_categorie = session.query(Category).filter_by(
                                id=editedItem.category_id).one()
            catalog_name = new_categorie.name
        session.add(editedItem)
        session.commit()
        flash('Item Successfully Edited')
        return redirect(url_for(
                'showItemInfo',
                catalog_name=catalog_name,
                item_name=editedItem.name, item_id=editedItem.id))
    else:
        return render_template(
            'edititem.html', item=editedItem, categories=categories)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
