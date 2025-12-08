from app import create_app, db
from app.models import Product

app = create_app()

def seed_products():
    with app.app_context():
        # Ensure table exists
        db.create_all()
        
        products_to_seed = [
            {'name': 'Marcus High Yield Savings', 'category': 'Savings', 'risk_level': 'Low', 'tags': 'Safe'},
            {'name': 'Chase Sapphire Reserve', 'category': 'Credit Card', 'risk_level': 'Medium', 'tags': 'Travel'},
            {'name': 'Citi Simplicity', 'category': 'Credit Card', 'risk_level': 'Low', 'tags': 'Debt-Consolidation'},
            {'name': 'Vanguard S&P 500 ETF', 'category': 'Investment', 'risk_level': 'Medium', 'tags': 'Growth'},
            {'name': 'Bitcoin Trust', 'category': 'Investment', 'risk_level': 'High', 'tags': 'Crypto'}
        ]
        
        print("--- Seeding Products ---")
        for p_data in products_to_seed:
            exists = Product.query.filter_by(name=p_data['name']).first()
            if not exists:
                new_product = Product(
                    name=p_data['name'],
                    category=p_data['category'],
                    risk_level=p_data['risk_level'],
                    tags=p_data['tags']
                )
                db.session.add(new_product)
                print(f"Added: {p_data['name']}")
            else:
                print(f"Exists: {p_data['name']}")
        
        db.session.commit()
        print("Product seeding complete.")

if __name__ == '__main__':
    seed_products()
