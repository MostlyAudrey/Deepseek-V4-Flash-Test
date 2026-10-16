"""
Seed database with 50 horse profiles so the platform looks populated.
Pulls images from horse image sources on the web.
"""
import random
import uuid
import sys
import requests
from datetime import datetime, timezone

# Add parent to path
sys.path.insert(0, '.')

from app import create_app
from extensions import db
from models import User, HorseProfile

app = create_app()

# Horse names (realistic horse names)
HORSE_NAMES = [
    "Midnight Storm", "Golden Breeze", "Shadow Dancer", "Silver Comet", "Chestnut Prince",
    "Whispering Wind", "Royal Thunder", "Dancing Star", "Brave Heart", "Velvet Sunset",
    "Rising Phoenix", "Crimson Tide", "Gentle Giant", "Starlight Express", "Thunder Hooves",
    "Sapphire Moon", "Copper King", "Amber Dawn", "Iron Will", "Silk Mane",
    "Wild Mustang", "Autumn Blaze", "Frost Walker", "Canyon Echo", "Prairie Song",
    "Golden Glory", "Midnight Shadow", "Valiant Spirit", "Sweet Melody", "Desert Rose",
    "Noble Quest", "Diamond Dust", "Crystal Creek", "Storm Chaser", "Mystic Dream",
    "Painted Sky", "River Dance", "Mountain Breeze", "Oakley Star", "Moonlit Meadow",
    "Running Free", "Ebony Night", "Sunlight Ray", "Prairie Fire", "Ocean Wave",
    "Golden Sunset", "Dark Beauty", "Silver Wind", "Crimson Glory", "Azure Sky",
]

HORSE_SURNAMES = [
    "of Windfall Ranch", "from Whispering Pines", "of Cedar Creek", "from Golden Valley",
    "of Shadow Brook", "from Rising Sun Farm", "of the Green Pastures", "from Silver Lake",
    "of the Rolling Hills", "from Meadow Brook", "", "", "", "", "",
]

BREEDS = [
    "Thoroughbred", "Quarter Horse", "Arabian", "Appaloosa", "Paint Horse",
    "Morgan", "Tennessee Walker", "Andalusian", "Friesian", "Clydesdale",
    "Mustang", "Percheron", "Warmblood", "Standardbred", "Miniature Horse",
    "Haflinger", "Icelandic", "Shetland Pony", "Connemara", "Gypsy Vanner",
]

COAT_COLORS = ["Bay", "Chestnut", "Black", "Gray", "Palomino", "Buckskin", "Roan", "Dun", "Appaloosa", "Pinto", "Sorrel", "Cremello", "Perlino", "White"]

MARKINGS_OPTIONS = ["Star", "Blaze", "Snip", "Stripe", "Socks", "Stockings", "Pastern", "Coronet", "Half Pastern", "None", "Star + Snip", "Blaze + Socks"]

GENDERS = ["mare", "stallion", "gelding"]

RIDING_DISCIPLINES = ["dressage", "jumping", "eventing", "western", "trail", "endurance", "racing", "barrel", "driving"]

EXPERIENCE_LEVELS = ["beginner", "intermediate", "advanced", "expert"]

TEMPERAMENTS = ["calm", "gentle", "eager", "spirited", "playful", "independent"]

REGIONS = [
    "Kentucky", "Ireland", "California", "Texas", "Virginia",
    "New York", "Florida", "Colorado", "Oregon", "Montana",
    "United Kingdom", "Australia", "Germany", "France", "New Zealand",
    "Canada", "Illinois", "Washington", "Pennsylvania", "Arizona",
]

TREATS = ["Carrots", "Apples", "Sugar cubes", "Peppermints", "Watermelon", "Bananas", "Hay cubes", "Alfalfa", "Molasses treats", "Sweet feed"]

DATE_ACTIVITIES = [
    "Trail ride through the forest", "Pasture grazing at sunset",
    "Arena work and training", "Beach gallop",
    "Cross-country jumping", "Dressage practice",
    "Mountain trail adventure", "River crossing ride",
    "Overnight camping trip", "Show preparation",
    "Casual hack through the countryside", "Barn socializing",
    "Paddock playtime", "Long trail ride",
    "Liberty work in the round pen",
]

