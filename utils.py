import os
import qrcode
from PIL import Image
from flask import current_app
import uuid

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_qr_code(batch_id):
    """Generate QR code for a product batch"""
    try:
        # Create QR code instance
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        # Generate URL for the QR code
        qr_data = f"{current_app.config.get('BASE_URL', 'http://localhost:5000')}/scan/{batch_id}"
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Create QR code image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save the image
        filename = f"qr_{batch_id}_{uuid.uuid4().hex[:8]}.png"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        img.save(filepath)
        
        return filename
    
    except Exception as e:
        current_app.logger.error(f"Error generating QR code: {str(e)}")
        return None

def calculate_green_score(product):
    """Calculate sustainability score for a product"""
    score = 100  # Start with perfect score
    
    # Deduct points for pesticide use
    if product.pesticide_used:
        score -= 30
    
    # Bonus for organic farming
    if product.farmer.farmer_profile and product.farmer.farmer_profile.farming_type == 'organic':
        score += 10
    
    # Could add more factors like food miles, packaging, etc.
    
    return max(0, min(100, score))  # Ensure score is between 0-100

def format_currency(amount):
    """Format currency for display"""
    if amount is None:
        return "N/A"
    return f"${amount:.2f}"

def get_stage_color(stage):
    """Get color class for journey stage"""
    stage_colors = {
        'harvested': 'success',
        'processed': 'info', 
        'shipped': 'warning',
        'retail': 'primary',
        'sold': 'secondary'
    }
    return stage_colors.get(stage, 'light')

def calculate_food_miles(farmer_location, consumer_location):
    """Calculate approximate food miles (simplified)"""
    # This is a simplified calculation - in a real app you'd use a proper geocoding service
    return 50  # Mock value

def generate_mock_blockchain_hash(data):
    """Generate a mock blockchain hash for demonstration"""
    import hashlib
    return hashlib.sha256(str(data).encode()).hexdigest()
