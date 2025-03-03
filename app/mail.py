from flask_mail import Mail, Message
from flask import current_app, url_for
from itsdangerous import URLSafeTimedSerializer

mail = Mail()

def send_verification_email(user_email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    token = serializer.dumps(user_email, salt='email-verification')
    
    verify_url = url_for('auth.verify_email', token=token, _external=True)
    
    msg = Message('Xác nhận đăng ký tài khoản',
                  sender='noreply@example.com',
                  recipients=[user_email])
    
    msg.body = f'''Để xác nhận email của bạn, vui lòng click vào link sau:
{verify_url}

Nếu bạn không yêu cầu xác nhận này, vui lòng bỏ qua email này.
'''
    mail.send(msg)

def send_reset_password_email(user_email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    token = serializer.dumps(user_email, salt='password-reset')
    
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    
    msg = Message('Yêu cầu đặt lại mật khẩu',
                  sender='noreply@example.com',
                  recipients=[user_email])
    
    msg.body = f'''Để đặt lại mật khẩu, vui lòng click vào link sau:
{reset_url}

Nếu bạn không yêu cầu đặt lại mật khẩu, vui lòng bỏ qua email này.
'''
    mail.send(msg) 