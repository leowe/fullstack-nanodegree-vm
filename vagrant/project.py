from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from database_setup import Base, Restaurant, MenuItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


app = Flask(__name__)

engine = create_engine("sqlite:///restaurantmenu.db")
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/restaurants/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):
	restaurant = session.query(MenuItem).filter_by(id = restaurant_id).one()
	items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id)
	return render_template('menu.html', restaurant=restaurant, items=items)


@app.route('/restaurants/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
	restaurant = session.query(MenuItem).filter_by(id = restaurant_id).one()
	items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id)
	return jsonify(MenuItems=[i.serialize for i in items])


@app.route('/restaurants/<int:restaurant_id>/<int:menuitem_id>/item/JSON')
def restaurantItemJSON(restaurant_id, menuitem_id):
	item = session.query(MenuItem).filter_by(restaurant_id = restaurant_id, id = menuitem_id).one()
	return jsonify(MenuItems=item.serialize)


@app.route('/restaurants/<int:restaurant_id>/createItem/', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
	if request.method == 'POST':
		newItem = MenuItem(name = request.form['name'], restaurant_id = restaurant_id)
		session.add(newItem)
		session.commit()
		flash("new menu item created!")
		return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))
	else:
		return render_template('newmenuitem.html', restaurant_id=restaurant_id)


@app.route('/restaurants/<int:restaurant_id>/edit/<int:menuitem_id>', methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menuitem_id):
	item = session.query(MenuItem).filter_by(id=menuitem_id).one()
	if request.method == 'POST':
		if request.form['name']:
			item.name = request.form['name']
		session.add(item)
		session.commit()
		flash("menu item edited!")
		return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))
	else: 
		return render_template('editMenuItem.html', restaurant_id=restaurant_id, menuitem_id=menuitem_id, i=item)


@app.route('/restaurants/<int:restaurant_id>/delete/<int:menuitem_id>', methods=['GET','POST'])
def deleteMenuItem(restaurant_id, menuitem_id):
	item = session.query(MenuItem).filter_by(id=menuitem_id).one()
	if request.method == 'POST':
		session.delete(item)
		session.commit()
		flash("menu item deleted!")
		return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))
	else: 
		return render_template('deleteMenuItem.html', restaurant_id=restaurant_id, i=item)


if __name__ == '__main__':
	app.secret_key = 'super_secret'
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)
