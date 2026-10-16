import random
import math
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timezone
from extensions import db
from models import User, HorseProfile, Match

matches_bp = Blueprint('matches', __name__, url_prefix='/matches')

# ------------------- MATCHING ALGORITHM -------------------

MATCH_WEIGHTS = {
    'same_breed': 20,
    'same_discipline': 15,
    'same_temperament': 12,
    'same_region': 10,
    'experience_compatible': 10,
    'age_compatible': 8,
    'height_compatible': 8,
    'offspring_goals': 8,
    'ideal_date_overlap': 7,
    'coat_color_appeal': 2,
}

EXPERIENCE_ORDER = ['beginner', 'intermediate', 'advanced', 'expert']

def calculate_compatibility(p1, p2):
    """Calculate a compatibility score between two horse profiles (0-100)."""
    if not p1 or not p2:
        return 0

    score = 0
    reasons = []

    # Same breed = strong connection
    if p1.breed and p2.breed and p1.breed.lower() == p2.breed.lower():
        score += MATCH_WEIGHTS['same_breed']
        reasons.append('Same breed')

    # Same riding discipline
    if p1.riding_discipline and p2.riding_discipline and p1.riding_discipline.lower() == p2.riding_discipline.lower():
        score += MATCH_WEIGHTS['same_discipline']
        reasons.append('Same discipline')

    # Same temperament
    if p1.temperament and p2.temperament and p1.temperament.lower() == p2.temperament.lower():
        score += MATCH_WEIGHTS['same_temperament']
        reasons.append('Same temperament')

    # Same stable region
    if p1.stable_region and p2.stable_region:
        r1 = p1.stable_region.lower().strip()
        r2 = p2.stable_region.lower().strip()
        if r1 == r2:
            score += MATCH_WEIGHTS['same_region']
            reasons.append('Same region')
        elif r1[:3] == r2[:3]:
            score += MATCH_WEIGHTS['same_region'] // 2
            reasons.append('Nearby region')

    # Experience compatibility (within 1 level)
    if p1.experience_level and p2.experience_level:
        try:
            l1 = EXPERIENCE_ORDER.index(p1.experience_level.lower())
            l2 = EXPERIENCE_ORDER.index(p2.experience_level.lower())
            if l1 == l2:
                score += MATCH_WEIGHTS['experience_compatible']
                reasons.append('Same experience level')
            elif abs(l1 - l2) == 1:
                score += MATCH_WEIGHTS['experience_compatible'] // 2
                reasons.append('Similar experience')
        except ValueError:
            pass

    # Age compatibility (within 5 years)
    if p1.age and p2.age:
        age_diff = abs(p1.age - p2.age)
        if age_diff <= 3:
            score += MATCH_WEIGHTS['age_compatible']
            if age_diff == 0:
                reasons.append('Same age!')
            else:
                reasons.append('Close in age')
        elif age_diff <= 7:
            score += MATCH_WEIGHTS['age_compatible'] // 2
            reasons.append('Age compatible')

    # Height compatibility (within 2 hands)
    if p1.height_hands and p2.height_hands:
        height_diff = abs(p1.height_hands - p2.height_hands)
        if height_diff <= 1.0:
            score += MATCH_WEIGHTS['height_compatible']
            reasons.append('Similar height')
        elif height_diff <= 3.0:
            score += MATCH_WEIGHTS['height_compatible'] // 2
            reasons.append('Height compatible')

    # Offspring goals alignment
    if p1.wants_offspring is not None and p2.wants_offspring is not None:
        if p1.wants_offspring == p2.wants_offspring:
            score += MATCH_WEIGHTS['offspring_goals']
            reasons.append('Shared offspring goals')

    # Ideal date overlap (keyword matching)
    if p1.ideal_date_activity and p2.ideal_date_activity:
        p1_keywords = set(p1.ideal_date_activity.lower().split(','))
        p2_keywords = set(p2.ideal_date_activity.lower().split(','))
        p1_keywords = {k.strip() for k in p1_keywords}
        p2_keywords = {k.strip() for k in p2_keywords}
        overlap = p1_keywords & p2_keywords
        if overlap:
            score += min(MATCH_WEIGHTS['ideal_date_overlap'], len(overlap) * 3)
            reasons.append(f"Date activity overlap: {', '.join(list(overlap)[:2])}")

    # Coat color appeal bonus (opposite colors attract)
    if p1.coat_color and p2.coat_color:
        if p1.coat_color.lower() != p2.coat_color.lower():
            score += MATCH_WEIGHTS['coat_color_appeal']
            reasons.append('Complementary colors')

    # Cap at 100
    final_score = min(100, score)

    return {
        'score': final_score,
        'reasons': reasons[:3],  # top 3 reasons
    }


def get_conversation_prompt(p1, p2, match_info):
    """Generate a fun icebreaker prompt for the matched pair."""
    prompts = [
        f"🐴 {p1.display_name} and {p2.display_name} both love {p1.riding_discipline or 'trail riding'}! "
        f"Ask each other about your best ride ever!",

        f"☕ Since you're both in the {p1.stable_region or 'same'} area — "
        f"who has the best grazing spot nearby?",

        f"🎯 You matched {match_info['score']}%! Who wants to share their "
        f"favorite treat first? {p1.favorite_treat or 'Carrots'}? {p2.favorite_treat or 'Apples'}?",

        f"🌅 {p1.display_name} {'wants' if p1.wants_offspring else 'isn\'t looking for'} foals "
        f"and {p2.display_name} {'wants' if p2.wants_offspring else 'isn\'t looking for'} foals. "
        f"Great starting point for a conversation!",

        f"🏆 Both {p1.breed or 'horse'} lovers! What's the one thing about "
        f"{p1.breed or 'your breed'} that nobody understands?",

        f"🎠 {p1.temperament or 'Gentle'} meets {p2.temperament or 'Spirited'}! "
        f"Opposite temperaments often make the best trail buddies. What's your dream ride?",
    ]

    if 'Same breed' in match_info.get('reasons', []):
        return prompts[4]
    if 'Same discipline' in match_info.get('reasons', []):
        return prompts[0]
    if match_info.get('score', 0) > 75:
        return f"⚡ {match_info['score']}% match — that's almost unheard of! "
               f"What drew you to {p1.display_name}'s profile?"

    return random.choice(prompts)


