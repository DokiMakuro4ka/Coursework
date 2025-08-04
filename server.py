import hashlib
from flask import Flask, render_template, request, redirect, url_for, abort, session, flash, jsonify
from flask_session import Session
from datetime import datetime
from decimal import Decimal, InvalidOperation
import psycopg2
from werkzeug.utils import secure_filename
import os

app = Flask(__name__, static_folder="")
app.secret_key = '123123'
app.config['UPLOAD_FOLDER'] = './uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  

app.config["SECRET_KEY"] = "super_secret_key"
app.config["SESSION_TYPE"] = "filesystem"      
from flask_session import Session
Session(app)

# Настройки подключения к базе данных
DATABASE_URL = 'postgresql://users_application_q6ok_user:Myf3l9gCMxT0n6SZ7ewn7YU3fGPE1UWT@dpg-d28a6u3ipnbc739h0hk0-a.oregon-postgres.render.com/users_application_q6ok'

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


@app.template_filter('to_datetime')
def to_datetime(value):
    """Кастомный фильтр для превращения строки в объект datetime"""
    if isinstance(value, str):
        return datetime.fromisoformat(value)
    return value

@app.template_filter('strftime')
def strftime(value, fmt='%Y-%m-%d'):
    """
    Кастомный фильтр для форматирования даты/времени в Jinja2.
    :param value: Значение даты (объект datetime или строка)
    :param fmt: Формат даты (по умолчанию '%Y-%m-%d')
    :return: Отформатированная строка даты
    """
    if isinstance(value, datetime):
        return value.strftime(fmt)
    elif isinstance(value, str):
        # Пробуем разобрать строку как объект datetime
        dt = datetime.fromisoformat(value)
        return dt.strftime(fmt)
    else:
        return ""


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
    mail = request.form['mail']  # mail → email (для единообразия)
    password = request.form['password']

    # Хешируем пароль перед сохранением
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    conn = get_db_connection()
    cur = conn.cursor()

    # Автоматически устанавливаем роль пользователя равной 1
    cur.execute('''
        INSERT INTO users(user_name, email, password_hash, role_id)
        VALUES (%s, %s, %s, 1);  -- Ставим роль 1 по умолчанию
    ''', (user_name, mail, hashed_password))

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
                session["user_role"] = user[6]
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

