document.addEventListener("DOMContentLoaded", async () => {
    const response = await fetch('/api/products'); // Запрашиваем список товаров от сервера
    const data = await response.json();

    // Получаем роль пользователя из ответа сервера
    const userRole = data.user_role || '1';

    const productListSection = document.querySelector('#product-list');

    for (const product of data.products) {
        let truncatedDescription = truncateText(product.description, 10); // Ограничение описания до 10 символов
        createProductCard(
            product.title,
            truncatedDescription,
            product.price,
            product.image_url,
            product.description,
            `/product/${product.product_id}`, // Правильная экранировка
            product.product_id,
            userRole // Передаем роль пользователя в функцию
        );
    }
});

// Функция обрезания текста до заданной длины с добавлением многоточия
function truncateText(text, limit) {
    return text.length > limit ? `${text.slice(0, limit)}...` : text; // Исправлено экранирование
}

// Создаем карточку товара
function createProductCard(title, description, price, imgUrl, fullDescription, link, productId, userRole) {
    const cardElement = document.createElement('div');
    cardElement.className = 'product-card';

    // Картинка товара с ссылкой
    const aImgElement = document.createElement('a');
    aImgElement.href = link;
    aImgElement.target = '_self';

    const imgElement = document.createElement('img');
    imgElement.src = imgUrl;
    imgElement.alt = title;
    imgElement.className = 'product-image';

    aImgElement.appendChild(imgElement);

    // Заголовок товара с ссылкой
    const aTitleElement = document.createElement('a');
    aTitleElement.href = link;
    aTitleElement.target = '_self';

    const titleElement = document.createElement('h3');
    titleElement.textContent = title;
    aTitleElement.appendChild(titleElement);

    // Цена товара
    const priceElement = document.createElement('p');
    priceElement.className = 'product-price';
    priceElement.textContent = `${price} руб.`; // Исправил форматы строки

    // Описание товара с кнопкой "ещё"
    const descElement = document.createElement('p');
    descElement.className = 'truncated-description';
    descElement.textContent = description;
    descElement.setAttribute('data-full-text', fullDescription);

    // Добавляем элементы в карточку товара
    cardElement.appendChild(aImgElement);
    cardElement.appendChild(aTitleElement);
    cardElement.appendChild(priceElement);
    cardElement.appendChild(descElement);

    // Только админам показываем кнопки редактирования и удаления
    if (userRole == '2') {
        // Кнопка редактирования
        const editButton = document.createElement('button');
        editButton.className = 'edit-btn';
        editButton.textContent = 'Редактировать';
        editButton.dataset.id = productId;
        editButton.onclick = function(event) {
            event.preventDefault();
            
            // Получение текущего идентификатора товара
            const currentProductId = this.dataset.id;
            
            // Формирование URL перехода
            const editUrl = '/edit_product/' + currentProductId;
            
            // Переход на страницу редактирования
            window.location.href = editUrl;
        };

        // Кнопка удаления
        const deleteButton = document.createElement('button');
        deleteButton.className = 'delete-button';
        deleteButton.textContent = 'Удалить';
        deleteButton.onclick = function() {
            deleteProduct(productId); // Вызов функции удаления
        };

        // Добавляем кнопки в карточку товара
        cardElement.appendChild(editButton);
        cardElement.appendChild(deleteButton);
    }

    // Вставляем карточку в контейнер списка товаров
    document.querySelector('#product-list').appendChild(cardElement);
}

// Открывает полное описание товара при клике на кнопку "ещё"
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.truncated-description').forEach((descElement) => {
        descElement.addEventListener('click', function(event) {
            event.stopPropagation(); // предотвращаем всплытие события

            if (!this.hasAttribute('data-expanded')) {
                const fullText = this.getAttribute('data-full-text');
                this.textContent = fullText;
                this.setAttribute('data-expanded', true);
            }
        });
    });
});


//Функция для редактирования товара
function EditButton(button) {
    button.addEventListener('click', function(event) {
        event.preventDefault();
        
        // Получаем productId из аттрибута data-id
        var productId = this.dataset.id;
        
        // Формируем URL
        var editUrl = '/edit_product/' + productId;
        
        // Переходим на соответствующую страницу
        window.location.href = editUrl;
    });
}

// Функция удаления товара (ее реализация зависит от особенностей вашей архитектуры)
function deleteProduct(productId) {
    if (window.confirm('Вы уверены, что хотите удалить этот товар?')) {
        fetch(`/api/products/${productId}`, { // Используем шаблонную строку
            method: 'DELETE'
        })
        .then(response => {
            if (response.ok) {
                alert('Товар успешно удалён!');
                location.reload(); // Обновляем страницу после успешной операции
            } else {
                alert('Ошибка при удалении товара.');
            }
        })
        .catch(error => {
            console.error('Ошибка:', error); // Записываем ошибку в консоль
            alert('Ошибка при удалении товара.'); // Сообщаем пользователю об ошибке
        });
    }
}