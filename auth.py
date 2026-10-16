from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from authlib.integrations.flask_client import OAuth
from urllib.parse import urlencode
from extensions import db
from models import User, HorseProfile
from config import Config
import requests
import json

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
oauth = OAuth()

google = oauth.register(
    name='google',
    client_id=Config.GOOGLE_CLIENT_ID,
    client_secret=Config.GOOGLE_CLIENT_SECRET,
    access_token_url='https://oauth2.googleapis.com/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    client_kwargs={'scope': 'openid email profile'},
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.horse_profile:
            return redirect(url_for('matches.browse'))
        return redirect(url_for('profiles.create_profile'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Welcome back!', 'success')
            if user.horse_profile:
                return redirect(url_for('matches.browse'))
            return redirect(url_for('profiles.create_profile'))
        flash('Invalid email or password', 'error')

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        if current_user.horse_profile:
            return redirect(url_for('matches.browse'))
        return redirect(url_for('profiles.create_profile'))

    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')

        if password != confirm:
            flash('Passwords do not match', 'error')
            return render_template('register.html')

        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('register.html')

        if User.query.filter_by(username=username).first():
            flash('Username already taken', 'error')
            return render_template('register.html')

        if len(password) < 8:
            flash('Password must be at least 8 characters', 'error')
            return render_template('register.html')

        user = User(email=email, username=username, auth_provider='local')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash('Account created! Now set up your horse profile.', 'success')
        return redirect(url_for('profiles.create_profile'))

    return render_template('register.html')


@auth_bp.route('/google-login')
def google_login():
    if Config.GOOGLE_CLIENT_ID and Config.GOOGLE_CLIENT_ID != 'your-google-client-id':
        redirect_uri = url_for('auth.google_callback', _external=True)
        return oauth.google.authorize_redirect(redirect_uri)
    else:
        flash('Google login is not configured. Use email/password registration.', 'warning')
        return redirect(url_for('auth.login'))


@auth_bp.route('/google/callback')
def google_callback():
    try:
        token = oauth.google.authorize_access_token()
        resp = oauth.google.get('https://www.googleapis.com/oauth2/v2/userinfo')
        user_info = resp.json()
        email = user_info['email']
        google_id = user_info['id']
        name = user_info.get('name', email.split('@')[0])

        user = User.query.filter_by(auth_provider='google', auth_provider_id=google_id).first()
        if not user:
            user = User.query.filter_by(email=email).first()
            if user:
                user.auth_provider = 'google'
                user.auth_provider_id = google_id
            else:
                user = User(
                    email=email,
                    username=name.replace(' ', '_').lower()[:80],
                    auth_provider='google',
                    auth_provider_id=google_id,
                )
                db.session.add(user)
            db.session.commit()

        login_user(user)
        flash(f'Welcome, {name}!', 'success')
        if user.horse_profile:
            return redirect(url_for('matches.browse'))
        return redirect(url_for('profiles.create_profile'))
    except Exception as e:
        flash(f'Google login failed: {str(e)}', 'error')
        return redirect(url_for('auth.login'))


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
