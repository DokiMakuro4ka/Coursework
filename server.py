import hashlib
from flask import Flask, render_template, request, redirect, url_for, abort, session, flash, jsonify
from flask_session import Session
from datetime import datetime
import decimal
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
from flask_session import Session
Session(app)

# Настройки подключения к базе данных
DATABASE_URL = 'postgresql://postgres:123123@localhost:5432/users_application'  # Ваш URL подключения к БД

# Функция для получения соединения с базой данных
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

# Путь к директории загрузки изображений
UPLOAD_FOLDER = app.config['UPLOAD_FOLDER']

# Разрешенные расширения файлов
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Класс для представления пользователя
class User:
    def __init__(self, user_id, user_name, email, password_hash, avatar_url, registration_date, role):
        self.user_id = user_id
        self.user_name = user_name
        self.email = email
        self.password_hash = password_hash
        self.avatar_url = avatar_url
        self.registration_date = registration_date
        self.role = role

class User_profile:
    def __init__(self,user_id, user_name, email, avatar_url, registration_date):
        self.user_id = user_id
        self.user_name = user_name
        self.email = email
        self.avatar_url = avatar_url
        self.registration_date = registration_date

class Role:
    def __init__(self, role_id, role_name):
        self.role_id = role_id
        self.role_name = role_name

@app.route('/reg')
def reg():
    return render_template('reg.html')

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    elif 'user_id' in session:
        session['logged_in'] = True
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT avatar_url FROM users WHERE user_id=%s', (session['user_id'],))
        user_data = cur.fetchone()
        avatar_url = user_data[0] if user_data else 'uploads/default_avatar.png'
        conn.close()
    else:
        session['logged_in'] = False
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

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_name = request.form.get("user_name")
        password = request.form.get("password")
        
        # Проверка наличия обоих полей
        if not user_name or not password:
            return render_template("login.html", error_message="Заполните все поля!")
        
        # Получаем подключение к базе данных
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Проверяем существование пользователя
        cur.execute("SELECT * FROM users WHERE user_name=%s", (user_name,))
        user = cur.fetchone()
        
        if user is not None:
            stored_password_hash = user[3]  # Полагаясь, что пароль хранится в третьем поле
            input_password_hash = hashlib.sha256(password.encode()).hexdigest()  # Хэшируем введённый пароль
            
            if input_password_hash == stored_password_hash:
                # Успешная авторизация
                session['logged_in'] = True
                session["user_id"] = user[0]
                return redirect(url_for("profile"))  # Перенаправление на профиль
                
            else:
                # Неверный пароль
                return render_template("login.html", error_message="Неверный пароль.")
        else:
            # Пользователь не найден
            return render_template("login.html", error_message="Пользователь не найден.")
        
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Ты успешно вышел.")
    return redirect(url_for("home"))

@app.route("/profile")
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
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

@app.route("/api/products")
def get_products():
    conn = get_db_connection()
    cur = conn.cursor()

    # Сначала получаем роль пользователя
    user_id = session.get('user_id')
    if user_id:
        cur.execute('SELECT role_id FROM users WHERE user_id=%s', (user_id,))
        user_role_row = cur.fetchone()
        if user_role_row:
            user_role = user_role_row[0]
        else:
            user_role = '1'
    else:
        user_role = '1'

    # Далее выполняем основную выборку продуктов
    # Параметры фильтра
    title_filter = request.args.get('title')
    price_min = request.args.get('min_price')
    price_max = request.args.get('max_price')
    sort_by = request.args.get('sort_by') or 'product_id'

    # Проверяем валидные поля сортировки
    valid_sort_fields = ['product_id', 'title', 'price']
    if sort_by not in valid_sort_fields:
        return jsonify({"message": f"Недопустимое поле сортировки '{sort_by}'. Допустимые значения: {valid_sort_fields}"})

    # Формируем SQL-запрос с условиями фильтрации и сортировкой
    sql_query = """
        SELECT *
        FROM products
        WHERE true
    """

    params = {}

    if title_filter:
        sql_query += " AND LOWER(title) LIKE LOWER(%(title)s)"
        params['title'] = '%' + title_filter.lower() + '%'

    if price_min is not None:
        sql_query += " AND price >= %(min_price)s"
        params['min_price'] = float(price_min)

    if price_max is not None:
        sql_query += " AND price <= %(max_price)s"
        params['max_price'] = float(price_max)

    sql_query += f" ORDER BY {sort_by}"

    cur.execute(sql_query, params)
    rows = cur.fetchall()

    result = [
        {
            'product_id': row[0],
            'title': row[1],
            'description': row[2],
            'price': row[3],
            'image_url': row[4]
        }
        for row in rows
    ]

    # Возвращаем список продуктов и роль пользователя
    return jsonify({
        'products': result,
        'user_role': user_role
    })
    
