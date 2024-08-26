from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy.exc import SQLAlchemyError

# Initialize Flask app
app = Flask(__name__)

# Configure MySQL Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:password@localhost/ecommerce_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Database and Marshmallow
db = SQLAlchemy(app)
ma = Marshmallow(app)

# Database Models
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)

class CustomerAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    customer = db.relationship('Customer', backref=db.backref('accounts', lazy=True))

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    products = db.relationship('Product', secondary='order_product')

class OrderProduct(db.Model):
    __tablename__ = 'order_product'
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)

# Marshmallow Schemas
class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer

class CustomerAccountSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = CustomerAccount

class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product

class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Order

# Task 1: Customer Management

@app.route('/customers', methods=['POST'])
def add_customer():
    data = request.get_json()
    try:
        new_customer = Customer(name=data['name'], email=data['email'], phone=data['phone'])
        db.session.add(new_customer)
        db.session.commit()
        return customer_schema.jsonify(new_customer), 201
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500

@app.route('/customers/<int:id>', methods=['GET'])
def get_customer(id):
    customer = Customer.query.get(id)
    if customer:
        return customer_schema.jsonify(customer)
    else:
        return jsonify({'message': 'Customer not found'}), 404

@app.route('/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    data = request.get_json()
    customer = Customer.query.get(id)
    if customer:
        customer.name = data['name']
        customer.email = data['email']
        customer.phone = data['phone']
        db.session.commit()
        return customer_schema.jsonify(customer)
    else:
        return jsonify({'message': 'Customer not found'}), 404

@app.route('/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    customer = Customer.query.get(id)
    if customer:
        db.session.delete(customer)
        db.session.commit()
        return jsonify({'message': 'Customer deleted successfully'})
    else:
        return jsonify({'message': 'Customer not found'}), 404

# Task 2: Customer Account Management

@app.route('/customer_accounts', methods=['POST'])
def add_customer_account():
    data = request.get_json()
    try:
        new_account = CustomerAccount(username=data['username'], password=data['password'], customer_id=data['customer_id'])
        db.session.add(new_account)
        db.session.commit()
        return customer_account_schema.jsonify(new_account), 201
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500

@app.route('/customer_accounts/<int:id>', methods=['GET'])
def get_customer_account(id):
    account = CustomerAccount.query.get(id)
    if account:
        return customer_account_schema.jsonify(account)
    else:
        return jsonify({'message': 'Customer account not found'}), 404

@app.route('/customer_accounts/<int:id>', methods=['PUT'])
def update_customer_account(id):
    data = request.get_json()
    account = CustomerAccount.query.get(id)
    if account:
        account.username = data['username']
        account.password = data['password']
        db.session.commit()
        return customer_account_schema.jsonify(account)
    else:
        return jsonify({'message': 'Customer account not found'}), 404

@app.route('/customer_accounts/<int:id>', methods=['DELETE'])
def delete_customer_account(id):
    account = CustomerAccount.query.get(id)
    if account:
        db.session.delete(account)
        db.session.commit()
        return jsonify({'message': 'Customer account deleted successfully'})
    else:
        return jsonify({'message': 'Customer account not found'}), 404

# Task 3: Product Management

@app.route('/products', methods=['POST'])
def add_product():
    data = request.get_json()
    try:
        new_product = Product(name=data['name'], price=data['price'])
        db.session.add(new_product)
        db.session.commit()
        return product_schema.jsonify(new_product), 201
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500

@app.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    product = Product.query.get(id)
    if product:
        return product_schema.jsonify(product)
    else:
        return jsonify({'message': 'Product not found'}), 404

@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    data = request.get_json()
    product = Product.query.get(id)
    if product:
        product.name = data['name']
        product.price = data['price']
        db.session.commit()
        return product_schema.jsonify(product)
    else:
        return jsonify({'message': 'Product not found'}), 404

@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get(id)
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Product deleted successfully'})
    else:
        return jsonify({'message': 'Product not found'}), 404

@app.route('/products', methods=['GET'])
def list_products():
    products = Product.query.all()
    return products_schema.jsonify(products)

# Task 4: Order Processing

@app.route('/orders', methods=['POST'])
def place_order():
    data = request.get_json()
    try:
        new_order = Order(customer_id=data['customer_id'], date=data['date'])
        for item in data['products']:
            product = Product.query.get(item['product_id'])
            if product:
                new_order.products.append(OrderProduct(order_id=new_order.id, product_id=item['product_id'], quantity=item['quantity']))
        db.session.add(new_order)
        db.session.commit()
        return order_schema.jsonify(new_order), 201
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500

@app.route('/orders/<int:id>', methods=['GET'])
def get_order(id):
    order = Order.query.get(id)
    if order:
        return order_schema.jsonify(order)
    else:
        return jsonify({'message': 'Order not found'}), 404

@app.route('/orders/<int:id>', methods=['PUT'])
def update_order(id):
    data = request.get_json()
    order = Order.query.get(id)
    if order:
        order.date = data['date']
        db.session.commit()
        return order_schema.jsonify(order)
    else:
        return jsonify({'message': 'Order not found'}), 404

@app.route('/orders/<int:id>', methods=['DELETE'])
def delete_order(id):
    order = Order.query.get(id)
    if order:
        db.session.delete(order)
        db.session.commit()
        return jsonify({'message': 'Order deleted successfully'})
    else:
        return jsonify({'message': 'Order not found'}), 404

# Optional Bonus Features

@app.route('/products/stock/<int:id>', methods=['GET'])
def view_stock(id):
    product = Product.query.get(id)
    if product:
        return jsonify({'stock': product.stock})
    else:
        return jsonify({'message': 'Product not found'}), 404

@app.route('/products/stock/<int:id>', methods=['PUT'])
def update_stock(id):
    data = request.get_json()
    product = Product.query.get(id)
    if product:
        product.stock = data['stock']
        db.session.commit()
        return jsonify({'message': 'Stock updated successfully'})
    else:
        return jsonify({'message': 'Product not found'}), 404

@app.route('/orders/track/<int:id>', methods=['GET'])
def track_order(id):
    order = Order.query.get(id)
    if order:
        return order_schema.jsonify(order)
    else:
        return jsonify({'message': 'Order not found'}), 404

@app.route('/orders/history/<int:customer_id>', methods=['GET'])
def order_history(customer_id):
    orders = Order.query.filter_by(customer_id=customer_id).all()
    return orders_schema.jsonify(orders)

@app.route('/orders/cancel/<int:id>', methods=['DELETE'])
def cancel_order(id):
    order = Order.query.get(id)
    if order:
        db.session.delete(order)
        db.session.commit()
        return jsonify({'message': 'Order canceled successfully'})
    else:
        return jsonify({'message': 'Order not found'}), 404

@app.route('/orders/total/<int:id>', methods=['GET'])
def calculate_order_total(id):
    order = Order.query.get(id)
    if order:
        total = sum([OrderProduct.query.filter_by(order_id=id, product_id=p.product_id).first().quantity * Product.query.get(p.product_id).price for p in OrderProduct.query.filter_by(order_id=id)])
        return jsonify({'total_price': total})
    else:
        return jsonify({'message': 'Order not found'}), 404

# Initialize the Database
with app.app_context():
    db.create_all()

# Run the App
if __name__ == '__main__':
    app.run(debug=True)
