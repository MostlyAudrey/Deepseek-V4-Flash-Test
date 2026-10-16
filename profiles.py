from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from extensions import db
from models import User, HorseProfile

profiles_bp = Blueprint('profiles', __name__, url_prefix='/profile')


@profiles_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_profile():
    if current_user.horse_profile:
        return redirect(url_for('profiles.edit_profile'))

    if request.method == 'POST':
        profile = HorseProfile(
            user_id=current_user.id,
            display_name=request.form.get('display_name'),
            bio=request.form.get('bio'),
            photo_url=request.form.get('photo_url'),
            age=request.form.get('age', type=int),
            breed=request.form.get('breed'),
            gender=request.form.get('gender'),
            height_hands=request.form.get('height_hands', type=float),
            experience_level=request.form.get('experience_level'),
            riding_discipline=request.form.get('riding_discipline'),
            temperament=request.form.get('temperament'),
            ideal_date_activity=request.form.get('ideal_date_activity'),
            stable_region=request.form.get('stable_region'),
            favorite_treat=request.form.get('favorite_treat'),
            wants_offspring=bool(request.form.get('wants_offspring')),
            coat_color=request.form.get('coat_color'),
            markings=request.form.get('markings'),
        )
        db.session.add(profile)
        db.session.commit()
        flash('Your horse profile has been created! Start browsing matches.', 'success')
        return redirect(url_for('matches.browse'))

    return render_template('create_profile.html')


@profiles_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    profile = HorseProfile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        return redirect(url_for('profiles.create_profile'))

    if request.method == 'POST':
        profile.display_name = request.form.get('display_name')
        profile.bio = request.form.get('bio')
        profile.photo_url = request.form.get('photo_url')
        profile.age = request.form.get('age', type=int)
        profile.breed = request.form.get('breed')
        profile.gender = request.form.get('gender')
        profile.height_hands = request.form.get('height_hands', type=float)
        profile.experience_level = request.form.get('experience_level')
        profile.riding_discipline = request.form.get('riding_discipline')
        profile.temperament = request.form.get('temperament')
        profile.ideal_date_activity = request.form.get('ideal_date_activity')
        profile.stable_region = request.form.get('stable_region')
        profile.favorite_treat = request.form.get('favorite_treat')
        profile.wants_offspring = bool(request.form.get('wants_offspring'))
        profile.coat_color = request.form.get('coat_color')
        profile.markings = request.form.get('markings')
        db.session.commit()
        flash('Profile updated!', 'success')
        return redirect(url_for('matches.browse'))

    return render_template('create_profile.html', profile=profile)


@profiles_bp.route('/<user_id>')
@login_required
def view_profile(user_id):
    user = User.query.filter_by(public_id=user_id).first()
    if not user or not user.horse_profile:
        flash('Profile not found.', 'error')
        return redirect(url_for('matches.browse'))
    return render_template('view_profile.html', profile_user=user)
