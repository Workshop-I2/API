import sqlite3

DATABASE = "toxic_users.db"

def init_db():
    print("database initializing")
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip TEXT,
        mac_address TEXT,
        phone_number TEXT,
        toxic_count INTEGER DEFAULT 0,
        severe_toxic_count INTEGER DEFAULT 0,
        obscene_count INTEGER DEFAULT 0,
        threat_count INTEGER DEFAULT 0,
        insult_count INTEGER DEFAULT 0,
        identity_hate_count INTEGER DEFAULT 0
    )
    ''')
    conn.commit()
    conn.close()

# Rechercher un utilisateur avec au moins 2 identifiants correspondants
def find_user(conn, ip: str, mac_address: str, phone_number: str):
    cursor = conn.cursor()
    cursor.execute('''
    SELECT * FROM users WHERE 
    (ip LIKE ? AND mac_address LIKE ?) OR 
    (ip LIKE ? AND phone_number LIKE ?) OR 
    (mac_address LIKE ? AND phone_number LIKE ?)
    ''', (f"%{ip}%", f"%{mac_address}%", f"%{ip}%", f"%{phone_number}%", f"%{mac_address}%", f"%{phone_number}%"))
    return cursor.fetchone()

# Fonction pour mettre à jour les identifiants d'un utilisateur
def update_identifiers(existing: str, new: str) -> str:
    existing_list = existing.split(';') if existing else []
    if new not in existing_list:
        existing_list.append(new)
    return ';'.join(existing_list)

# Ajouter ou mettre à jour un utilisateur dans la base de données
def update_or_insert_user(ip: str, mac_address: str, phone_number: str, classifications):
    conn = sqlite3.connect(DATABASE)
    
    user = find_user(conn, ip, mac_address, phone_number)
    
    if user:
        user_id = user[0]
        updated_ip = update_identifiers(user[1], ip)
        updated_mac = update_identifiers(user[2], mac_address)
        updated_phone = update_identifiers(user[3], phone_number)
        
        # Mise à jour des catégories problématiques
        category_updates = [f"{category}_count = {category}_count + 1" for category in classifications]
        category_update_query = ", ".join(category_updates)
        
        query = f'''
        UPDATE users
        SET ip = ?, mac_address = ?, phone_number = ?, {category_update_query}
        WHERE id = ?
        '''
        conn.execute(query, (updated_ip, updated_mac, updated_phone, user_id))
    
    else:
        print('classifications')
        print(classifications)
        category_values = [1 if category in classifications else 0 for category in ['toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hate']]

        query = '''
        INSERT INTO users (ip, mac_address, phone_number, toxic_count, severe_toxic_count, obscene_count, threat_count, insult_count, identity_hate_count)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        conn.execute(query, (ip, mac_address, phone_number, *category_values))
    
    conn.commit()
    conn.close()
