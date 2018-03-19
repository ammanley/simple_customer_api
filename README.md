# Shipt Simple Customer API

This is a simple REST API built in Flask, designed to take REST URL inputs and return JSON. It uses SQLalchemy to interface with a Postgres database (using psycopg2 driver) and Alembic for database migration support. It demonstrates some key REST, unit-testing, and MVC ideas without getting bogged down in a full-fledged framework. 
***

## Requirements
```
-Python3
-Flask
-Alembic
-PostgreSQL
-SQLAlchemy
-Nose2 (optional for easy testing)
```
## Getting Started

**1. Create a virtual enviroment and install Python packages and dependencies**

Once you've cloned the project, create a Python virtual environment (virtualenv was used here, but isn't required), and then run ```pip install -r requirements.txt``` to fetch all required packages and their dependencies.

**2. Set DATABASE_URL env variable**

Once you've set up your virtual environment, you'll want to create a database in PostgreSQL, and set up a DATABASE\_URL env variable to point to your Postgres instance and provide the required username and password (which could be none if you're a local user using ident). The app defaults to look for a database called 'customer_api' if you have not set the DATABASE\_URL env variable.

**3. Setup database tables, seed database**

After you've set up your database, run ```python manage.py db init/migrate/upgrade``` to set up the necessary tables from the provided migration folder. Optionally, you can also run```python seed.py``` to seed some starter values to play with (this is needed if you want to see results from the show_info.py script).

**4. Start development server, set optional PORT env variable**

At this point, run ```python run.py ```, which will init your server from the provided app package, and your server will be running! Specify the optional PORT env variable to run on a particular port, the app will default to port 5000.


## API

```api/products'```  provides JSON of all products and their IDs.

```api/customers``` provides JSON of all customers.

```api/customers/\<id>'``` provides JSON of all the products ordered across all orders for a particular customer id (and implicitly, that customer's name). Technically, this end-point actually returns all the OrderItems from all that customer's Orders. Will throw 404 on non-existant customer ID

```api/orders'``` provides JSON of all orders.

```api/orders/categories'``` provides a global breakdown of all customers, the categories they've ordered items from, and the number of items in that category they've ordered.

```api/orders/YYYY-MM-DD/YYYY-MM-DD'``` provides JSON of a breakdown of all orders within a certain date range, taking a start-date and an end-date. Will throw a JSON error code if date is formatted wrong, or if end-date is before start-date.

```api/orders/YYYY-MM-DD/YYYY-MM-DD/<day/week/month>/<\export>'``` provides JSON of a breakdown of all orders within a certain date range, and then breaks down how often particular items in that range were ordered by day/week/month. Including the optional ```export``` flag will download the results as a CSV file.

## Walkthrough and Assumptions

I have provided a test directory within the app package - you can run it with ```python -m unittest discover app/tests```, or use ```nose2```. Aside from testing the models and end-points for functionality, you may find the tests file to be helpful for verifying the various outputs meet the requirements of the provided project instructions.

The app supports a simple GUI on the ```/api/```

**Assumptions**

- I assumed that graphics, styling, and browser-use would be limited factors here, with the assumption being that this would be a simple GET-only end-point to query and view data.

- I assumed only the most basic of items in the models. functionality such as user verification of identity and user-auth are not implemented or supported.

- In the same vein, the end-points are configured to only receive GET requests, but could be extended to add if POST/PUT/DELETE

- CSRF, XSS, and SQL-injection were not considered since this is a GET-only API.

### Models

SQLalchemy and Alembic were used to auto-magically create and manage SQL tables for Customer, Order, OrderItem, Product, and Category models. But nothing here couldn't be done with just SQL and opening/closing database connections. I also won't go into the particulars of the models here beyond their relations - the code in models.py is fairly self-documenting.

**Customer** has a 1-to-many relationship to Order. 

**Order** has a foreign-key to Customer (1 Customer per Order) and a 1-to-many relationship to OrderItem. This represents the date and status information for a particular Order and all its items. One could easily extend this model to store more order information that is independent of individual items, again also including auth or credit-card/payment info.

**OrderItem** represents an actual item as part of a larger Order. This includes a 1-to-1 relationship to the actual Product a customer ordered, and a foreign-key to the Order it's attached to (1 Order per OrderItem), as well as individual information like quantity. 

**Product** represents a individual Product and it's specific information, many-to-many relationship to it's categories.

**Category**, represents a individual Category with a many-to-many relation with Product.


## Answers to Questions


**Creating Lists**

The ability to create a modifiable list for instant-ordering is not very different from creating an order with many items. You could create a simple order_lists table to associate any given list with a customer ID, and then a order_lists_items table to associate any given list-item with its corresponding list, as well as hold information about what the product to be ordered in the future will be, and in what quantity.

This approach is fairly easy to extend, but you may notice it doesn't look too different from simply creating an order with its associate order_details. This approach would create two new tables yes, but as I don't anticipate the order_lists or its associated order_lists_items being written or read to anywhere near as much as the orders and orders_details tables, you could more easily implement maintainable indexes on the list table, so that in the end the same amount of actual disk space is used to store your information, but your ability to recall and turn a order_list into an actual bulk order is much quicker.

```
order_lists
----------------
id | customer.id

order_lists_items
------------------------------------------
id | order_list.id | product.id | quantity
```

**High Traffic/High Volume**
A customer who orders later that has a store with an available item closer may get their order sooner than a customer who ordered earlier, but lives farther away from a store. But, a customer who orders earlier should never have to wait for their order to be processed after someone who orders later. To deal with high traffic for a limited item, you should have a Queue of orders placed - customers who place an order earlier are closer to the front of the queue, and get their orders fulfilled before people at the end of the queue. If the exact inventory shows that the item has run out, then people at the back of the Queue who placed their orders later need to be informed either that there will be a wait to get an item from a more distant store, or that they may need to re-think their order items.
~      
