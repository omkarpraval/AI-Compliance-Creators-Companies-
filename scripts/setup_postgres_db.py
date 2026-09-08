import psycopg

def setup_db():
    conn = psycopg.connect("postgresql://postgres:postgres@localhost:5432/postgres", autocommit=True)
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_roles WHERE rolname = 'verifyd'")
        if not cur.fetchone():
            cur.execute("CREATE ROLE verifyd WITH LOGIN PASSWORD 'verifyd' SUPERUSER CREATEDB")
            print("Created role verifyd")
        else:
            cur.execute("ALTER ROLE verifyd WITH PASSWORD 'verifyd' SUPERUSER CREATEDB")
            print("Updated role verifyd")

        cur.execute("SELECT 1 FROM pg_database WHERE datname = 'verifyd'")
        if not cur.fetchone():
            cur.execute("CREATE DATABASE verifyd OWNER verifyd")
            print("Created database verifyd")
        else:
            print("Database verifyd already exists")
            
        cur.execute("SELECT 1 FROM pg_database WHERE datname = 'verifyd_test'")
        if not cur.fetchone():
            cur.execute("CREATE DATABASE verifyd_test OWNER verifyd")
            print("Created database verifyd_test")
        else:
            print("Database verifyd_test already exists")
    conn.close()

if __name__ == "__main__":
    setup_db()
