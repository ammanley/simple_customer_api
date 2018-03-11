from app import db
from app.models import Product, Category, Customer, Order, OrderItem

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