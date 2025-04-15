import hashlib
from flask import Flask, render_template, request, redirect, url_for, abort, session, flash
from flask_session import Session
import psycopg2
from werkzeug.utils import secure_filename
import os

app = Flask(__name__, static_folder="")
app.secret_key = '123123'
app.config['UPLOAD_FOLDER'] = './uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  

# Конфигурация для работы с сессией
app.config["SECRET_KEY"] = "super_secret_key"  # Замените на свою секретную фразу
app.config["SESSION_TYPE"] = "filesystem"      # Хранение сессий на файловой системе
Session(app)

# Настройки подключения к базе данных
DATABASE_URL = 'postgresql://postgres:123123@localhost:5432/users_application'  # Ваш URL подключения к БД

# Функция для получения соединения с базой данных
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

# Класс для представления пользователя
class User:
    def __init__(self, user_id, user_name, email, password_hash, avatar_url, registration_date):
        self.user_id = user_id
        self.user_name = user_name
        self.email = email
        self.password_hash = password_hash
        self.avatar_url = avatar_url
        self.registration_date = registration_date

class User_profile:
    def __init__(self,user_id, user_name, email, avatar_url, registration_date):
        self.user_id = user_id
        self.user_name = user_name
        self.email = email
        self.avatar_url = avatar_url
        self.registration_date = registration_date

@app.route('/reg')
def reg():
    return render_template('reg.html')

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/')
def home():
    if 'user_id' in session:
        conn = get_db_connection()
        cur = conn.cursor()
        print(f"Запрашиваемый ID: {session['user_id']}")  # Отладочная печать
        cur.execute('SELECT avatar_url FROM users WHERE user_id=%s', (session['user_id'],))
        user_data = cur.fetchone()
        print(f"Полученный результат: {user_data}")  # Отладочная печать
        avatar_url = user_data[0] if user_data else 'uploads/default_avatar.png'
        conn.close()
    else:
        avatar_url = 'uploads/default_avatar.png'

    return render_template('main.html', avatar_url=avatar_url)


@app.route('/user/create', methods=['POST'])
def create_user():
    user_name = request.form['user_name']
    email = request.form['mail']
    password = request.form['password']

    # Хешируем пароль перед сохранением
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    conn = get_db_connection()
    cur = conn.cursor()

    # Сохраняем хешированный пароль
    cur.execute('''
        INSERT INTO USERS(user_name, email, password_hash)
        VALUES (%s, %s, %s);
    ''', (user_name, email, hashed_password))

    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('success'))

@app.route('/users/all')    
@app.route('/user/<int:user_id>')
def get_user(user_id=None):
    
    if user_id is None:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''SELECT user_order, user_name, email, password FROM USERS''')
        users_data = cur.fetchall()
        conn.close()
        cur.close()
        
        return [User(i[0], i[1], i[2], i[3]).__dict__ for i in users_data]
    
    cur.execute('''SELECT * FROM USERS WHERE users_order=%s''', [user_id])
    
    user_data = cur.fetchall()
    
    conn.close()
    cur.close
    
    if users_data.__len__():
        return abort(404, f"User with id {user_id} not found")
    
    return User(user_data[0][0], user_data[0][1]).__dict__

# Маршрут для авторизации
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_name = request.form.get("user_name")
        password = request.form.get("password")
        
        # Получаем подключение к базе данных
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Сначала проверяем, существует ли пользователь
        cur.execute("SELECT * FROM users WHERE user_name=%s", (user_name,))
        user = cur.fetchone()
        
        if user is not None:
            stored_password_hash = user[3]  # Предполагаем, что пароль хранится в третьем поле
            input_password_hash = hashlib.sha256(password.encode()).hexdigest()  # Простое хеширование SHA-256
            print(stored_password_hash is input_password_hash)
            if input_password_hash == stored_password_hash:
                # Авторизация успешна
                session['logged_in'] = True
                session["user_id"] = user[0]
                flash(f"Привет, {user[1]}! Ты успешно вошёл.")
                return redirect(url_for("profile"))
            else:
                flash("Неверный пароль.")
                return redirect(url_for('login'))
        else:
            flash("Пользователь не найден.")
            return redirect(url_for('login'))
        
        # Завершаем работу с базой данных
        cur.close()
        conn.close()
        
        return redirect(url_for("login"))

    return render_template("login.html")

# Маршрут для выхода пользователя
@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Ты успешно вышел.")
    return redirect(url_for("home"))

@app.route("/profile")
def profile():
    # Проверяем наличие авторизации
    if "user_id" in session:
        conn = get_db_connection()  # Функция для подключения к БД
        cur = conn.cursor()
        
        # Выполняем запрос к базе данных
        cur.execute(
            """
            SELECT user_id, user_name, email, avatar_url, registration_date 
            FROM users 
            WHERE user_id=%s
            """,
            (session["user_id"],),
        )
        user_data = cur.fetchone()
    
        if user_data is not None:
            user = User_profile(
                user_id=user_data[0],
                user_name=user_data[1],
                email=user_data[2],
                avatar_url=user_data[3],
                registration_date=user_data[4],
            )
            return render_template("profile.html", user=user)
        else:
            flash("Произошла ошибка при загрузке профиля.")
            return redirect(url_for("main"))
    else:
        flash("Войдите, пожалуйста, чтобы увидеть свой профиль.")
        return redirect(url_for("login"))
    
@app.route('/edit-profile', methods=['GET'])
def edit_profile():
    if not session.get('logged_in'):
        flash('Необходимо войти в систему', 'warning')
        return redirect(url_for('login'))

    if "user_id" in session:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT user_id, user_name, email, avatar_url, registration_date 
            FROM users 
            WHERE user_id=%s
            """,
            (session["user_id"],),
        )
        user_data = cur.fetchone()
        conn.close()
        return render_template('edit-profile.html', user=user_data)
    else:
        return redirect(url_for('login'))

# Маршрут для обновления профиля
@app.route('/update-profile', methods=['POST'])
def update_profile():
    if not session.get('logged_in'):
        flash('Необходимо войти в систему', 'warning')
        return redirect(url_for('login'))

    # Получить данные из формы
    new_username = request.form.get('user_name')
    new_email = request.form.get('email')
    avatar_file = request.files.get('avatar')

    # Соединение с базой данных
    conn = get_db_connection()
    cur = conn.cursor()

    # Обновляем данные пользователя
    update_query = """UPDATE users SET user_name=%s, email=%s"""
    params = [new_username, new_email]

    # Если загружен новый аватар, сохраняем его
    if avatar_file:
        filename = secure_filename(avatar_file.filename)
        avatar_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        avatar_file.save(avatar_path)
        update_query += ", avatar_url=%s"
        params.append('/uploads/' + filename)

    # Дополняем запрос фильтрацией по user_id
    update_query += " WHERE user_id=%s;"
    params.append(session["user_id"])

    # Выполнить запрос на обновление
    cur.execute(update_query, tuple(params))
    conn.commit()
    conn.close()

    flash('Профиль успешно обновлён!', 'success')
    return redirect(url_for('profile'))

if __name__ == "__main__":
    app.run(debug=True)