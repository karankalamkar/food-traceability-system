import os
from flask import render_template, request, redirect, url_for, flash, jsonify, current_app, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime, date
from app import app, db
from models import User, FarmerProfile, Product, ProductJourney, Rating, Message, Transaction
from forms import RegistrationForm, LoginForm, FarmerProfileForm, ProductForm, RatingForm, MessageForm, ProductJourneyForm
from utils import generate_qr_code, allowed_file
import logging

@app.route('/')
def index():
    # Get featured products for the marketplace
    featured_products = Product.query.filter_by(status='available').limit(6).all()
    return render_template('index.html', featured_products=featured_products)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if user already exists
        existing_user = User.query.filter((User.username == form.username.data) | (User.email == form.email.data)).first()
        if existing_user:
            flash('Username or email already exists. Please choose a different one.', 'danger')
            return render_template('register.html', form=form)
        
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data,
            role=form.role.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash(f'Welcome back, {user.username}!', 'success')
            
            # Redirect to role-specific dashboard
            if user.role == 'farmer':
                return redirect(url_for('farmer_dashboard'))
            elif user.role == 'consumer':
                return redirect(url_for('consumer_dashboard'))
            elif user.role == 'processor':
                return redirect(url_for('processor_dashboard'))
            elif user.role == 'retailer':
                return redirect(url_for('retailer_dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/farmer/dashboard')
@login_required
def farmer_dashboard():
    if current_user.role != 'farmer':
        flash('Access denied. Farmers only.', 'danger')
        return redirect(url_for('index'))
    
    # Get farmer's products and stats
    products = Product.query.filter_by(farmer_id=current_user.id).all()
    total_products = len(products)
    total_revenue = sum(p.price_per_unit * p.quantity for p in products if p.price_per_unit and p.status == 'sold')
    avg_rating = 0
    if products:
        all_ratings = [r for p in products for r in p.ratings]
        if all_ratings:
            avg_rating = sum(r.rating for r in all_ratings) / len(all_ratings)
    
    return render_template('farmer_dashboard.html', 
                         products=products, 
                         total_products=total_products,
                         total_revenue=total_revenue,
                         avg_rating=round(avg_rating, 1))

@app.route('/consumer/dashboard')
@login_required
def consumer_dashboard():
    if current_user.role != 'consumer':
        flash('Access denied. Consumers only.', 'danger')
        return redirect(url_for('index'))
    
    # Get consumer's recent activities
    recent_ratings = Rating.query.filter_by(user_id=current_user.id).order_by(Rating.created_at.desc()).limit(5).all()
    recent_transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.created_at.desc()).limit(5).all()
    
    return render_template('consumer_dashboard.html', 
                         recent_ratings=recent_ratings,
                         recent_transactions=recent_transactions)

@app.route('/processor/dashboard')
@login_required
def processor_dashboard():
    if current_user.role != 'processor':
        flash('Access denied. Processors only.', 'danger')
        return redirect(url_for('index'))
    
    # Get products that need processing
    available_products = Product.query.filter_by(status='available').all()
    processed_products = ProductJourney.query.filter_by(stage='processed', created_by=current_user.id).all()
    
    return render_template('processor_dashboard.html', 
                         available_products=available_products,
                         processed_products=processed_products)

@app.route('/retailer/dashboard')
@login_required
def retailer_dashboard():
    if current_user.role != 'retailer':
        flash('Access denied. Retailers only.', 'danger')
        return redirect(url_for('index'))
    
    # Get products in retail
    retail_products = ProductJourney.query.filter_by(stage='retail', created_by=current_user.id).all()
    
    return render_template('retailer_dashboard.html', retail_products=retail_products)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if current_user.role == 'farmer':
        form = FarmerProfileForm()
        farmer_profile = current_user.farmer_profile
        
        if request.method == 'GET' and farmer_profile:
            # Pre-populate form with existing data
            form.farm_name.data = farmer_profile.farm_name
            form.location.data = farmer_profile.location
            form.farm_size.data = farmer_profile.farm_size
            form.farming_type.data = farmer_profile.farming_type
            form.certification.data = farmer_profile.certification
            form.description.data = farmer_profile.description
            form.phone.data = farmer_profile.phone
            form.latitude.data = farmer_profile.latitude
            form.longitude.data = farmer_profile.longitude
            form.established_year.data = farmer_profile.established_year
        
        if form.validate_on_submit():
            if not farmer_profile:
                farmer_profile = FarmerProfile(user_id=current_user.id)
                db.session.add(farmer_profile)
            
            farmer_profile.farm_name = form.farm_name.data
            farmer_profile.location = form.location.data
            farmer_profile.farm_size = form.farm_size.data
            farmer_profile.farming_type = form.farming_type.data
            farmer_profile.certification = form.certification.data
            farmer_profile.description = form.description.data
            farmer_profile.phone = form.phone.data
            farmer_profile.latitude = form.latitude.data
            farmer_profile.longitude = form.longitude.data
            farmer_profile.established_year = form.established_year.data
            
            # Handle file upload
            if form.certification_file.data:
                file = form.certification_file.data
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filename = f"cert_{current_user.id}_{filename}"
                    file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                    farmer_profile.certification_file = filename
            
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('profile'))
        
        return render_template('profile.html', form=form, farmer_profile=farmer_profile)
    
    return render_template('profile.html')

