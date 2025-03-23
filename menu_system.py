from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, Confirm
import sqlite3
import random

class MenuRecommendationSystem:
    def __init__(self, db_path='restaurant.db'):
        self.console = Console()
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.setup_database()
    
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
            calories INTEGER
        )''')
        self.conn.commit()
    
    def get_preferences(self):
        self.console.print(Panel("Welcome to the AI Restaurant! 🍽️", style="bold green"))
        category = Prompt.ask("What category of food do you prefer?", choices=["Main", "Appetizer", "Dessert", "Any"], default="Any")
        vegetarian = Confirm.ask("Do you want only vegetarian options?")
        vegan = Confirm.ask("Do you want only vegan options?")
        max_spicy = IntPrompt.ask("What is the maximum spice level you can handle? (0-5)", default=3, choices=["0", "1", "2", "3", "4", "5"])
        return category, vegetarian, vegan, max_spicy
    
    def get_recommendations(self, category, vegetarian, vegan, max_spicy, limit=3):
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
        self.cursor.execute(query, params)
        items = self.cursor.fetchall()
        return random.sample(items, min(len(items), limit))
    
    def display_recommendations(self, recommendations):
        table = Table(title="🍽️ Recommended Dishes", style="bold cyan")
        table.add_column("ID", justify="center", style="yellow")
        table.add_column("Name", style="bold white")
        table.add_column("Category", style="magenta")
        table.add_column("Price ($)", justify="right", style="green")
        table.add_column("Spice 🌶", justify="center", style="red")
        for item in recommendations:
            spice = "🌶️" * item[5] if item[5] > 0 else "Not spicy"
            table.add_row(str(item[0]), item[1], item[2], f"{item[3]:.2f}", spice)
        self.console.print(table)
    
    def run(self):
        category, vegetarian, vegan, max_spicy = self.get_preferences()
        recommendations = self.get_recommendations(category, vegetarian, vegan, max_spicy)
        if recommendations:
            self.display_recommendations(recommendations)
        else:
            self.console.print("[bold red]No matching dishes found. Try changing your preferences![/]")
        self.conn.close()

if __name__ == "__main__":
    system = MenuRecommendationSystem()
    system.run()