BIO_TEMPLATES = [
    "I'm a {temperament} {breed} who loves {discipline}. Looking for a partner to share trail rides and quiet evenings in the pasture with.",
    "Sassy {gender} looking for a fellow horse who can keep up! I excel at {discipline} and love {activity}. Treats are the way to my heart.",
    "Gentle soul here. I enjoy long trail rides, sunsets in the pasture, and the occasional sugar cube. Looking for a meaningful connection.",
    "Competitive {breed} with {experience} experience. When I'm not training for {discipline}, you'll find me grazing and enjoying the view.",
    "Easy-going {temperament} mare/stallion looking for my other half. I believe the best relationships start with a good gallop together.",
    "{temperament|title} and {experience} level. Love exploring new trails and making new friends. Bonus points if you bring carrots.",
    "Show horse by day, romantic at heart. Looking for someone who understands the thrill of {discipline} and the peace of a quiet stable night.",
    "Just a {coat_color} {breed} looking for love in all the right pastures. I'm told I have a great mane and an even better personality.",
    "Life is better with someone to share it with. I love {activity} and dream of finding a partner who values trust and companionship.",
    "Retired racehorse seeking a slower pace of life with the right partner. I enjoy long walks, good food, and meaningful conversations.",
]

PASSWORD = "horselover123"  # common seed password


def generate_seed_names():
    """Generate display names from the lists."""
    names = []
    for name in HORSE_NAMES:
        surname = random.choice(HORSE_SURNAMES)
        if surname:
            display = f"{name} {surname}"
        else:
            display = name
        names.append(display)
    return names


def get_horse_images():
    """Fetch horse images from public sources."""
    images = []
    sources = [
        # Direct image URLs from various horse photography sources
        "https://images.unsplash.com/photo-1553284965-83fd3e82ef5a?w=600",
        "https://images.unsplash.com/photo-1553284965-9b6eb9b03b8b?w=600",
        "https://images.unsplash.com/photo-1534773718119-7cfa4e63f7a0?w=600",
        "https://images.unsplash.com/photo-1603974374968-8251f2163f0a?w=600",
        "https://images.unsplash.com/photo-1512758017271-d7b84c2113f1?w=600",
        "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=600",
        "https://images.unsplash.com/photo-1553284965-83fd3e82ef5a?w=600",
        "https://images.unsplash.com/photo-1566321323640-e5b5a0f1d6b9?w=600",
        "https://images.unsplash.com/photo-1570372325884-5c5b36e5e8f1?w=600",
        "https://images.unsplash.com/photo-1581023698737-3f1f5b7fc06f?w=600",
        "https://images.unsplash.com/photo-1550355291-b1e8f0e8c1e6?w=600",
        "https://images.unsplash.com/photo-1534773718119-7cfa4e63f7a0?w=600",
        "https://images.unsplash.com/photo-1572789670332-26f3f0c4df26?w=600",
        "https://images.unsplash.com/photo-1572783306140-8baf8f5a8c0a?w=600",
        "https://images.unsplash.com/photo-1598033129183-c4f50c736c10?w=600",
        "https://images.unsplash.com/photo-1569321631549-f6e3f3a7b187?w=600",
        "https://images.unsplash.com/photo-1590234782349-6b23af9be4b4?w=600",
        "https://images.unsplash.com/photo-1599791448902-65a9fcfaf35f?w=600",
        "https://images.unsplash.com/photo-1583478731447-6afcbc9c0f8c?w=600",
        "https://images.unsplash.com/photo-1550355291-c5b1f8e0e8c6?w=600",
        "https://images.unsplash.com/photo-1598033129183-c4f50c736c10?w=600",
        "https://images.unsplash.com/photo-1590234782349-6b23af9be4b4?w=600",
        "https://images.unsplash.com/photo-1566321323640-e5b5a0f1d6b9?w=600",
        "https://images.unsplash.com/photo-1512758017271-d7b84c2113f1?w=600",
        "https://images.unsplash.com/photo-1534773718119-7cfa4e63f7a0?w=600",
        "https://images.unsplash.com/photo-1603974374968-8251f2163f0a?w=600",
        "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=600",
        "https://images.unsplash.com/photo-1572789670332-26f3f0c4df26?w=600",
        "https://images.unsplash.com/photo-1598033129183-c4f50c736c10?w=600",
        "https://images.unsplash.com/photo-1590234782349-6b23af9be4b4?w=600",
        "https://images.unsplash.com/photo-1566321323640-e5b5a0f1d6b9?w=600",
        "https://images.unsplash.com/photo-1583478731447-6afcbc9c0f8c?w=600",
        "https://images.unsplash.com/photo-1569321631549-f6e3f3a7b187?w=600",
        "https://images.unsplash.com/photo-1599791448902-65a9fcfaf35f?w=600",
        "https://images.unsplash.com/photo-1572783306140-8baf8f5a8c0a?w=600",
        "https://images.unsplash.com/photo-1572789670332-26f3f0c4df26?w=600",
        "https://images.unsplash.com/photo-1599791448902-65a9fcfaf35f?w=600",
        "https://images.unsplash.com/photo-1550355291-b1e8f0e8c1e6?w=600",
        "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=600",
        "https://images.unsplash.com/photo-1553284965-83fd3e82ef5a?w=600",
        "https://images.unsplash.com/photo-1553284965-9b6eb9b03b8b?w=600",
        "https://images.unsplash.com/photo-1603974374968-8251f2163f0a?w=600",
        "https://images.unsplash.com/photo-1512758017271-d7b84c2113f1?w=600",
        "https://images.unsplash.com/photo-1566321323640-e5b5a0f1d6b9?w=600",
        "https://images.unsplash.com/photo-1581023698737-3f1f5b7fc06f?w=600",
        "https://images.unsplash.com/photo-1569321631549-f6e3f3a7b187?w=600",
        "https://images.unsplash.com/photo-1598033129183-c4f50c736c10?w=600",
        "https://images.unsplash.com/photo-1590234782349-6b23af9be4b4?w=600",
        "https://images.unsplash.com/photo-1583478731447-6afcbc9c0f8c?w=600",
        "https://images.unsplash.com/photo-1599791448902-65a9fcfaf35f?w=600",
    ]
    return sources


