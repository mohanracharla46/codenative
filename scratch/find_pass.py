import hashlib

target = "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"
candidates = ["admin", "admin123", "1234", "123456", "mohan", "mohan123", "Mohan@123", "mohanracharla", "Mohanani#467", "mohanani#467"]

for c in candidates:
    h = hashlib.sha256(c.encode()).hexdigest()
    if h == target:
        print(f"Match found: {c}")
        break
else:
    print("No match found in candidates.")