@app.route("/api/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Получаем пользователя и проверяем наличие сессии
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'message': 'Требуется авторизация'}), 401

        # Можно дополнительно проверить права пользователя, если это важно

        # Выполняем удаление товара
        cur.execute("DELETE FROM products WHERE product_id=%s", (product_id,))
        deleted_rows = cur.rowcount

        if deleted_rows > 0:
            conn.commit()
            return jsonify({'message': 'Товар успешно удалён'})
        else:
            return jsonify({'message': 'Товар не найден'}), 404
    except Exception as e:
        print(f'Ошибка при удалении товара: {e}')
        return jsonify({'message': 'Ошибка при удалении товара'}), 500
    finally:
        cur.close()
        conn.close()

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
        count = int(request.form.get("count", 1))  # Количество товара (по умолчанию 1)
        
        # Проверка наличия аутентифицированного пользователя
        if not session.get("user_id"):
            flash("Необходимо войти в систему.")
            return redirect(url_for("login"))  # Перенаправляем на страницу авторизации
            
        # Добавляем товар в корзину любого зарегистрированного пользователя
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO cart (product_id, user_id, count) VALUES (%s, %s, %s)",
                (product_id, session.get("user_id"), count)
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
        # Получаем данные из формы
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        
        # Загрузка фото
        file = request.files.get('photo')
        photo_path = None
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            
            # Определяем директорию для сохранения файлов
            upload_folder = 'uploads'
            os.makedirs(upload_folder, exist_ok=True)  # Создаем директорию, если её нет
            
            # Полный путь для сохранения файла
            full_path = os.path.join(upload_folder, filename)
            
            # Сохраняем файл
            file.save(full_path)
            
            # Записываем относительный путь в базу данных
            photo_path = '/' + full_path.lstrip('/')
        
        # Проверяем роль пользователя
        user_role = session.get('user_role')  # Предполагается, что роль хранится в сессии
        if user_role is None or user_role != 2:  # Роль администратора равна 2
            flash('Доступ ограничен. Товар могут добавлять только администраторы.', category='danger')
            return redirect(url_for('home'))  # Перенаправляем на главную страницу
        
        try:
            conn = get_db_connection()  # Подключаемся к базе данных
            cur = conn.cursor()
            
            # Выполняем вставку данных
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
        flash('Вы не имеете полномочий для редактирования товаров.', 'danger')
        return redirect(url_for('home'))
    else:
        if request.method == 'GET':  # Показываем форму редактирования товара
            cur.execute("SELECT product_id, title, description, price, image_url FROM products WHERE product_id=%s;", (id,))
            product = cur.fetchone()
            if not product:
                flash('Товар не найден.', category='warning')
                return redirect(url_for('home'))
            else:
                # Преобразуем кортеж в словарь для простоты использования в шаблоне
                product_data = {
                    'product_id': product[0],  # Первичный ключ товара
                    'title': product[1],      # Название товара
                    'description': product[2], # Описание товара
                    'price': product[3],      # Цена товара
                    'image_url': product[4]   # Адрес изображения
                }
                return render_template('edit_product.html', product=product_data)

        elif request.method == 'POST':  # Обрабатываем отправленные данные
            title = request.form.get('title', False)
            description = request.form.get('description', False)
            price = request.form.get('price', False)
            image_file = request.files.get('image_url')
            
            updates = []
            update_values = []

            # Собираем обновление полей, только тех, которые были изменены
            if title:
                updates.append("title=%s")
                update_values.append(title)
                
            if description:
                updates.append("description=%s")
                update_values.append(description)
                
            if price:
                updates.append("price=%s")
                update_values.append(float(price))  # Конвертировать цену в число

            # Загрузка нового изображения
            if image_file and image_file.filename != '':
                filename = secure_filename(image_file.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image_file.save(image_path)
                new_image_url = "/uploads/" + filename
                updates.append("image_url=%s")
                update_values.append(new_image_url)

            # Формирование SQL-запроса
            if len(updates) > 0:
                sql_query = f"""
                    UPDATE products SET {','.join(updates)} WHERE product_id=%s;
                """
                update_values.append(id)
                cur.execute(sql_query, tuple(update_values))
                conn.commit()
                flash('Товар успешно обновлен!', category='success')
            else:
                flash('Ничего не изменилось.', category='info')

            cur.close()
            conn.close()
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
            # Проверка авторизации пользователя
            if not session.get("logged_in"):
                flash('Вы должны войти в систему для оформления заказа.', 'warning')
                return redirect(url_for('login'))
            
            # Извлекаем итоговую сумму из формы
            total_sum_str = request.form.get("total_sum")
            
            # Проверяем наличие и корректность итоговой суммы
            if not total_sum_str:
                flash("Не удалось определить итоговую сумму заказа.", category="danger")
                return redirect(url_for('cart'))
            
            try:
                total_sum = Decimal(total_sum_str)
            except InvalidOperation:
                flash("Неверный формат итоговой суммы.", category="danger")
                return redirect(url_for('cart'))
            
            # Открываем соединение с базой данных
            with get_db_connection() as conn:
                cur = conn.cursor()
                conn.autocommit = False  # Используем транзакционный режим
                
                try:
                    # Выбираем товары из корзины текущего пользователя
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
                    
                    # Если корзина пуста, показываем предупреждение
                    if not cart_items:
                        flash("Корзина пуста. Оформление заказа невозможно.", category="warning")
                        return redirect(url_for('cart'))
                    
                    # Формируем заказы для каждого товара в корзине
                    for product_name, quantity, unit_price in cart_items:
                        total_item_price = unit_price * quantity
                        
                        # Создаем новую запись в таблице orders с автоматически устанавливаемым статусом "В обработке" (статус = 2)
                        cur.execute(
                            """
                            INSERT INTO orders (
                                user_id,
                                product_name,
                                quantity,
                                total_price,
                                status_id,
                                created_at
                            ) VALUES (%s, %s, %s, %s, %s, %s)
                            """,
                            (session["user_id"],
                             product_name,
                             quantity,
                             total_item_price,
                             2,  # Автоматически добавляем статус "В обработке"
                             datetime.now())
                        )
                    
                    # Очищаем корзину после успешного оформления заказа
                    cur.execute(
                        """
                        DELETE FROM cart
                        WHERE user_id = %s
                        """,
                        (session["user_id"],)
                    )
                    
                    # Сохраняем изменения в базу данных
                    conn.commit()
                    
                    flash("Ваш заказ успешно оформлен!", category="success")
                    return redirect(url_for('home'))
                
                except Exception as e:
                    # Откатываем транзакцию в случае ошибок
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
    # Проверка авторизированности пользователя
    if not session.get("logged_in"):
        flash('Вы должны войти в систему.', 'warning')
        return redirect(url_for('login'))
    
    # Получаем идентификатор пользователя из сессии
    user_id = session.get('user_id')
    print(f'Полученное значение user_id: {user_id}')
    
    if not user_id:
        flash('Ошибка идентификации пользователя.', 'danger')
        return redirect(url_for('home'))  # Перенаправляем обратно на главную страницу
    
    # Получаем роль пользователя из базы данных
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute('SELECT role_id FROM users WHERE user_id=%s', (user_id,))
        result = cur.fetchone()
        if result:
            user_role = result[0]
            print('Role_id: ', user_role)
        else:
            user_role = None
    
    # Получаем доступные статусы заказов из базы данных
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute('SELECT status_id, status_name FROM order_status')
        statuses = dict(cur.fetchall())

    # Выбор нужного набора заказов в зависимости от роли пользователя
    if user_role == 2:  # Администратор
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute('''
                SELECT o.order_id, u.user_name, o.product_name, o.quantity, o.total_price, o.created_at, o.status_id
                FROM orders o
                LEFT JOIN users u ON o.user_id = u.user_id
                ORDER BY o.created_at DESC
            ''')
            results = cur.fetchall()
    else:  # Обычный пользователь видит только свои заказы
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute('''
                SELECT o.order_id, u.user_name, o.product_name, o.quantity, o.total_price, o.created_at, o.status_id
                FROM orders o
                INNER JOIN users u ON o.user_id = u.user_id
                WHERE o.user_id = %s
                ORDER BY o.created_at DESC
            ''', (user_id,))
            results = cur.fetchall()

    # Формируем данные для вывода
    orders_data = []
    for row in results:
        order_id, user_name, product_name, quantity, total_price, created_at, status_id = row
        # Проверяем, что created_at - это строка, и преобразуем её в объект datetime
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        formatted_created_at = created_at.strftime('%Y-%m-%d') if created_at else ''
        status_name = statuses.get(status_id, 'Не определен')
        orders_data.append({
            "order_id": order_id,
            "user_name": user_name,  # Добавляем никнейм пользователя
            "product_name": product_name,
            "quantity": quantity,
            "total_price": total_price,
            "created_at": formatted_created_at,
            "status": status_name
        })

    return render_template('orders.html', orders=orders_data, user_role=user_role)

@app.route("/update_order/<int:order_id>", methods=['POST'])
def update_order_status(order_id):
    # Проверяем, что у пользователя есть право изменять статус заказа
    if session.get("user_role") != 2:
        print('Недостаточно прав для изменения статуса заказа.', 'danger')
        return redirect(url_for('get_orders'))

    # Получаем новый статус из формы
    new_status = int(request.form['new_status'])

    # Устанавливаем соединение с базой данных
    conn = get_db_connection()
    cur = conn.cursor()

    # Обновляем статус заказа
    cur.execute(
        '''
        UPDATE orders SET status_id = %s WHERE order_id = %s
        ''',
        (new_status, order_id)
    )

    conn.commit()
    cur.close()
    conn.close()

    flash('Статус заказа успешно обновлён.', 'success')
    return redirect(url_for('get_orders'))

if __name__ == '__main__':
    app.run(debug=True)
