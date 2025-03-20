from tinydb import TinyDB, Query
import os

# Pfad zur JSON-Datenbank
db_path = os.path.join(os.path.dirname(__file__), 'data', 'mechanisms.json')

# Ordner und Datei automatisch erstellen, falls nicht vorhanden
if not os.path.exists(os.path.dirname(db_path)):
    os.makedirs(os.path.dirname(db_path))

if not os.path.exists(db_path):
    with open(db_path, 'w') as f:
        f.write("{}")

# TinyDB initialisieren
db = TinyDB(db_path)
MechanismTable = db.table('mechanisms')

def save_mechanism(user, name, data):
    """Speichert einen Mechanismus in der Datenbank (Benutzer + Name)"""
    MechanismTable.upsert({'user': user, 'name': name, 'data': data}, 
                          (Query().user == user) & (Query().name == name))

def load_mechanism(user, name):
    """Lädt einen gespeicherten Mechanismus eines Benutzers"""
    result = MechanismTable.search((Query().user == user) & (Query().name == name))
    if result:
        return result[0]['data']
    return None

def delete_mechanism(user, name):
    """Löscht einen gespeicherten Mechanismus eines Benutzers"""
    MechanismTable.remove((Query().user == user) & (Query().name == name))

def list_mechanisms(user):
    """Gibt eine Liste der gespeicherten Mechanismen für einen Benutzer zurück"""
    return [entry['name'] for entry in MechanismTable.search(Query().user == user)]