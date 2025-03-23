from flask import Flask, render_template, request, jsonify
import sqlite3
import random
import os

app = Flask(__name__)

class MenuRecommendationSystem:
    def __init__(self, db_path='restaurant.db'):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.setup_database()
        self.insert_sample_data()
    
    def setup_database(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS menu_items (
            item_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT,
            spicy_level INTEGER,
            is_vegetarian BOOLEAN,
            is_vegan BOOLEAN,
            calories INTEGER,
            image_url TEXT
        )''')
        self.conn.commit()
    
    def insert_sample_data(self):
        # Check if data already exists
        self.cursor.execute("SELECT COUNT(*) FROM menu_items")
        if self.cursor.fetchone()[0] > 0:
            return
            
        # Sample menu items
        items = [
            (1, "Grilled Salmon", "Main", 22.99, "Fresh salmon fillet grilled to perfection with herbs", 1, 0, 0, 420, "/static/images/salmon.jpg"),
            (2, "Veggie Burger", "Main", 14.99, "Plant-based patty with lettuce, tomato, and special sauce", 2, 1, 1, 380, "/static/images/veggie-burger.jpg"),
            (3, "Chocolate Cake", "Dessert", 8.99, "Rich chocolate cake with ganache", 0, 1, 0, 450, "/static/images/chocolate-cake.jpg"),
            (4, "Spicy Pad Thai", "Main", 16.99, "Traditional Thai noodles with peanuts and lime", 4, 0, 0, 520, "/static/images/pad-thai.jpg"),
            (5, "Caesar Salad", "Appetizer", 9.99, "Crisp romaine lettuce with parmesan and croutons", 0, 1, 0, 320, "/static/images/caesar-salad.jpg"),
            (6, "Veggie Spring Rolls", "Appetizer", 7.99, "Fresh vegetables wrapped in rice paper", 1, 1, 1, 250, "/static/images/spring-rolls.jpg"),
            (7, "Fiery Chicken Wings", "Appetizer", 12.99, "Wings tossed in our signature hot sauce", 5, 0, 0, 480, "/static/images/wings.jpg"),
            (8, "Vegan Ice Cream", "Dessert", 6.99, "Coconut-based ice cream with fresh berries", 0, 1, 1, 280, "/static/images/vegan-ice-cream.jpg"),
            (9, "Mushroom Risotto", "Main", 18.99, "Creamy arborio rice with wild mushrooms", 0, 1, 0, 520, "/static/images/risotto.jpg"),
            (10, "Tiramisu", "Dessert", 9.99, "Classic Italian dessert with coffee and mascarpone", 0, 1, 0, 380, "/static/images/tiramisu.jpg")
        ]
        
        self.cursor.executemany('''
        INSERT OR IGNORE INTO menu_items (item_id, name, category, price, description, spicy_level, is_vegetarian, is_vegan, calories, image_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', items)
        self.conn.commit()
    
    def get_recommendations(self, category, vegetarian, vegan, max_spicy, limit=6):
        query = "SELECT * FROM menu_items WHERE 1=1"
        params = []
        if category != "Any":
            query += " AND category = ?"
            params.append(category)
        if vegetarian:
            query += " AND is_vegetarian = 1"
        if vegan:
            query += " AND is_vegan = 1"
        query += " AND spicy_level <= ?"
        params.append(max_spicy)
        
        # Create a connection and cursor for this query (thread safety)
        conn = sqlite3.connect('restaurant.db')
        cursor = conn.cursor()
        cursor.execute(query, params)
        items = cursor.fetchall()
        conn.close()
        
        return random.sample(items, min(len(items), limit)) if items else []

# Initialize database on startup
def initialize_database():
    if not os.path.exists('restaurant.db'):
        MenuRecommendationSystem()

# Use with_appcontext instead of before_first_request
with app.app_context():
    initialize_database()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    data = request.json
    category = data.get('category', 'Any')
    vegetarian = data.get('vegetarian', False)
    vegan = data.get('vegan', False)
    max_spicy = int(data.get('maxSpicy', 3))
    
    system = MenuRecommendationSystem()
    recommendations = system.get_recommendations(category, vegetarian, vegan, max_spicy)
    
    result = []
    for item in recommendations:
        # Make sure we handle items with potentially missing fields safely
        item_dict = {
            'id': item[0] if len(item) > 0 else None,
            'name': item[1] if len(item) > 1 else "Unknown Item",
            'category': item[2] if len(item) > 2 else "Uncategorized",
            'price': item[3] if len(item) > 3 else 0.0,
            'description': item[4] if len(item) > 4 else "",
            'spicyLevel': item[5] if len(item) > 5 else 0,
            'isVegetarian': bool(item[6]) if len(item) > 6 else False,
            'isVegan': bool(item[7]) if len(item) > 7 else False,
            'calories': item[8] if len(item) > 8 else 0,
            'imageUrl': item[9] if len(item) > 9 else "/static/images/placeholder.jpg"
        }
        result.append(item_dict)
    
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)