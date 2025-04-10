from flask import Flask, render_template, request, redirect, url_for, abort, session, flash
from flask_session import Session
import psycopg2

app = Flask(__name__, static_folder="")


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
    def __init__(self, user_id, user_name, email, password):
        self.id = user_id
        self.username = user_name
        self.email = email
        self.password = password

@app.route('/reg')
def reg():
    return render_template('reg.html')

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/')
def main():
    return render_template('main.html')

@app.route('/user/create', methods=['POST'])
def create_user():
    user_name = request.form['user_name']
    mail = request.form['mail']
    password = request.form['password']
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('''INSERT INTO USERS(user_name, mail, password)
                   VALUES (%s, %s, %s);''', (user_name, mail, password))
    
    conn.commit()
    conn.close()
    cur.close()
    
    return redirect(url_for('success'))

@app.route('/users/all')    
@app.route('/user/<int:user_id>')
def get_user(user_id=None):
    
    if user_id is None:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''SELECT user_order, user_name, mail, password FROM USERS''')
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

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_name = request.form.get("user_name")
        password = request.form.get("password")
        
        # Подключение к базе данных и создание курсора
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Безопасный SQL-запрос с использованием параметров
        cur.execute("SELECT * FROM users WHERE user_name=%s AND password=%s", (user_name, password))
        user = cur.fetchone()

        if user is not None:
            # Сохраняем идентификатор пользователя в сессии
            session["user_id"] = user[0]
            flash(f"Привет, {user[1]}! Ты успешно вошел.")
            return redirect(url_for("profile"))
        else:
            flash("Неверное имя пользователя или пароль.")
            return redirect(url_for("login"))

    return render_template("login.html")

# Маршрут для выхода пользователя
@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Ты успешно вышел.")
    return redirect(url_for("index"))

# Маршрут для страницы профиля
@app.route("/profile")
def profile():
    if "user_id" in session:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE id=%s", (session["user_id"],))
        user_data = cur.fetchone()
        if user_data is not None:
            user = User(user_data[0], user_data[1], user_data[2], user_data[3])
            return render_template("profile.html", user=user)
        else:
            flash("Произошла ошибка при загрузке профиля.")
            return redirect(url_for("index"))
    else:
        flash("Войдите, пожалуйста, чтобы увидеть свой профиль.")
        return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)