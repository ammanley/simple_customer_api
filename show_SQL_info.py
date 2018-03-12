from app.models import Customer

def customer_by_category():
    customers = Customer.query.all()
    print("CustomerID, CutomerName, CategoryID, CategoryName, Quantity")
    print('_________________________________________________________')
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
            print(customer.id, customer.name, category.id, category, category_quantities[category])

if __name__ == "__main__":
    print('************************************************************')
    customer_by_category()