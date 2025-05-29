from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
import uuid

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # farmer, consumer, processor, retailer
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    farmer_profile = db.relationship('FarmerProfile', backref='user', uselist=False)
    products = db.relationship('Product', backref='farmer', lazy=True)
    ratings = db.relationship('Rating', backref='user', lazy=True)
    messages_sent = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy=True)
    messages_received = db.relationship('Message', foreign_keys='Message.recipient_id', backref='recipient', lazy=True)
    transactions = db.relationship('Transaction', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class FarmerProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    farm_name = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    farm_size = db.Column(db.Float)  # in acres
    farming_type = db.Column(db.String(50))  # organic, conventional, etc.
    certification = db.Column(db.String(200))
    certification_file = db.Column(db.String(200))
    description = db.Column(db.Text)
    phone = db.Column(db.String(20))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    established_year = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    variety = db.Column(db.String(100))
    batch_id = db.Column(db.String(50), unique=True, nullable=False)
    qr_code_path = db.Column(db.String(200))
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=False)  # kg, tons, pieces, etc.
    harvest_date = db.Column(db.Date, nullable=False)
    expiry_date = db.Column(db.Date)
    price_per_unit = db.Column(db.Float)
    grade = db.Column(db.String(10))  # A1, B1, etc.
    pesticide_used = db.Column(db.Boolean, default=False)
    pesticide_details = db.Column(db.Text)
    description = db.Column(db.Text)
    image_path = db.Column(db.String(200))
    status = db.Column(db.String(20), default='available')  # available, sold, processed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    ratings = db.relationship('Rating', backref='product', lazy=True)
    journey_steps = db.relationship('ProductJourney', backref='product', lazy=True)
    transactions = db.relationship('Transaction', backref='product', lazy=True)

    def __init__(self, **kwargs):
        super(Product, self).__init__(**kwargs)
        if not self.batch_id:
            self.batch_id = self.generate_batch_id()

    def generate_batch_id(self):
        return f"TH{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"

    @property
    def average_rating(self):
        if self.ratings:
            return sum(r.rating for r in self.ratings) / len(self.ratings)
        return 0

class ProductJourney(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    stage = db.Column(db.String(50), nullable=False)  # harvested, processed, shipped, retail, sold
    location = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    details = db.Column(db.Text)
    handler_name = db.Column(db.String(120))
    handler_contact = db.Column(db.String(100))
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    vehicle_info = db.Column(db.String(200))
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    blockchain_hash = db.Column(db.String(64))  # Mock blockchain hash

    def __init__(self, **kwargs):
        super(ProductJourney, self).__init__(**kwargs)
        if not self.blockchain_hash:
            self.blockchain_hash = self.generate_mock_hash()

    def generate_mock_hash(self):
        import hashlib
        data = f"{self.product_id}{self.stage}{self.timestamp}{uuid.uuid4()}"
        return hashlib.sha256(data.encode()).hexdigest()

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    review = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # purchase, sale, processing
    amount = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, completed, cancelled
    blockchain_hash = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        super(Transaction, self).__init__(**kwargs)
        if not self.blockchain_hash:
            self.blockchain_hash = self.generate_mock_hash()

    def generate_mock_hash(self):
        import hashlib
        data = f"{self.user_id}{self.product_id}{self.amount}{self.created_at}{uuid.uuid4()}"
        return hashlib.sha256(data.encode()).hexdigest()
