document.addEventListener("DOMContentLoaded", async () => {
    const response = await fetch('/api/products'); // Запрашиваем список товаров от сервера
    const data = await response.json();

    const productListSection = document.querySelector('#product-list');

    for (const product of data.products) {
        let truncatedDescription = truncateText(product.description, 100); // Ограничение описания до 100 символов
        createProductCard(
            product.title,
            truncatedDescription,
            product.price,
            product.image_url,
            product.description,
            `/product/${product.product_id}`,
            product.product_id
        );
    }
});

// Функция обрезания текста до заданной длины с добавлением кнопки "Ещё"
function truncateText(text, limit) {
    return text.length > limit ? `${text.slice(0, limit)}...` : text;
}

// Создаем карточку товара
function createProductCard(title, description, price, imgUrl, fullDescription, link, productId) {
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
    priceElement.textContent = `${price} руб`;

    // Описание товара с кнопкой "ещё"
    const descElement = document.createElement('p');
    descElement.className = 'truncated-description';
    descElement.textContent = description;
    descElement.setAttribute('data-full-text', fullDescription);

    // Кнопки редактирования и удаления
    const editButton = document.createElement('button');
    editButton.className = 'edit-btn';
    editButton.textContent = 'Редактировать';
    editButton.dataset.id = productId;
    EditButton(editButton);

    const deleteButton = document.createElement('button');
    deleteButton.className = 'delete-button';
    deleteButton.textContent = 'Удалить';
    deleteButton.onclick = function() { deleteProduct(productId); };

    cardElement.appendChild(aImgElement);
    cardElement.appendChild(aTitleElement);
    cardElement.appendChild(priceElement);
    cardElement.appendChild(descElement);
    cardElement.appendChild(editButton);
    cardElement.appendChild(deleteButton);

    document.querySelector('#product-list').appendChild(cardElement);
}

// Открывает полное описание товара при клике на кнопку "ещё"
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.truncated-description').forEach(function(descriptionElement) {
        descriptionElement.addEventListener('click', function(event) {
            event.stopPropagation(); // предотвратим всплытие события
            const fullText = this.getAttribute('data-full-text');
            this.textContent = fullText;
            this.removeEventListener('click', arguments.callee); // уберем обработчик после открытия полного текста
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
        fetch(`/api/products/${productId}`, {
            method: 'DELETE'
        })
        .then(response => {
            if (response.ok) {
                alert('Товар успешно удалён!');
                location.reload(); // обновляем страницу после успешной операции
            } else {
                alert('Ошибка при удалении товара.');
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
            alert('Ошибка при удалении товара.');
        });
    }
}