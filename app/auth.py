from flask import Blueprint, request, jsonify, current_app, render_template
from flask_jwt_extended import create_access_token
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from .models import User
from .mail import send_verification_email, send_reset_password_email
from werkzeug.security import generate_password_hash
import logging

logger = logging.getLogger(__name__)

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - email
            - password
            - full_name
          properties:
            email:
              type: string
              example: "user@example.com"
            password:
              type: string
              example: "password123"
            full_name:
              type: string
              example: "John Doe"
    responses:
      200:
        description: User registered successfully
      400:
        description: Invalid input or email already exists
    """
    logger.info("Received registration request")
    data = request.get_json()
    logger.info(f"Registration data: {data}")
    
    try:
        # Kiểm tra dữ liệu đầu vào
        required_fields = ['email', 'password', 'full_name']
        for field in required_fields:
            if field not in data or not data[field].strip():
                logger.warning(f"Missing required field: {field}")
                return jsonify({'message': f'Vui lòng điền {field}'}), 400
        
        # Kiểm tra email đã tồn tại
        existing_user = User.find_by_email(data['email'])
        if existing_user:
            logger.warning(f"Email already exists: {data['email']}")
            return jsonify({'message': 'Email đã tồn tại'}), 400
            
        # Tạo user mới
        user = User(
            email=data['email'],
            full_name=data['full_name']
        )
        user.set_password(data['password'])
        user.save()
        logger.info(f"New user created: {data['email']}")
        
        # Gửi email xác nhận
        send_verification_email(user.email)
        logger.info(f"Verification email sent to: {data['email']}")
        
        return jsonify({
            'message': 'Đăng ký thành công. Vui lòng kiểm tra email để xác nhận tài khoản',
            'user': {
                'email': user.email,
                'full_name': user.full_name
            }
        }), 200
    except Exception as e:
        logger.error(f"Error during registration: {str(e)}")
        return jsonify({'message': 'Đã xảy ra lỗi'}), 500

@auth.route('/verify-email/<token>')
def verify_email(token):
    """
    Verify email address
    ---
    tags:
      - Authentication
    parameters:
      - in: path
        name: token
        required: true
        type: string
    responses:
      200:
        description: Email verified successfully
      400:
        description: Invalid or expired token
    """
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='email-verification', max_age=3600)
        user = User.find_by_email(email)
        if user:
            User.update_active_status(email, True)
            return jsonify({'message': 'Email đã được xác nhận'}), 200
    except SignatureExpired:
        return jsonify({'message': 'Token đã hết hạn'}), 400
    except:
        return jsonify({'message': 'Token không hợp lệ'}), 400

@auth.route('/login', methods=['POST'])
def login():
    """
    Login user
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
            password:
              type: string
    responses:
      200:
        description: Login successful
      401:
        description: Invalid credentials
    """
    logger.info("Received login request")
    data = request.get_json()
    logger.info(f"Login attempt for email: {data.get('email')}")
    
    try:
        user = User.find_by_email(data['email'])
        if user and user.check_password(data['password']):
            if not user.is_active:
                logger.warning(f"Inactive user attempted login: {data['email']}")
                return jsonify({'message': 'Vui lòng xác nhận email trước khi đăng nhập'}), 401
            
            access_token = create_access_token(identity=str(user.email))
            logger.info(f"Successful login for user: {data['email']}")
            return jsonify({
                'access_token': access_token,
                'user': {
                    'email': user.email,
                    'full_name': user.full_name,
                    'role': user.role
                }
            }), 200
            
        logger.warning(f"Failed login attempt for email: {data['email']}")
        return jsonify({'message': 'Email hoặc mật khẩu không đúng'}), 401
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        return jsonify({'message': 'Đã xảy ra lỗi'}), 500

@auth.route('/forgot-password', methods=['POST'])
def forgot_password():
    """
    Request password reset
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - email
          properties:
            email:
              type: string
    responses:
      200:
        description: Reset email sent
      404:
        description: User not found
    """
    data = request.get_json()
    user = User.find_by_email(data['email'])
    
    if not user:
        return jsonify({'message': 'Email không tồn tại'}), 404
        
    send_reset_password_email(user.email)
    return jsonify({'message': 'Email đặt lại mật khẩu đã được gửi'}), 200

@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """
    Reset password with token
    ---
    tags:
      - Authentication
    parameters:
      - in: path
        name: token
        required: true
        type: string
      - in: body
        name: body
        schema:
          type: object
          required:
            - new_password
          properties:
            new_password:
              type: string
    responses:
      200:
        description: Password reset successful
      400:
        description: Invalid or expired token
    """
    if request.method == 'GET':
        try:
            serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
            email = serializer.loads(token, salt='password-reset', max_age=3600)
            # Trả về template HTML thay vì JSON
            return render_template('reset_password.html', token=token, email=email)
        except SignatureExpired:
            return render_template('reset_password.html', error='Token đã hết hạn')
        except:
            return render_template('reset_password.html', error='Token không hợp lệ')
    
    elif request.method == 'POST':
        try:
            serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
            email = serializer.loads(token, salt='password-reset', max_age=3600)
            
            user = User.find_by_email(email)
            if not user:
                return jsonify({'message': 'Người dùng không tồn tại'}), 404
                
            data = request.get_json()
            if 'new_password' not in data:
                return jsonify({'message': 'Vui lòng nhập mật khẩu mới'}), 400
                
            user.set_password(data['new_password'])
            user.save()
            
            return jsonify({'message': 'Mật khẩu đã được đặt lại thành công'}), 200
        except SignatureExpired:
            return jsonify({'message': 'Token đã hết hạn'}), 400
        except:
            return jsonify({'message': 'Token không hợp lệ'}), 400 