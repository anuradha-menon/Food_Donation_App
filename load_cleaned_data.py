import pandas as pd
from sqlalchemy import create_engine, text

# PostgreSQL connection details
db_user = "postgres"   # your postgres username
db_password = "your_password"  # change to your actual password
db_host = "localhost"
db_port = "5432"
db_name = "food_waste_db"

# Create DB connection
engine = create_engine(f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")

# File to table mapping
csv_table_map = {
    "providers_clean.csv": "providers",
    "receivers_clean.csv": "receivers",
    "food_listings_clean.csv": "food_listings",
    "claims_clean.csv": "claims"
}

# Create tables if not exist
create_table_queries = {
    "providers": """
        CREATE TABLE IF NOT EXISTS providers (
            provider_id SERIAL PRIMARY KEY,
            name TEXT,
            location TEXT,
            contact TEXT
        )
    """,
    "receivers": """
        CREATE TABLE IF NOT EXISTS receivers (
            receiver_id SERIAL PRIMARY KEY,
            name TEXT,
            location TEXT,
            contact TEXT
        )
    """,
    "food_listings": """
        CREATE TABLE IF NOT EXISTS food_listings (
            listing_id SERIAL PRIMARY KEY,
            provider_id INT,
            food_item TEXT,
            quantity INT,
            expiry_date DATE,
            FOREIGN KEY (provider_id) REFERENCES providers(provider_id)
        )
    """,
    "claims": """
        CREATE TABLE IF NOT EXISTS claims (
            claim_id SERIAL PRIMARY KEY,
            listing_id INT,
            receiver_id INT,
            claim_date DATE,
            FOREIGN KEY (listing_id) REFERENCES food_listings(listing_id),
            FOREIGN KEY (receiver_id) REFERENCES receivers(receiver_id)
        )
    """
}

# Run create table queries
with engine.connect() as conn:
    for table_name, query in create_table_queries.items():
        conn.execute(text(query))
    conn.commit()

# Load CSVs into tables
for csv_file, table_name in csv_table_map.items():
    print(f"Loading {csv_file} into {table_name}...")
    df = pd.read_csv(csv_file)
    df.to_sql(table_name, engine, if_exists="append", index=False)

print("✅ All cleaned CSVs loaded into PostgreSQL successfully!")
