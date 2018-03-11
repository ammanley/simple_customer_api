from flask import Flask, render_template, jsonify, request, make_response
from flask_sqlalchemy import SQLAlchemy
import os
import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'postgres://localhost/customer_api'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
if os.environ.get('ENV') == 'prod':
    app.config['DEBUG'] = False
else:
    app.config['DEBUG'] = True

db = SQLAlchemy(app)

from app.models import Customer, Category, Product, Order

@app.route("/", methods=['GET'])
def root():
    """Just tell the user the app is running and the routes avaliable"""
    return render_template('index.html')


@app.route("/customers/categories", methods=['GET'])
def customer_categories():
    """
    Return JSON of the quantity of items purchased in a particular 
    category by a certain customer who placed order
    """
    results = []
    customers = Customer.query.all()
    for customer in customers:
        category_quantities = {}
        for order in customer.orders:
             for item in order.order_items:
                for category in item.product.categories:
                    if category in category_quantities:
                        category_quantities[category] += item.quantity
                    else:
                        category_quantities[category] = item.quantity
        for category in category_quantities:
            results.append({'id': customer.id, 'name': customer.name, 'category_id': category.id, 'category': category.name, 'quantity': category_quantities[category]})
    return jsonify(results)


@app.route("/customers", methods=['GET'])
def customers():
    """
    Provides  JSON of all customers with thteir associated IDs (so you can lookup someone easy during testing the API
    """
    customers = Customer.query.all()
    return jsonify(customers)


@app.route("/customers/<id>", methods=['GET'])
def customers_orders(id):
    """
    Provide JSON of a customer's orders and their corresponding items
    """
    orders = Customer.query.filter_by(id=id).first().orders
    results = []
    for order in orders:
        for item in order.order_items:
            results.append({'order.id': item.order_id, 'product.id': item.product_id, 'name': item.product.name, 'quantity': item.quantity})
    return jsonify(results)


@app.route("/products", methods=['GET'])
def products():
    """
    Provide JSON of all current products that can be ordered and their product.ids
    """
    if request.method == 'GET':
        results = {product.id: product.name for product in Product.query.all()}
        return jsonify(results)


@app.route("/orders", methods=['GET'])
def products_by_date():
    """
    Provide a JSON GET request with 'start_date' and 'end_date' 
    keys in mm/dd/yyyy format and a 'interval' key of day, week, or month
    and returns list of all products sold in time interval, and how many by day/week/month
    """
    if request.method == 'GET':
        json = request.get_json()
        try:
            start_date = datetime.datetime.strptime(json['start_date'], '%m/%d/%Y')
            end_date = datetime.datetime.strptime(json['end_date'], '%m/%d/%Y')
        except ValueError:
            return make_response(jsonify(error='Invalid date format, use MM/DD/YYYY (11/20/2000 for Nov 20, 2001)'), 400)
        interval = json['interval']
        if interval not in ['day', 'month', 'year']:
            return make_response(jsonify(error='Invalid interval format (use day, month, or year).'), 400)
        delta = end_date-start_date
        orders = Order.query.filter(Order.date.between(start_date, end_date)).all()
        items_quantities = {}
        for order in orders:
            for item in order.order_items:
                items_quantities[item.product.name] = items_quantities.get(item.product.name, 0) + item.quantity
        if interval == 'day':
            results = {key: value/delta.days for key,value in items_quantities.items()}
        elif interval == 'month':
            results = {key: value/(int(delta.days/30)) for key,value in items_quantities.items()}
        else: 
            results = {key: value/int(delta.days/365.25) for key,value in items_quantities.items()}
        return jsonify(results)