from flask import Flask, jsonify, request, render_template
from database import init_db, get_db_connection, init_users_table
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime, timezone, date
import jwt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'  # ⚠️ в проде заменить на секрет из env

init_db()
init_users_table()

# ======= ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =======
def now_iso():
    """Возвращает ISO8601-дату в UTC без микросекунд"""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def make_error(status, error, field_errors=None, message=None):
    payload = {
        "timestamp": now_iso(),
        "status": status,
        "error": error,
    }
    if field_errors:
        payload["fieldErrors"] = field_errors
    if message:
        payload["message"] = message
    return jsonify(payload), status

# ======= JWT =======
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return make_error(401, "Unauthorized", message="Brak tokena")
        try:
            token = token.replace('Bearer ', '')
            jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return make_error(401, "Unauthorized", message="Token wygasł")
        except Exception:
            return make_error(401, "Unauthorized", message="Niepoprawny token")
        return f(*args, **kwargs)
    return decorated

# ======= ROUTES =======
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

# ======= AUTH =======
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    login = (data.get('login') or "").strip()
    password = data.get('password') or ""

    field_errors = []
    if not login:
        field_errors.append({"field": "login", "message": "Login wymagany", "code": "REQUIRED"})
    elif not (3 <= len(login) <= 50):
        field_errors.append({"field": "login", "message": "Login musi mieć 3-50 znaków", "code": "INVALID_LENGTH"})
    if not password or len(password) < 6:
        field_errors.append({"field": "password", "message": "Hasło min 6 znaków", "code": "INVALID_LENGTH"})

    if field_errors:
        return make_error(400, "Bad Request", field_errors=field_errors, message="Błędne dane wejściowe")

    conn = get_db_connection()
    exists = conn.execute('SELECT * FROM users WHERE login = ?', (login,)).fetchone()
    if exists:
        conn.close()
        return make_error(409, "Conflict", message="Login zajęty")

    conn.execute(
        'INSERT INTO users (login, hasloHash, rola, created_at) VALUES (?, ?, ?, ?)',
        (login, generate_password_hash(password), 'USER', now_iso())
    )
    conn.commit()
    conn.close()
    return jsonify({'msg': 'Użytkownik utworzony'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    login = data.get('login')
    password = data.get('password')

    if not login or not password:
        return make_error(400, "Bad Request", message="Login i hasło wymagane")

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE login = ?', (login,)).fetchone()
    conn.close()

    if not user or not check_password_hash(user['hasloHash'], password):
        return make_error(401, "Unauthorized", message="Niepoprawny login lub hasło")

    token = jwt.encode({'login': login}, app.config['SECRET_KEY'], algorithm='HS256')
    if isinstance(token, bytes):
        token = token.decode()
    return jsonify({'access_token': token}), 200

# ======= PRODUKTY =======
def validate_produkt_payload(data, partial=False):
    errs = []
    if not partial or 'nazwa' in data:
        nazwa = (data.get('nazwa') or "").strip()
        if not nazwa:
            errs.append({"field": "nazwa", "message": "Nazwa wymagana", "code": "REQUIRED"})
        elif not (3 <= len(nazwa) <= 50):
            errs.append({"field": "nazwa", "message": "Nazwa musi miec 3-50 znaków", "code": "INVALID_LENGTH"})
    if not partial or 'cena' in data:
        try:
            cena = float(data.get('cena'))
            if cena <= 0:
                errs.append({"field": "cena", "message": "Cena musi być > 0", "code": "INVALID_VALUE"})
        except Exception:
            errs.append({"field": "cena", "message": "Cena musi być liczbą", "code": "INVALID_FORMAT"})
    if not partial or 'ilosc' in data:
        try:
            ilosc = int(data.get('ilosc', 0))
            if ilosc < 0:
                errs.append({"field": "ilosc", "message": "Ilość nie może być ujemna", "code": "INVALID_VALUE"})
        except Exception:
            errs.append({"field": "ilosc", "message": "Ilość musi być liczbą całkowitą", "code": "INVALID_FORMAT"})
    if 'data_dodania' in data and data.get('data_dodania'):
        try:
            dd = datetime.fromisoformat(data.get('data_dodania'))
            if dd.date() > date.today():
                errs.append({"field": "data_dodania", "message": "Data nie może być późniejsza niż dziś", "code": "INVALID_VALUE"})
        except Exception:
            errs.append({"field": "data_dodania", "message": "Niepoprawny format daty", "code": "INVALID_FORMAT"})
    return errs

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
    return jsonify(result), 200

@app.route('/produkty', methods=['POST'])
@token_required
def add_produkt():
    data = request.get_json() or {}
    required_fields = ['nazwa', 'cena', 'kategoria', 'ilosc']

    # Проверка обязательных полей
    for field in required_fields:
        if field not in data:
            return make_error(
                400, "Bad Request",
                field_errors=[{"field": field, "message": "Brak pola", "code": "MISSING_FIELD"}],
                message="Brakuje wymaganych pól"
            )

    # ✅ Добавляем валидацию содержимого
    field_errors = validate_produkt_payload(data)
    if field_errors:
        return make_error(400, "Bad Request", field_errors=field_errors, message="Błędne dane wejściowe")

    conn = get_db_connection()
    # Проверяем, есть ли уже продукт с такой nazwой
    exists = conn.execute('SELECT * FROM produkty WHERE nazwa = ?', (data['nazwa'],)).fetchone()
    if exists:
        conn.close()
        return make_error(409, "Conflict", message="Produkt o takiej nazwie już istnieje")

    conn.execute(
        'INSERT INTO produkty (nazwa, cena, kategoria, ilosc, producent, data_dodania) VALUES (?, ?, ?, ?, ?, ?)',
        (data['nazwa'], data['cena'], data['kategoria'], data['ilosc'], data.get('producent'), data.get('data_dodania'))
    )
    conn.commit()
    conn.close()

    return jsonify({
        "timestamp": now_iso(),
        "status": 201,
        "message": "Produkt dodany pomyślnie!"
    }), 201


@app.route('/produkty/<int:id>', methods=['PUT'])
@token_required
def update_produkt(id):
    data = request.get_json() or {}
    conn = get_db_connection()
    produkt = conn.execute('SELECT * FROM produkty WHERE id = ?', (id,)).fetchone()
    if produkt is None:
        conn.close()
        return make_error(404, "Not Found", message="Produkt nie istnieje")

    field_errors = validate_produkt_payload(data, partial=True)
    if field_errors:
        conn.close()
        return make_error(400, "Bad Request", field_errors=field_errors, message="Błędne dane")

    nazwa = data.get('nazwa', produkt['nazwa'])
    cena = data.get('cena', produkt['cena'])
    kategoria = data.get('kategoria', produkt['kategoria'])
    ilosc = data.get('ilosc', produkt['ilosc'])
    producent = data.get('producent', produkt['producent'])
    data_dodania = data.get('data_dodania', produkt['data_dodania'])

    if nazwa != produkt['nazwa']:
        exists = conn.execute('SELECT * FROM produkty WHERE nazwa = ?', (nazwa,)).fetchone()
        if exists:
            conn.close()
            return make_error(409, "Conflict", message="Inny produkt ma taką samą nazwę")

    conn.execute(
        'UPDATE produkty SET nazwa = ?, cena = ?, kategoria = ?, ilosc = ?, producent = ?, data_dodania = ? WHERE id = ?',
        (nazwa, cena, kategoria, ilosc, producent, data_dodania, id)
    )
    conn.commit()
    conn.close()
    return jsonify({'message': 'Produkt zaktualizowany pomyślnie!'}), 200

@app.route('/produkty/<int:id>', methods=['DELETE'])
@token_required
def delete_produkt(id):
    conn = get_db_connection()
    produkt = conn.execute('SELECT * FROM produkty WHERE id = ?', (id,)).fetchone()
    if produkt is None:
        conn.close()
        return make_error(404, "Not Found", message="Produkt nie istnieje")

    conn.execute('DELETE FROM produkty WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Produkt usunięty pomyślnie!'}), 200

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

