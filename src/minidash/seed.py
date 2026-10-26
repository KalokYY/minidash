"""Seed data: 5 restaurants, each with a small menu. Prices are in cents."""

RESTAURANTS = [
    {
        "name": "Luigi's Pizzeria",
        "cuisine": "Italian",
        "opens_at": "11:00",
        "closes_at": "22:00",
        "avg_prep_minutes": 25,
        "menu": [
            ("Margherita Pizza", 1200),
            ("Pepperoni Pizza", 1400),
            ("Garlic Knots", 600),
            ("Tiramisu", 700),
        ],
    },
    {
        "name": "Sakura Sushi",
        "cuisine": "Japanese",
        "opens_at": "12:00",
        "closes_at": "21:30",
        "avg_prep_minutes": 30,
        "menu": [
            ("Salmon Nigiri (2 pc)", 800),
            ("California Roll", 900),
            ("Miso Soup", 400),
            ("Edamame", 500),
        ],
    },
    {
        "name": "Taco Fiesta",
        "cuisine": "Mexican",
        "opens_at": "10:00",
        "closes_at": "23:00",
        "avg_prep_minutes": 15,
        "menu": [
            ("Carne Asada Taco", 350),
            ("Chicken Burrito", 1000),
            ("Chips and Guacamole", 600),
            ("Horchata", 300),
        ],
    },
    {
        "name": "Spice Route",
        "cuisine": "Indian",
        "opens_at": "11:30",
        "closes_at": "22:30",
        "avg_prep_minutes": 35,
        "menu": [
            ("Chicken Tikka Masala", 1500),
            ("Vegetable Biryani", 1300),
            ("Garlic Naan", 400),
            ("Mango Lassi", 450),
        ],
    },
    {
        "name": "Burger Barn",
        "cuisine": "American",
        "opens_at": "10:30",
        "closes_at": "23:30",
        "avg_prep_minutes": 20,
        "menu": [
            ("Classic Cheeseburger", 1100),
            ("Bacon Burger", 1300),
            ("French Fries", 450),
            ("Chocolate Shake", 550),
        ],
    },
]


def seed_if_empty(conn):
    """Insert the seed data only when the restaurants table is empty."""
    count = conn.execute("SELECT COUNT(*) FROM restaurants").fetchone()[0]
    if count > 0:
        return
    for r in RESTAURANTS:
        cur = conn.execute(
            "INSERT INTO restaurants (name, cuisine, opens_at, closes_at, avg_prep_minutes) "
            "VALUES (?, ?, ?, ?, ?)",
            (r["name"], r["cuisine"], r["opens_at"], r["closes_at"], r["avg_prep_minutes"]),
        )
        restaurant_id = cur.lastrowid
        conn.executemany(
            "INSERT INTO menu_items (restaurant_id, name, price_cents) VALUES (?, ?, ?)",
            [(restaurant_id, name, price) for name, price in r["menu"]],
        )