def seed():
    with app.app_context():
        # Check if already seeded
        existing = User.query.filter(User.auth_provider == 'seed').count()
        if existing >= 50:
            print(f"Already seeded ({existing} accounts). Skipping.")
            return

        print("Generating 50 seed horse profiles...")
        display_names = generate_seed_names()
        images = get_horse_images()

        random.seed(42)  # deterministic for reproducibility

        for i in range(50):
            name = display_names[i] if i < len(display_names) else f"Seed Horse {i}"
            username = f"horse_{i}_{uuid.uuid4().hex[:6]}"
            email = f"horse{i}@pasturematch.com"
            breed = random.choice(BREEDS)
            gender = random.choice(GENDERS)
            discipline = random.choice(RIDING_DISCIPLINES)
            temperament = random.choice(TEMPERAMENTS)
            experience = random.choice(EXPERIENCE_LEVELS)
            region = random.choice(REGIONS)
            coat = random.choice(COAT_COLORS)
            age = random.randint(3, 25)
            hands = round(random.uniform(14.0, 17.3), 1)
            wants_foals = random.choice([True, False])
            markings = random.choice(MARKINGS_OPTIONS)
            treat = random.choice(TREATS)
            date_act = random.choice(DATE_ACTIVITIES)

            # Generate bio
            bio_template = random.choice(BIO_TEMPLATES)
            bio = bio_template.format(
                temperament=temperament,
                breed=breed,
                gender=gender,
                discipline=discipline,
                experience=experience,
                coat_color=coat,
                activity=date_act.lower(),
            )

            photo_url = images[i % len(images)]

            user = User(
                email=email,
                username=username,
                auth_provider='seed',
                auth_provider_id=f'seed_{i}',
            )
            user.set_password(PASSWORD)
            db.session.add(user)
            db.session.flush()

            profile = HorseProfile(
                user_id=user.id,
                display_name=name,
                bio=bio,
                photo_url=photo_url,
                age=age,
                breed=breed,
                gender=gender,
                height_hands=hands,
                experience_level=experience,
                riding_discipline=discipline,
                temperament=temperament,
                ideal_date_activity=date_act,
                stable_region=region,
                favorite_treat=treat,
                wants_offspring=wants_foals,
                coat_color=coat,
                markings=markings,
            )
            db.session.add(profile)

            if (i + 1) % 10 == 0:
                db.session.commit()
                print(f"  Seeded {i + 1}/50...")

        db.session.commit()
        print("Done! 50 seed horse profiles created.")
        print(f"Password for all seed accounts: {PASSWORD}")
        print("Log in with any email: horse0@pasturematch.com through horse49@pasturematch.com")


if __name__ == '__main__':
    seed()
