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
-Nose (optional for easy testing)
```
## Getting Started

- Create a virtual enviroment and install Python packages and dependencies

Once you've cloned the project, create a Python virtual environment (virtualenv was used here, but isn't required), and then run ```pip install -r requirements.txt``` to fetch all required packages and their dependencies.

- Set DATABASE_URL env variable 

Once you've set up your virtual environment, you'll want to create a database in PostgreSQL, and set up a DATABASE\_URL env variable to point to your Postgres instance and provide the required username and password (which could be none if you're a local user using ident). The app defaults to look for a database called 'customer_api' if you have not set the DATABASE\_URL env variable.

- Setup database tables, seed database 

After you've set up your database, run ```python manage.py db upgrade``` to set up the necessary tables from the provided migration folder. Optionally, you can also run```python seed.py``` to seed some starter values to play with (this is needed if you want to see results from the show_info.py script).

- Start development server, set optional PORT env variable

At this point, run ```python run.py ```, which will init your server from the provided app package, and your server will be running! Specify the optional PORT env variable to run on a particular port, the app will default to port 5000.


## Walkthrough and Assumptions

As the time and requirements were limited, I did not provide POST methods or any other C(R)UD operations other than GET methods. However, I assumed the API would function best as a RESTful model, and POST/PUT/DELETE functionality can be added by extending current functions with other methods, and by creating further API end points. So you'll see end points like '/customers/\<id>' representing the idea of getting a particular customer, but no '/customers' end point to get all customers (I did however include a '/products' endpoint just to demonstrate the concept). On that note, the end-points assume they would be part of a greater RESTful structure, which is why a cursory glance at the available end-points might seem incomplete ('/customers/categories', but no '/customers'). The end-point naming closely represents the models, with 'products', 'orders', and 'customers' present.

A lot of the ideas for extending various aspects assume some common-sense authentication and all the minor changes that would come with it (extending customers with encrypted password fields, starting and ending sessions, not allowing unauthorized access to any write-level operations) and all the code and modules that would entail. That can get extensive beyond "secure this", so I won't make further mention.

### API

**'/products'** simply provides a JSON response of all products and their ids. With more time, I would want to implement end-points for '/products' with create functionality, as well as '/products/<id>' for individual product read, update, and destroy functionality.


**'/customers/\<id>'** provides all the products ordered across all orders for a particular customer id (and implicitly, that customer's name). Technically, this end-point actually returns all the OrderItems from all that customer's Orders. An extended version of this might provide more information about that customer, with the individual order-functionality perhaps being put into a '/customers\<id>/orders' end-point.

Fulfills Item 6 from the provided project instructions.

**'/customers/categories'** provides a global breakdown of all customers, the categories they've ordered items from, and the number of items in that category they've ordered.

Fulfills Item 3 from the provided project instructions (SQL query is in a txt file creatively titled 'SQLstatement' in the main app package directory).

**'/orders'** right now assumes that it will be servicing GET requests with a start\_date, end\_date, and interval to return the correct orders and their frequency. I find this to be a brittle setup as it is currently, and if I had more time I would want to extend this end point to return a set of orders with a default interval if it simply got a GET request with no further JSON data, as well as create end-points for '/orders/\<id>' and implement remaining CRUD functionality for creating new orders and order-items (you could even start talking about auth here but lets not get ahead of ourselves). 

Fulfills Item 5 from the provided project instructions.

### Models

SQLalchemy and Alembic were used to auto-magically create and manage SQL tables for Customer, Order, OrderItem, Product, and Category models. But nothing here couldn't be done with just SQL and opening/closing database connections. I also won't go into the particulars of the models here beyond their relations - the code in models.py is fairly self-documenting.

The below fulfills Items 1 and 2 from the provided project instructions.

**Customer** has a 1-to-many relationship to Order. A extended version of this might include more customer details and perhaps even login auth info.

**Order** has a foreign-key to Customer (1 Customer per Order) and a 1-to-many relationship to OrderItem. This represents the date and status information for a particular Order and all its items. One could easily extend this model to store more order information that is independent of individual items, again also including auth or credit-card/payment info.

**OrderItem** represents an actual item as part of a larger Order. This includes a 1-to-1 relationship to the actual Product a customer ordered, and a foreign-key to the Order it's attached to (1 Order per OrderItem), as well as individual information like quantity. You could get really granular like Amazon and use this to store actual status information for items (so an individual Order could have multiple Order_Items that can ship out on different days - you get your new hat in the mail tomorrow with Prime, but that new dumpster you ordered will take a while longer).

**Product** represents, you guessed it, a actual Product and it's specific information. You could extend this with all sorts of details, but right now it simply has a many-to-many relationship to it's categories.

**Category**, much like Product, could be extended with all sorts of extra information, and even include things like sub-categories, but right now its just the other end of the many-to-many with Product.

### Some Last Conceptual Thoughts

I have provided a test directory within the app package - you can run it with ```python -m unittest discover app/tests```, or use ```nose2```. Aside from testing the models and end-points for functionality, you may find the tests file to be helpful for verifying the various outputs meet the requirements of the provided project instructions. As the tests use SQLite, you don't have to do any separate database configuration and can simply 'run' the app from the tests file, and hop into ipython if you want to play around. 

**Creating Lists**

To allow customers to create lists of items for bulk-ordering, we would want an additional CustomerList model, which much like the Order model, could store multiple OrderItems. Depending on if you wanted to allow people to share lists socially, you could establish either a 1-to-many or many-to-many relationship between Customer and CustomerList. In SQL, this would mean creating a customer\_list table with id, customer.id, and extending the OrderItem model (order_items) to have an optional list\_id (foreign\_key) field.

Alternatively, you could make use of SQL JSON fields to store these lists individually on each Customer. By extending the customer table to include a JSON data field, you can include multiple lists, each with multiple product.ids and quantities for future ordering. Note, this could get messy for people using a LOT of lists, and having a ton of potentially null fields is never the greatest thing, but is is an option.

**High Traffic/High Volume**

Now this is interesting. If you had geographical information (potentially stored in the Customer or a potential Order.delivery_address model), you could cross-reference that with store locations to help determine where your best 'supply depots' are. If you didn't have this information and you've got a lot or orders coming in for not-a-lot of items, it seems like the best way to distribute this would be based on order time - first-come, first-serve. You could utilize the existing date field on the Order model to create a queue for this. In the best world, you would be able to do both of these things, prioritizing recent orders and cross-referencing that with the nearest supply location. 

One potential way of implementing this would be with a graph, with each customer pointing at multiple store nodes, with vectors weighed by distance and a customer time value. This way, you could have all sorts of customer objects pointing at all sorts of store objects that each have their own values for a particular item. A job queue could be utilized to prioritize by order time, incrementing the longer and order remains unfulfilled. That way, an order placed later that is closer to a supply depot might get serviced before an earlier order placed on the edge of a region, but that score might later flip as the delta since order time goes up. If a store runs out of an item, it would be removed from an indexed list of customers in line for that item, which would remove that store object from all those customers' graphs. I'm not going to pretend anything like this would be casual to whip up, but these are just my thoughts out loud. Well, on paper actually. Digital, to be particular.

Hope you enjoyed this half as much as I did working/writing it! Please let me know if you have any questions, and don't hesitate to reach out at aaron.m.manley@gmail.com.

**The End**