# 📦 Coursework Project Architecture & Logic (DOC PLA) 🎓✨

<p align="center">
  <img src="https://github.com/DokiMakuro4ka/Coursework/raw/main/demo.gif" alt="DEMO GIF" width="100%">
</p>

---

<table>
<tr>
<th align="left">🇷🇺 Русский</th>
<th align="left">en English</th>
</tr>
<tr>
<td valign="top">

## 📝 Описание проекта

**Название:** Coursework  
🚀 Моя первая курсовая работа!  
Задача: создать приложение на Flask, где можно просматривать товары, управлять заказами и иметь 2 типа аккаунтов (пользователь 👤 и администратор 👑).

</td>
<td valign="top">

## 📝 Project Description

**Title:** Coursework  
🚀 My first coursework!  
Task: Create a Flask application where users can view products, manage orders, and have 2 types of accounts (user 👤 and admin 👑).

</td>
</tr>
<tr>
<td valign="top">

## 🎯 Основные требования

- 👀 Просмотр товаров (каталог)
- 📦 Управление заказами (создание, просмотр, изменение)
- 🔑 Два типа аккаунтов: пользователь и администратор
- 💻 Веб-интерфейс (HTML, CSS, JS)
- 🐍 Backend на Python (Flask)

</td>
<td valign="top">

## 🎯 Key Requirements

- 👀 Product catalog viewing
- 📦 Order management (create, view, edit)
- 🔑 Two account types: user & admin
- 💻 Web interface (HTML, CSS, JS)
- 🐍 Python (Flask) backend

</td>
</tr>
<tr>
<td valign="top">

## 🏗️ Архитектура приложения

### 📁 Основные компоненты

- 🐍 Flask-приложение — основной сервер, обрабатывающий запросы
- 🖼️ Шаблоны (templates) — HTML-страницы для отображения информации
- 🎨 Статические файлы (static) — CSS, JS, изображения
- 🗄️ База данных — хранение информации о товарах, заказах, пользователях
- 🔒 Модули авторизации — управление сессиями, права доступа

### 📂 Примерная структура проекта

```
Coursework/
├── app.py
├── models.py
├── forms.py
├── templates/
├── static/
├── requirements.txt
└── README.md
```

</td>
<td valign="top">

## 🏗️ Application Architecture

### 📁 Main Components

- 🐍 Flask app — main server for handling requests
- 🖼️ Templates — HTML pages for displaying information
- 🎨 Static files — CSS, JS, images
- 🗄️ Database — stores products, orders, users
- 🔒 Auth modules — session & permission management

### 📂 Example Project Structure

```
Coursework/
├── app.py
├── models.py
├── forms.py
├── templates/
├── static/
├── requirements.txt
└── README.md
```

</td>
</tr>
<tr>
<td valign="top">

## 🌐 Основные маршруты

- `/` — 🏠 Главная страница
- `/catalog` — 🛍️ Каталог товаров
- `/login` — 🔑 Вход
- `/logout` — 🚪 Выход
- `/register` — 📝 Регистрация
- `/orders` — 📋 Мои заказы
- `/admin` — 🛠️ Панель администратора
- `/admin/orders` — 📦 Управление заказами
- `/admin/products` — 🗂️ Управление товарами

</td>
<td valign="top">

## 🌐 Main Routes

- `/` — 🏠 Home page
- `/catalog` — 🛍️ Product catalog
- `/login` — 🔑 Login
- `/logout` — 🚪 Logout
- `/register` — 📝 Registration
- `/orders` — 📋 My orders
- `/admin` — 🛠️ Admin panel
- `/admin/orders` — 📦 Orders management
- `/admin/products` — 🗂️ Products management

</td>
</tr>
<tr>
<td valign="top">

## 🧩 Логика работы

### 👤 Пользователь

- Регистрируется/логинится
- Просматривает товары
- Оформляет заказы
- Смотрит свои заказы

### 👑 Администратор

- Добавляет, изменяет, удаляет товары
- Управляет всеми заказами
- Может управлять пользователями (по необходимости)

### 🔒 Авторизация и права доступа

- 👀 Гость: просмотр каталога
- 👤 Пользователь: оформление, просмотр заказов
- 👑 Админ: управление товарами и заказами

</td>
<td valign="top">

## 🧩 Logic Flow

### 👤 User

- Registers/logs in
- Views products
- Places orders
- Views own orders

### 👑 Admin

- Adds, edits, deletes products
- Manages all orders
- Manages users (if needed)

### 🔒 Authorization & Permissions

- 👀 Guest: view catalog
- 👤 User: place/view own orders
- 👑 Admin: manage products & orders

</td>
</tr>
<tr>
<td valign="top">

## 🗄️ Работа с данными

- ORM (SQLAlchemy) для работы с базой данных
- **Модели:**
  - User (id, username, password_hash, role)
  - Product (id, name, description, price, image_url)
  - Order (id, user_id, date, status, items)
  - OrderItem (id, order_id, product_id, quantity)

</td>
<td valign="top">

## 🗄️ Data Handling

- ORM (SQLAlchemy) for DB handling
- **Models:**
  - User (id, username, password_hash, role)
  - Product (id, name, description, price, image_url)
  - Order (id, user_id, date, status, items)
  - OrderItem (id, order_id, product_id, quantity)

</td>
</tr>
<tr>
<td valign="top">

## 🖥️ Примеры страниц

- 🛍️ Каталог: список товаров с фото, ценой, кнопкой "Заказать"
- 📝 Заказ: форма выбора товаров, подтверждение
- 🛠️ Админ-панель: таблицы для управления товарами и заказами

</td>
<td valign="top">

## 🖥️ Example Pages

- 🛍️ Catalog: product list with image, price, "Order" button
- 📝 Order: product selection form, confirmation
- 🛠️ Admin panel: tables for managing products and orders

</td>
</tr>
<tr>
<td valign="top">

## ⚙️ Технологии

- Backend: Python, Flask, SQLAlchemy
- Frontend: HTML, CSS, JavaScript
- Database: SQLite/MySQL/PostgreSQL
- Auth: Flask-Login

</td>
<td valign="top">

## ⚙️ Technologies

- Backend: Python, Flask, SQLAlchemy
- Frontend: HTML, CSS, JavaScript
- Database: SQLite/MySQL/PostgreSQL
- Auth: Flask-Login

</td>
</tr>
<tr>
<td valign="top">

## 💡 Возможные доработки

- 📱 API для интеграции
- 🖼️ Загрузка изображений товаров
- 🔎 Фильтрация и поиск
- 📧 Email-уведомления

</td>
<td valign="top">

## 💡 Possible Improvements

- 📱 API for integrations
- 🖼️ Product image uploading
- 🔎 Filtering & search
- 📧 Email notifications

</td>
</tr>
</table>

---