# ------------------- ROUTES -------------------


@matches_bp.route('/browse')
@login_required
def browse():
    profile = HorseProfile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        return redirect(url_for('profiles.create_profile'))

    # Get already matched/rejected user IDs
    interacted = Match.query.filter(
        (Match.user1_id == current_user.id) | (Match.user2_id == current_user.id)
    ).all()

    excluded_ids = {current_user.id}
    for m in interacted:
        excluded_ids.add(m.user1_id)
        excluded_ids.add(m.user2_id)

    # Get candidates with profiles
    candidates = User.query.filter(
        ~User.id.in_(excluded_ids),
        User.id != current_user.id,
        User.horse_profile.has(HorseProfile.id.isnot(None))
    ).all()

    # Score all candidates
    scored = []
    for candidate in candidates:
        if candidate.horse_profile:
            result = calculate_compatibility(profile, candidate.horse_profile)
            scored.append((result['score'], candidate, result['reasons']))

    # Sort by score descending
    scored.sort(key=lambda x: x[0], reverse=True)

    page = request.args.get('page', 1, type=int)
    per_page = 1
    total = len(scored)
    total_pages = max(1, math.ceil(total / per_page))

    if scored:
        offset = (page - 1) * per_page
        if offset < total:
            current_score, current_candidate, current_reasons = scored[offset]
            match_result = {
                'score': current_score,
                'reasons': current_reasons,
            }
            return render_template('browse.html',
                                   candidate=current_candidate,
                                   match_result=match_result,
                                   page=page,
                                   total_pages=total_pages,
                                   total=total)
        else:
            flash("You've seen everyone! Check back later for new faces.", 'info')
            return render_template('browse.html',
                                   candidate=None,
                                   match_result=None,
                                   page=page,
                                   total_pages=total_pages,
                                   total=total)

    flash("No new horses to show right now. Check back soon!", 'info')
    return render_template('browse.html',
                           candidate=None,
                           match_result=None,
                           page=1,
                           total_pages=1,
                           total=0)


@matches_bp.route('/swipe/<int:target_id>/<action>', methods=['POST'])
@login_required
def swipe(target_id, action):
    if target_id == current_user.id:
        return jsonify({'error': "Can't match with yourself"}), 400

    profile = HorseProfile.query.filter_by(user_id=current_user.id).first()
    target_profile = HorseProfile.query.filter_by(user_id=target_id).first()
    if not profile or not target_profile:
        return jsonify({'error': 'Profile not found'}), 404

    existing = Match.query.filter(
        ((Match.user1_id == current_user.id) & (Match.user2_id == target_id)) |
        ((Match.user1_id == target_id) & (Match.user2_id == current_user.id))
    ).first()

    if existing:
        if action == 'like' and existing.status == 'pending':
            # Check if other user already liked this user
            reverse = Match.query.filter(
                Match.user1_id == target_id,
                Match.user2_id == current_user.id,
                Match.status == 'pending'
            ).first()
            if reverse:
                reverse.status = 'matched'
                reverse.matched_at = datetime.now(timezone.utc)
                match_info = calculate_compatibility(profile, target_profile)
                reverse.conversation_prompt = get_conversation_prompt(profile, target_profile, match_info)
                db.session.commit()
                return jsonify({'matched': True, 'prompt': reverse.conversation_prompt})
        existing.status = 'liked' if action == 'like' else 'rejected'
        db.session.commit()
        return jsonify({'status': 'updated'})

    match_info = calculate_compatibility(profile, target_profile)
    conv_prompt = get_conversation_prompt(profile, target_profile, match_info)

    match = Match(
        user1_id=current_user.id,
        user2_id=target_id,
        score=match_info['score'],
        status='pending',
        conversation_prompt=conv_prompt,
    )

    db.session.add(match)

    # Check mutual like
    reverse = Match.query.filter(
        Match.user1_id == target_id,
        Match.user2_id == current_user.id,
        Match.status == 'pending'
    ).first()

    if reverse and action == 'like':
        match.status = 'matched'
        match.matched_at = datetime.now(timezone.utc)
        reverse.status = 'matched'
        reverse.matched_at = datetime.now(timezone.utc)
        reverse.conversation_prompt = conv_prompt
        db.session.commit()
        return jsonify({'matched': True, 'prompt': conv_prompt})

    db.session.commit()
    return jsonify({'status': 'pending', 'score': match_info['score']})


@matches_bp.route('/my-matches')
@login_required
def my_matches():
    matches = Match.query.filter(
        ((Match.user1_id == current_user.id) | (Match.user2_id == current_user.id)),
        Match.status == 'matched'
    ).order_by(Match.matched_at.desc()).all()

    matched_profiles = []
    for m in matches:
        other_user_id = m.user2_id if m.user1_id == current_user.id else m.user1_id
        other_user = User.query.get(other_user_id)
        if other_user and other_user.horse_profile:
            matched_profiles.append({
                'match': m,
                'user': other_user,
                'profile': other_user.horse_profile,
            })

    return render_template('my_matches.html', matches=matched_profiles)
