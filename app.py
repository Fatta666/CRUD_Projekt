from flask import Flask, jsonify, request, render_template
from database import init_db, get_db_connection

app = Flask(__name__)

init_db()

@app.route('/')
def home():
    return render_template('index.html')

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