@app.route('/product/<int:id>', methods=['GET'])
def view_product(id):
    try:
        if 'user_id' in session:
            session['logged_in'] = True
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('SELECT avatar_url FROM users WHERE user_id=%s', (session['user_id'],))
            user_data = cur.fetchone()
            avatar_url = user_data[0] if user_data else 'uploads/default_avatar.png'
        else:
            session['logged_in'] = False
            avatar_url = 'uploads/default_avatar.png'

        cur.execute("SELECT * FROM products WHERE product_id=%s;", (id,))
        row = cur.fetchone()
        
        if row is None:
            # Товар не найден, выдаём ошибку 404
            abort(404)
        
        # Преобразование результата в удобный объект
        product = {
            'product_id': row[0],
            'title': row[1],
            'description': row[2],
            'price': row[3],
            'image_url': row[4]
        }
        
        # Возвращаем шаблон страницы товара
        return render_template('product.html', product=product, avatar_url=avatar_url)
    except Exception as ex:
        # Выводим сообщение об ошибке
        abort(500)

@app.route("/add-to-cart", methods=["POST"])
def add_to_cart():
    """Добавляет товар в корзину."""
    try:
        # Получаем ID продукта и количество из формы
        product_id = int(request.form.get("product_id"))
        count = int(request.form.get("count", 1))  # Получаем количество товара (по умолчанию 1)

        # Проверка наличия аутентифицированного пользователя
        if not session.get("user_id"):
            flash("Необходимо войти в систему.")
            return redirect(url_for("login"))  # Перенаправляем на страницу авторизации

        # Соединение с базой данных
        with get_db_connection() as conn:
            cur = conn.cursor()
            # Запись заказа в базу данных
            cur.execute(
                "INSERT INTO cart (product_id, user_id, count) VALUES (%s, %s, %s)",
                (product_id, session.get("user_id"), count),  # Тут используем количество из формы
            )
            conn.commit()

        flash("Товар успешно добавлен в корзину!")
        return redirect(url_for("home"))  # Возвращаемся обратно на главную страницу

    except Exception as e:
        print(f"Ошибка при добавлении товара в корзину: {e}")
        flash("Возникла ошибка при добавлении товара в корзину.")
        return redirect(url_for("home"))

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():  
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        
        # Обработка загрузки фото
        file = request.files.get('photo')
        photo_path = None
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            
            # Определение пути для сохранения файла относительно текущего рабочего каталога
            upload_folder = 'uploads'
            os.makedirs(upload_folder, exist_ok=True)  # Создаем директорию загрузки, если её ещё нет
            
            # Полный путь для сохранения файла
            full_path = os.path.join(upload_folder, filename)
            
            # Сохранение файла
            file.save(full_path)
            
            # Относительный путь для записи в базу данных
            photo_path = '/' + full_path.lstrip('/')
        
        try:
            conn = get_db_connection()  # Предположительно, ваша функция подключения к БД
            cur = conn.cursor()
            
            sql_query = """
                INSERT INTO products (title, description, price, image_url)
                VALUES (%s, %s, %s, %s);
            """
            values = (name, description, price, photo_path)
            cur.execute(sql_query, values)
            conn.commit()
            flash('Продукт успешно добавлен!', category='success')
            return redirect(url_for('home'))
        except Exception as e:
            flash('Ошибка при добавлении продукта.', category='danger')
            return redirect(url_for('home'))
        finally:
            cur.close()
            conn.close()
    
    return render_template('add_product.html')

