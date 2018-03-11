from app import app, db
from app.models import Product, Category, Customer, Order, OrderItem
import unittest
from flask import json


class TestApp(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        app.config['TESTING'] = True
        app.config['DEBUG'] = True
        app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///testing.db'
        db.drop_all()
        db.create_all()

        category1 = Category('Cleaning')
        category2 = Category('Chemicals')
        category3 = Category('Household Supplies')

        product0 = Product('Bleach')
        product1 = Product('toilet paper')
        product2 = Product('mop')
        product3 = Product('small bucket')
        product5 = Product('hand soap')
        product0.categories.extend([category1, category2])
        product1.categories.extend([category2, category3])
        product2.categories.append(category3)
        product3.categories.append(category3)
        product5.categories.append(category1)

        order0 = Order(1, 'Waiting')
        order1 = Order(1, 'Waiting')
        order2 = Order(2, 'In Transit')
        order3 = Order(3, 'Delivered')

        customer1 = Customer('Donald Trump')
        customer2 = Customer('George Washington')
        customer3 = Customer('BILL Clinton')

        db.session.add_all([order0, order1, order2, order3, customer1, customer2, customer3, product0, product1, product2, product3, product5, category1, category2, category3])
        db.session.commit()
        order_item0 = OrderItem(5, product0.id, order0.id)
        order_item1 = OrderItem(5, product0.id, order1.id)
        order_item2 = OrderItem(2, product3.id, order1.id)
        order_item3 = OrderItem(20, product1.id, order2.id)
        order_item4 = OrderItem(1, product2.id, order3.id)
        db.session.add_all([order_item0, order_item1, order_item2, order_item3, order_item4])
        db.session.commit()
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()

# ***TEST RELATIONS***

    def test_has_product(self):
        product = Product.query.filter_by(name='Bleach').first()
        self.assertEqual(product.name, 'Bleach')

    def test_has_categories(self):
        categories = Category.query.all()
        category1 = Category.query.filter_by(name='Cleaning').first()
        category2 = Category.query.filter_by(name='Chemicals').first()
        self.assertTrue(category1 in categories)
        self.assertTrue(category2 in categories)

    def test_product_has_category(self):
        product = Product.query.filter_by(name='Bleach').first()
        category1 = Category.query.filter_by(name='Cleaning').first()
        category2 = Category.query.filter_by(name='Chemicals').first()
        self.assertEqual(len(product.categories), 2)
        self.assertTrue(category1 in product.categories)
        self.assertTrue(category2 in product.categories)

    def test_category_has_product(self):
        category1 = Category.query.filter_by(name='Cleaning').first()
        product = Product.query.filter_by(name='Bleach').first()
        self.assertTrue(len(category1.products), 1)
        self.assertTrue(product in category1.products)

    def test_customer_has_order(self):
        customer = Customer.query.filter_by(name='Donald Trump').first()
        order1 = Order(1, 'Waiting')
        order2 = Order(1, 'In Transit')
        db.session.add_all([order1, order2])
        db.session.commit()
        self.assertEqual(len(customer.orders), 4)
        self.assertTrue(order1 in customer.orders)
        self.assertTrue(order2 in customer.orders)

    def test_order_has_items(self):
        customer = Customer.query.filter_by(name='George Washington').first()
        order_items = customer.orders[0].order_items
        tp = Product.query.filter_by(name='toilet paper').first()
        self.assertEqual(len(order_items), 1)
        self.assertEqual(order_items[0].quantity, 20)
        self.assertEqual(order_items[0].product, tp)

    def test_order_status(self):
        order1 = Order.query.first()
        self.assertTrue(order1.status == 'In Transit' or 'Delivered' or 'Waiting')

    def test_order_items(self):
        product1 = Product.query.filter_by(name='Bleach').first()
        order1 = Order.query.filter_by(id=1).first()
        order_item1 = OrderItem.query.filter_by(product_id=1).first()
        self.assertTrue(order_item1.order, order1)
        self.assertEqual(len(order1.order_items), 1)
        self.assertEqual(order_item1.product, product1)

    def test_order_date(self):
        order1 = Order.query.first()
        self.assertTrue(order1.date)

# ***Test API***

    def test_get_orders_for_customers(self):
        response = self.app.get('/customers/categories')
        response_json = json.loads(response.data)
        expected_json = [
         {'category': 'Chemicals',
          'category_id': 2,
          'id': 1,
          'name': 'Donald Trump',
          'quantity': 10},
         {'category': 'Cleaning',
          'category_id': 1,
          'id': 1, 
          'name': 'Donald Trump',
          'quantity': 10},
         {'category': 'Household Supplies',
          'category_id': 3,
          'id': 1,
          'name': 'Donald Trump',
          'quantity': 2},
         {'category': 'Chemicals',
          'category_id': 2,
          'id': 2,
          'name': 'George Washington',
          'quantity': 20},
         {'category': 'Household Supplies',
          'category_id': 3,
          'id': 2,
          'name': 'George Washington',
          'quantity': 20},
         {'category': 'Household Supplies',
          'category_id': 3,
          'id': 3,
          'name': 'BILL Clinton',
          'quantity': 1}
        ]
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response_json, expected_json)

    def test_customer_orders(self):
        response = self.app.get('/customers/1')
        response_json = json.loads(response.data)
        expected_json = [
          {'name': 'Bleach', 'order.id': 1, 'product.id': 1, 'quantity': 5},
          {'name': 'Bleach', 'order.id': 2, 'product.id': 1, 'quantity': 5},
          {'name': 'small bucket', 'order.id': 2, 'product.id': 5, 'quantity': 2}
        ]
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response_json, expected_json)

    def test_products(self):
        response = self.app.get('/products')
        response_json = json.loads(response.data)
        expected_json = {
          "1": "Bleach", 
          "2": "hand soap", 
          "3": "toilet paper", 
          "4": "mop", 
          "5": "small bucket"
          }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json, expected_json)

    def test_producs_sold_bad_syntax(self):
        order1 = Order(1, 'Waiting', date='11/20/2000')
        order2 = Order(2, 'In Transit', date='3/5/2010')
        db.session.add_all([order1, order2])
        db.session.commit()
        order_item0 = OrderItem(5, 1, order1.id)
        order_item1 = OrderItem(10, 2, order1.id)
        order_item2 = OrderItem(25, 3, order2.id)
        db.session.add_all([order_item0, order_item1, order_item2])
        db.session.commit()
        response = self.app.get('/orders', 
            headers={'Content-Type': 'application/json'},
            data=json.dumps({
                'start_date': '1/1/2000',
                'end_date': '6/15/2012',
                'interval': 'monthhhhhhhh'
                })
            )
        response_json = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['error'], 'Invalid interval format (use day, month, or year).')    

    def test_bad_date(self):
        response = self.app.get('/orders', 
            headers={'Content-Type': 'application/json'},
            data=json.dumps({
                'start_date': '13/1/200',
                'end_date': '6/15/212',
                'interval': 'monthhhhhhhh'
                })
            )
        response_json = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['error'], 'Invalid date format, use MM/DD/YYYY (11/20/2000 for Nov 20, 2001)')

    def test_products_sold_month(self):
        order1 = Order(1, 'Waiting', date='11/20/2000')
        order2 = Order(2, 'In Transit', date='3/5/2010')
        db.session.add_all([order1, order2])
        db.session.commit()
        order_item0 = OrderItem(5, 1, order1.id)
        order_item1 = OrderItem(10, 2, order1.id)
        order_item2 = OrderItem(25, 3, order2.id)
        db.session.add_all([order_item0, order_item1, order_item2])
        db.session.commit()
        response = self.app.get('/orders', 
            headers={'Content-Type': 'application/json'},
            data=json.dumps({
                'start_date': '1/1/2000',
                'end_date': '6/15/2012',
                'interval': 'month'
                })
            )
        response_json = json.loads(response.data)
        expected_json = {
          'Bleach': 0.033112582781456956,
          'hand soap': 0.06622516556291391,
          'toilet paper': 0.16556291390728478
          }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_json), 3)
        self.assertEqual(response_json, expected_json)

    def test_products_sold_year(self):
        response = self.app.get('/orders', 
            headers={'Content-Type': 'application/json'},
            data=json.dumps({
                'start_date': '1/1/2000',
                'end_date': '6/15/2018',
                'interval': 'year'
                })
            )
        response_json = json.loads(response.data)
        expected_json = {
            'Bleach': 0.5555555555555556,
            'mop': 0.05555555555555555,
            'small bucket': 0.1111111111111111,
            'toilet paper': 1.1111111111111112
            }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_json), 4)
        self.assertEqual(response_json, expected_json)


if __name__ == "__main__":
    unittest.main()