@app.route('/product/new', methods=['GET', 'POST'])
@login_required
def new_product():
    if current_user.role != 'farmer':
        flash('Access denied. Farmers only.', 'danger')
        return redirect(url_for('index'))
    
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(
            farmer_id=current_user.id,
            name=form.name.data,
            category=form.category.data,
            variety=form.variety.data,
            quantity=form.quantity.data,
            unit=form.unit.data,
            harvest_date=form.harvest_date.data,
            expiry_date=form.expiry_date.data,
            price_per_unit=form.price_per_unit.data,
            pesticide_used=form.pesticide_used.data,
            pesticide_details=form.pesticide_details.data,
            description=form.description.data
        )
        
        db.session.add(product)
        db.session.flush()  # Get the product ID
        
        # Handle image upload
        if form.image.data:
            file = form.image.data
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename = f"product_{product.id}_{filename}"
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                product.image_path = filename
        
        # Generate QR code
        qr_filename = generate_qr_code(product.batch_id)
        product.qr_code_path = qr_filename
        
        # Create initial journey entry
        journey = ProductJourney(
            product_id=product.id,
            stage='harvested',
            location=current_user.farmer_profile.location if current_user.farmer_profile else 'Farm',
            details='Product harvested and added to system',
            handler_name=current_user.username,
            created_by=current_user.id
        )
        db.session.add(journey)
        
        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('farmer_dashboard'))
    
    return render_template('product_form.html', form=form)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    ratings = Rating.query.filter_by(product_id=product_id).order_by(Rating.created_at.desc()).all()
    return render_template('product_detail.html', product=product, ratings=ratings)

@app.route('/product/<int:product_id>/journey')
def product_journey(product_id):
    product = Product.query.get_or_404(product_id)
    journey_steps = ProductJourney.query.filter_by(product_id=product_id).order_by(ProductJourney.timestamp).all()
    return render_template('product_journey.html', product=product, journey_steps=journey_steps)

@app.route('/product/<int:product_id>/rate', methods=['POST'])
@login_required
def rate_product(product_id):
    if current_user.role != 'consumer':
        flash('Only consumers can rate products.', 'danger')
        return redirect(url_for('product_detail', product_id=product_id))
    
    form = RatingForm()
    if form.validate_on_submit():
        # Check if user already rated this product
        existing_rating = Rating.query.filter_by(user_id=current_user.id, product_id=product_id).first()
        if existing_rating:
            existing_rating.rating = int(form.rating.data)
            existing_rating.review = form.review.data
            flash('Your rating has been updated!', 'success')
        else:
            rating = Rating(
                user_id=current_user.id,
                product_id=product_id,
                rating=int(form.rating.data),
                review=form.review.data
            )
            db.session.add(rating)
            flash('Thank you for your rating!', 'success')
        
        db.session.commit()
    
    return redirect(url_for('product_detail', product_id=product_id))

@app.route('/qr-scanner')
def qr_scanner():
    return render_template('qr_scanner.html')

@app.route('/scan/<batch_id>')
def scan_result(batch_id):
    product = Product.query.filter_by(batch_id=batch_id).first()
    if not product:
        flash('Product not found. Invalid QR code.', 'danger')
        return redirect(url_for('qr_scanner'))
    
    return redirect(url_for('product_journey', product_id=product.id))

@app.route('/marketplace')
def marketplace():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    
    query = Product.query.filter_by(status='available')
    
    if category:
        query = query.filter_by(category=category)
    
    if search:
        query = query.filter(Product.name.contains(search) | Product.description.contains(search))
    
    products = query.paginate(page=page, per_page=12, error_out=False)
    
    categories = db.session.query(Product.category).distinct().all()
    categories = [cat[0] for cat in categories]
    
    return render_template('marketplace.html', products=products, categories=categories, 
                         current_category=category, search_term=search)

@app.route('/product/<int:product_id>/update-journey', methods=['POST'])
@login_required
def update_journey(product_id):
    if current_user.role not in ['processor', 'retailer']:
        flash('Access denied.', 'danger')
        return redirect(url_for('product_detail', product_id=product_id))
    
    form = ProductJourneyForm()
    if form.validate_on_submit():
        journey = ProductJourney(
            product_id=product_id,
            stage=form.stage.data,
            location=form.location.data,
            details=form.details.data,
            handler_name=form.handler_name.data,
            handler_contact=form.handler_contact.data,
            temperature=form.temperature.data,
            humidity=form.humidity.data,
            vehicle_info=form.vehicle_info.data,
            created_by=current_user.id
        )
        
        # Update product grade if processor
        if current_user.role == 'processor' and form.stage.data == 'processed':
            product = Product.query.get(product_id)
            # Simple grading logic (could be enhanced with AI)
            if product.pesticide_used:
                product.grade = 'B1'
            else:
                product.grade = 'A1'
        
        db.session.add(journey)
        db.session.commit()
        flash('Journey updated successfully!', 'success')
    
    return redirect(url_for('product_journey', product_id=product_id))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