@app.route('/edit_product/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT role_id FROM users WHERE user_id=%s', (session['user_id'],))
    user_role = cur.fetchone()[0]
    print('Роль: ', user_role)
    if user_role == '1':
        flash('Вы не имеете полномочий для удаления товаров.', 'danger')
        return redirect(url_for('home'))
    else:
        if request.method == 'GET':  # Запрашиваем данные товара
            cur.execute("SELECT * FROM products WHERE product_id=%s;", (id,))
            product = cur.fetchone()
            if not product:
                flash('Товар не найден.', category='warning')
                return redirect(url_for('home'))
            else:
                return render_template('edit_product.html', product=product)

        elif request.method == 'POST':  # Обрабатываем отправленную форму
            title = request.form['title']
            description = request.form['description']
            price = float(request.form['price'])
            image_file = request.files.get('image_url')  # Проверка загрузки нового изображения
            print(f'Полученные данные: название {title}, описание{description}, цена{price}, фото{image_file}')
            
            # Если загрузилось новое изображение
            if image_file and image_file.filename != '':
                filename = secure_filename(image_file.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image_file.save(image_path)
                print ('Файл: ', image_file)
                new_image_url = "/uploads/" + filename
                        # Обновление записей в таблице
                sql_query = """
                    UPDATE products SET title=%s, description=%s, price=%s, image_url=%s WHERE product_id=%s;
                """
                values = (title, description, price, new_image_url, id)
                cur.execute(sql_query, values)
                conn.commit()
                cur.close()
                conn.close()
                flash('Товар успешно обновлён!', category='success')
                return redirect(url_for('home'))  # Перенаправляем на список товаров

            else:
                # Здесь мы используем старый адрес изображения из формы
                old_image_url = request.form.get('old_image_url')  # Предположительно старое изображение передается в форме
                new_image_url = old_image_url
                return redirect(url_for('home'))

@app.route('/cart')
def cart():
    """Отображает содержимое корзины пользователя."""
    # Проверяем, залогинен ли пользователь
    if 'user_id' not in session:
        flash('Необходимо войти в систему.', 'warning')
        return redirect(url_for('login'))

    # Подключаемся к базе данных
    with get_db_connection() as conn:
        cur = conn.cursor()
        # Получаем товары из корзины текущего пользователя
        cur.execute("""
            SELECT p.title AS name, o.count AS quantity, p.price AS price, 
                   o.count * p.price AS total_price, o.order_id AS order_id
            FROM cart o
            JOIN products p ON o.product_id = p.product_id
            WHERE o.user_id = %s
            ORDER BY o.order_id ASC
        """, (session['user_id'], ))

        rows = cur.fetchall()

    # Подготовим массив объектов для передачи в шаблон
    cart_items = []
    total_sum = 0.0
    for row in rows:
        name, quantity, price, total_price, order_id = row
        cart_items.append({
            'name': name,
            'quantity': quantity,
            'price': float(price),
            'total_price': float(total_price),
            'order_id': order_id
        })
        total_sum += total_price

    return render_template("cart.html", cart_items=cart_items, total_sum=total_sum)

@app.route("/checkout", methods=["POST"])
def checkout():
    if request.method == "POST":
        try:
            # Проверяем, залогинен ли пользователь
            if not session.get("logged_in"):
                flash('Вы должны войти в систему для оформления заказа.', 'warning')
                return redirect(url_for('login'))
            
            # Получаем итоговую сумму из формы
            total_sum_str = request.form.get("total_sum")
            
            # Проверяем, что итоговая сумма передана и корректна
            if not total_sum_str:
                flash("Не удалось определить итоговую сумму заказа.", category="danger")
                return redirect(url_for('cart'))
            
            try:
                total_sum = decimal.Decimal(total_sum_str)
            except decimal.InvalidOperation:
                flash("Неверный формат итоговой суммы.", category="danger")
                return redirect(url_for('cart'))
            
            # Подключение к базе данных
            with get_db_connection() as conn:
                cur = conn.cursor()
                conn.autocommit = False  # Работаем в режиме транзакции
                
                try:
                    # Получаем товары из корзины текущего пользователя
                    cur.execute(
                        """
                        SELECT p.title AS product_name, c.count AS quantity, p.price AS unit_price
                        FROM cart c
                        JOIN products p ON c.product_id = p.product_id
                        WHERE c.user_id = %s
                        """,
                        (session["user_id"],)
                    )
                    cart_items = cur.fetchall()
                    
                    # Если корзина пуста, сообщаем об этом пользователю
                    if not cart_items:
                        flash("Корзина пуста. Оформление заказа невозможно.", category="warning")
                        return redirect(url_for('cart'))
                    
                    # Создаем новый заказ для каждого товара в корзине
                    for product_name, quantity, unit_price in cart_items:
                        total_item_price = unit_price * quantity
                        
                        # Создаем запись в таблице orders
                        cur.execute(
                            """
                            INSERT INTO orders (user_id, product_name, quantity, total_price, created_at)
                            VALUES (%s, %s, %s, %s, %s)
                            """,
                            (session["user_id"], product_name, quantity, total_item_price, datetime.now())
                        )
                    
                    # Очищаем корзину после оформления заказа
                    cur.execute(
                        """
                        DELETE FROM cart
                        WHERE user_id = %s
                        """,
                        (session["user_id"],)
                    )
                    
                    # Фиксируем транзакцию
                    conn.commit()
                    
                    flash("Ваш заказ успешно оформлен!", category="success")
                    return redirect(url_for('index'))
                
                except Exception as e:
                    conn.rollback()
                    print(f"Ошибка при оформлении заказа: {e}")
                    flash("При оформлении заказа возникла проблема.", category="danger")
                    return redirect(url_for('cart'))
                
                finally:
                    cur.close()
        
        except Exception as e:
            print(f"Ошибка при оформлении заказа: {e}")
            flash("При оформлении заказа возникла проблема.", category="danger")
            return redirect(url_for('cart'))

@app.route('/remove-from-cart', methods=['POST'])
def remove_from_cart():
    """Удаляет товар из корзины"""
    try:
        # Получаем ID заказа из формы
        order_id = int(request.form.get("order_id"))

        # Проверка наличия аутентифицированного пользователя
        if not session.get("user_id"):
            flash("Необходимо войти в систему.", "warning")
            return redirect(url_for("login"))

        # Удаляем товар из корзины
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM cart WHERE order_id = %s", (order_id,))
            conn.commit()

        flash("Товар успешно удалён из корзины!", "info")
        return redirect(url_for("cart"))

    except Exception as e:
        print(f"Ошибка при удалении товара из корзины: {e}")
        flash("Возникла ошибка при удалении товара из корзины.", "danger")
        return redirect(url_for("cart"))

@app.route('/orders', methods=['GET'])
def get_orders():
    # Проверяем, залогинен ли пользователь
    if not session.get("logged_in"):
        flash('Вы должны войти в систему.', 'warning')
        return redirect(url_for('login'))

    # Получаем историю заказов из базы данных
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT o.order_id, o.product_name, o.quantity, o.total_price, o.created_at, os.status_id
            FROM orders o
            INNER JOIN order_status os ON o.status_id = os.status_id
            WHERE o.user_id = %s
            ORDER BY o.created_at DESC
        """, (session["user_id"],))
        results = cur.fetchall()

    # Преобразуем данные в удобный формат для шаблона
    orders_data = [
        {
            "order_id": row[0],
            "product_name": row[1],
            "quantity": row[2],
            "total_price": row[3],
            "create_at": row[4].strftime('%Y-%m-%d'),
            "status": row[5]
        }
        for row in results
    ]

    return render_template('orders.html', orders=orders_data)


if __name__ == '__main__':
    app.run(debug=True)