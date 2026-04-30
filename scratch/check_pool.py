
try:
    from psycopg2 import pool
    print("psycopg2.pool imported successfully")
    print(f"Available: {[name for name in dir(pool) if 'Pool' in name]}")
except Exception as e:
    print(f"Failed to import psycopg2.pool: {e}")
