from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, FloatField, IntegerField, DateField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional, EqualTo
from datetime import date

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[
        ('farmer', 'Farmer'),
        ('consumer', 'Consumer'),
        ('processor', 'Processor'),
        ('retailer', 'Retailer')
    ], validators=[DataRequired()])

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class FarmerProfileForm(FlaskForm):
    farm_name = StringField('Farm Name', validators=[DataRequired(), Length(max=120)])
    location = StringField('Location', validators=[DataRequired(), Length(max=200)])
    farm_size = FloatField('Farm Size (acres)', validators=[Optional(), NumberRange(min=0)])
    farming_type = SelectField('Farming Type', choices=[
        ('organic', 'Organic'),
        ('conventional', 'Conventional'),
        ('sustainable', 'Sustainable'),
        ('biodynamic', 'Biodynamic')
    ], validators=[Optional()])
    certification = StringField('Certification', validators=[Optional(), Length(max=200)])
    certification_file = FileField('Certification Document', validators=[
        Optional(), FileAllowed(['pdf', 'jpg', 'jpeg', 'png'], 'Only PDF and image files allowed!')
    ])
    description = TextAreaField('Farm Description', validators=[Optional()])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    latitude = FloatField('Latitude', validators=[Optional(), NumberRange(min=-90, max=90)])
    longitude = FloatField('Longitude', validators=[Optional(), NumberRange(min=-180, max=180)])
    established_year = IntegerField('Established Year', validators=[Optional(), NumberRange(min=1800, max=date.today().year)])

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired(), Length(max=120)])
    category = SelectField('Category', choices=[
        ('vegetables', 'Vegetables'),
        ('fruits', 'Fruits'),
        ('grains', 'Grains'),
        ('herbs', 'Herbs'),
        ('dairy', 'Dairy'),
        ('meat', 'Meat'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    variety = StringField('Variety', validators=[Optional(), Length(max=100)])
    quantity = FloatField('Quantity', validators=[DataRequired(), NumberRange(min=0)])
    unit = SelectField('Unit', choices=[
        ('kg', 'Kilograms'),
        ('tons', 'Tons'),
        ('pieces', 'Pieces'),
        ('liters', 'Liters'),
        ('boxes', 'Boxes')
    ], validators=[DataRequired()])
    harvest_date = DateField('Harvest Date', validators=[DataRequired()])
    expiry_date = DateField('Expiry Date', validators=[Optional()])
    price_per_unit = FloatField('Price per Unit', validators=[Optional(), NumberRange(min=0)])
    pesticide_used = BooleanField('Pesticides Used')
    pesticide_details = TextAreaField('Pesticide Details', validators=[Optional()])
    description = TextAreaField('Description', validators=[Optional()])
    image = FileField('Product Image', validators=[
        Optional(), FileAllowed(['jpg', 'jpeg', 'png'], 'Only image files allowed!')
    ])

class RatingForm(FlaskForm):
    rating = SelectField('Rating', choices=[
        ('5', '5 Stars - Excellent'),
        ('4', '4 Stars - Very Good'),
        ('3', '3 Stars - Good'),
        ('2', '2 Stars - Fair'),
        ('1', '1 Star - Poor')
    ], validators=[DataRequired()])
    review = TextAreaField('Review', validators=[Optional(), Length(max=500)])

class MessageForm(FlaskForm):
    subject = StringField('Subject', validators=[DataRequired(), Length(max=200)])
    content = TextAreaField('Message', validators=[DataRequired(), Length(max=1000)])

class ProductJourneyForm(FlaskForm):
    stage = SelectField('Stage', choices=[
        ('processed', 'Processed'),
        ('shipped', 'Shipped'),
        ('retail', 'At Retail'),
        ('sold', 'Sold')
    ], validators=[DataRequired()])
    location = StringField('Location', validators=[Optional(), Length(max=200)])
    details = TextAreaField('Details', validators=[Optional()])
    handler_name = StringField('Handler Name', validators=[Optional(), Length(max=120)])
    handler_contact = StringField('Handler Contact', validators=[Optional(), Length(max=100)])
    temperature = FloatField('Temperature (°C)', validators=[Optional()])
    humidity = FloatField('Humidity (%)', validators=[Optional(), NumberRange(min=0, max=100)])
    vehicle_info = StringField('Vehicle Information', validators=[Optional(), Length(max=200)])
