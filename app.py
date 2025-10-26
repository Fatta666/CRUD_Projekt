from flask import Flask, jsonify, request, render_template
from database import init_db, get_db_connection, init_users_table
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
import jwt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'

init_db()
init_users_table()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'msg':'Brak tokena'}), 401
        try:
            token = token.replace('Bearer ', '')
            jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except:
            return jsonify({'msg':'Niepoprawny token'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    login = data.get('login')
    password = data.get('password')

    if not login or not password or len(password) < 6:
        return jsonify({'msg':'Niepoprawne dane'}), 400

    conn = get_db_connection()
    exists = conn.execute('SELECT * FROM users WHERE login = ?', (login,)).fetchone()
    if exists:
        conn.close()
        return jsonify({'msg':'Login zajęty'}), 400

    conn.execute(
        'INSERT INTO users (login, hasloHash, rola, created_at) VALUES (?, ?, ?, ?)',
        (login, generate_password_hash(password), 'USER', datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()
    return jsonify({'msg':'Użytkownik utworzony'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    login = data.get('login')
    password = data.get('password')

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE login = ?', (login,)).fetchone()
    conn.close()

    if not user or not check_password_hash(user['hasloHash'], password):
        return jsonify({'msg':'Niepoprawny login lub hasło'}), 401

    token = jwt.encode({'login': login}, app.config['SECRET_KEY'], algorithm='HS256')
    return jsonify({'access_token': token}), 200

@app.route('/produkty', methods=['GET'])
def get_produkty():
    conn = get_db_connection()
    produkty = conn.execute('SELECT * FROM produkty').fetchall()
    conn.close()
    result = []
    for produkt in produkty:
        result.append({
            'id': produkt['id'],
            'nazwa': produkt['nazwa'],
            'cena': produkt['cena'],
            'kategoria': produkt['kategoria'],
            'ilosc': produkt['ilosc'],
            'producent': produkt['producent'],
            'data_dodania': produkt['data_dodania']
        })
    return jsonify(result)

@app.route('/produkty', methods=['POST'])
@token_required
def add_produkt():
    data = request.get_json()
    required_fields = ['nazwa', 'cena', 'kategoria', 'ilosc']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Brak pola: {field}'}), 400

    conn = get_db_connection()
    conn.execute(
        'INSERT INTO produkty (nazwa, cena, kategoria, ilosc, producent, data_dodania) VALUES (?, ?, ?, ?, ?, ?)',
        (data['nazwa'], data['cena'], data['kategoria'], data['ilosc'], data.get('producent'), data.get('data_dodania'))
    )
    conn.commit()
    conn.close()
    return jsonify({'message': 'Produkt dodany pomyślnie!'}), 201

@app.route('/produkty/<int:id>', methods=['PUT'])
@token_required
def update_produkt(id):
    data = request.get_json()
    conn = get_db_connection()
    produkt = conn.execute('SELECT * FROM produkty WHERE id = ?', (id,)).fetchone()
    if produkt is None:
        conn.close()
        return jsonify({'error': 'Produkt nie istnieje'}), 404

    nazwa = data.get('nazwa', produkt['nazwa'])
    cena = data.get('cena', produkt['cena'])
    kategoria = data.get('kategoria', produkt['kategoria'])
    ilosc = data.get('ilosc', produkt['ilosc'])
    producent = data.get('producent', produkt['producent'])
    data_dodania = data.get('data_dodania', produkt['data_dodania'])

    conn.execute(
        'UPDATE produkty SET nazwa = ?, cena = ?, kategoria = ?, ilosc = ?, producent = ?, data_dodania = ? WHERE id = ?',
        (nazwa, cena, kategoria, ilosc, producent, data_dodania, id)
    )
    conn.commit()
    conn.close()
    return jsonify({'message': 'Produkt zaktualizowany pomyślnie!'})

@app.route('/produkty/<int:id>', methods=['DELETE'])
@token_required
def delete_produkt(id):
    conn = get_db_connection()
    produkt = conn.execute('SELECT * FROM produkty WHERE id = ?', (id,)).fetchone()
    if produkt is None:
        conn.close()
        return jsonify({'error': 'Produkt nie istnieje'}), 404

    conn.execute('DELETE FROM produkty WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Produkt usunięty pomyślnie!'})

if __name__ == '__main__':
    app.run(debug=True)
