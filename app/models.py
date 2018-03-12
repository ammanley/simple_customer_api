from app import db
import datetime


class Order(db.Model):

    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    order_items = db.relationship('OrderItem', backref='order', lazy=True)

    def __init__(self, customer_id, status, date=datetime.datetime.now().strftime('%Y-%m-%d')):
        self.customer_id = customer_id
        self.status = status
        self.date = datetime.datetime.strptime(date, '%Y-%m-%d')

    def __repr__(self):
        return "Customer: {}, {}, {}".format(self.customer_id, self.status, self.date)


class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)

    def __init__(self, quantity, product_id, order_id):
        self.quantity = quantity
        self.order_id = order_id
        self.product_id = product_id

    def __repr__(self):
        return "Order ID: {}, Quantity: {}, Product: {}".format(self.order_id, self.quantity, self.product.name)


class Category(db.Model):

    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "{}".format(self.name)


products_categories = db.Table('products_categories',
    db.Column('product_id', db.Integer, db.ForeignKey('products.id')),
    db.Column('category_id',db.Integer, db.ForeignKey('categories.id'))
)


class Product(db.Model):

    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    categories = db.relationship('Category', secondary=products_categories, backref='products')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "{},{}".format(self.name, self.categories)


orders_products = db.Table('orders_products', 
    db.Column('product_id', db.Integer, db.ForeignKey('products.id')),
    db.Column('order_id', db.Integer, db.ForeignKey('orders.id'))
)


class Customer(db.Model):

    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    orders = db.relationship('Order', backref='customers', lazy=True)


    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "{}".format(self.name)

