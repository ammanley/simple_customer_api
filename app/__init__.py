from flask import Flask, render_template, jsonify, request, make_response, abort
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


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route("/", methods=['GET'])
def root():
    return "This is the root of the app, you probablly are looking for /api"


@app.route("/api/", methods=['GET'])
def index():
    """Just tell the user the app is running and the routes avaliable"""
    return render_template('index.html')


@app.route("/api/customers", methods=['GET'])
def customers():
    """
    Provides  JSON of all customers with thteir associated IDs (so you can look up someone easy during testing the API
    """
    customers = [repr(customer) for customer in Customer.query.all()]
    return jsonify(customers)


@app.route("/api/customers/<id>", methods=['GET'])
def customers_orders(id):
    """
    Provide JSON of a customer's orders and their corresponding items
    """
    customer = Customer.query.filter_by(id=id).first()
    if not customer:
        #  return render_template('404.html'), 404
        abort(404)
    orders = customer.orders
    results = []
    for order in orders:
        for item in order.order_items:
            results.append({
                'order.id': item.order_id, 
                'product.id': item.product_id, 
                'name': item.product.name, 
                'quantity': item.quantity
                })
    return jsonify(results)


@app.route("/api/products/categories", methods=['GET'])
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


@app.route("/api/products", methods=['GET'])
def products():
    """
    Provide JSON of all current products that can be ordered and their product.ids
    """
    if request.method == 'GET':
#        import ipdb; ipdb.set_trace()
        results = {product.id: [product.name, repr(product.categories)] for product in Product.query.all()}
        return jsonify(results)


@app.route("/api/orders", methods=["GET"])
@app.route("/api/orders/<start_date>/<end_date>/", methods=['GET'])
@app.route("/api/orders/<start_date>/<end_date>/<interval>", methods=['GET'])
def orders_by_date(start_date=None, end_date=None, interval=None):
    """
    Provide a GET request with 'start_date' and 'end_date' 
    keys in yyyy-mm-dd format and an optional 'interval' key of day, week, or month
    and returns list of all products sold in time interval, and how many by day/week/month
    """
    if request.method == 'GET':
        if all(param is None for param in [start_date, end_date, interval]):
            orders = Order.query.all()
            results = [
                [order.customer_id, 
                repr(order.customers), 
                order.date.strftime('%Y-%m-%d'), 
                repr(order.order_items)] for order in orders
            ]
            return jsonify(results)
        try:
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            return make_response(jsonify(
                error='Invalid date format, use YYYY-MM-DD (2000-11-20 for Nov 20, 2001)'),
                400)
        if interval is not None and interval not in ['day', 'month', 'year']:
            return make_response(jsonify(error='Invalid interval format (use day, month, or year).'), 400)
        delta = end_date-start_date
        if delta.total_seconds() < 0:
            return make_response(jsonify(error='Invalid date range, ending date cannot be before starting date.'), 400)
        orders = Order.query.filter(Order.date.between(start_date, end_date)).all()
        items_quantities = {}
        for order in orders:
            for item in order.order_items:
                items_quantities[item.product.name] = items_quantities.get(item.product.name, 0) + item.quantity
        if interval == 'day':
            results = {key: value/delta.days for key,value in items_quantities.items()}
        elif interval == 'month':
            results = {key: value/(int(delta.days/30)) for key,value in items_quantities.items()}
        elif interval == 'year': 
            results = {key: value/int(delta.days/365.25) for key,value in items_quantities.items()}
        else:
            results = [
                [order.customer_id, 
                repr(order.customers), 
                order.date.strftime('%Y-%m-%d'), 
                repr(order.order_items)] for order in orders
            ]
        return jsonify(results)