from flask import Flask, jsonify, request, render_template
from database import init_db, get_db_connection

app = Flask(__name__)

# Ініціалізація бази
init_db()

# --- Головна сторінка ---
@app.route('/')
def home():
    return "API działa! (Flask + SQLite)"

@app.route('/ui')
def ui():
    return render_template('index.html')

# --- GET /produkty: Отримати всі продукти ---
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
            'ilosc': produkt['ilosc']
        })
    return jsonify(result)

# --- POST /produkty: Додати новий продукт ---
@app.route('/produkty', methods=['POST'])
def add_produkt():
    data = request.get_json()
    required_fields = ['nazwa', 'cena', 'kategoria', 'ilosc']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Brak pola: {field}'}), 400

    conn = get_db_connection()
    conn.execute(
        'INSERT INTO produkty (nazwa, cena, kategoria, ilosc) VALUES (?, ?, ?, ?)',
        (data['nazwa'], data['cena'], data['kategoria'], data['ilosc'])
    )
    conn.commit()
    conn.close()

    return jsonify({'message': 'Produkt dodany pomyślnie!'}), 201

# --- PUT /produkty/<id>: Редагувати продукт ---
@app.route('/produkty/<int:id>', methods=['PUT'])
def update_produkt(id):
    data = request.get_json()
    conn = get_db_connection()
    produkt = conn.execute('SELECT * FROM produkty WHERE id = ?', (id,)).fetchone()
    if produkt is None:
        conn.close()
        return jsonify({'error': 'Produkt nie istnieje'}), 404

    # Використовуємо старі значення, якщо нові не передані
    nazwa = data.get('nazwa', produkt['nazwa'])
    cena = data.get('cena', produkt['cena'])
    kategoria = data.get('kategoria', produkt['kategoria'])
    ilosc = data.get('ilosc', produkt['ilosc'])

    conn.execute(
        'UPDATE produkty SET nazwa = ?, cena = ?, kategoria = ?, ilosc = ? WHERE id = ?',
        (nazwa, cena, kategoria, ilosc, id)
    )
    conn.commit()
    conn.close()

    return jsonify({'message': 'Produkt zaktualizowany pomyślnie!'})

# --- DELETE /produkty/<id>: Видалити продукт ---
@app.route('/produkty/<int:id>', methods=['DELETE'])
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
