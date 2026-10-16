import os
from flask import Flask, redirect, url_for
from flask_login import LoginManager
from config import Config
from extensions import db, migrate, login_manager

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from models import User, HorseProfile

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    from auth import auth_bp
    from profiles import profiles_bp
    from matches import matches_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(profiles_bp)
    app.register_blueprint(matches_bp)

    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
