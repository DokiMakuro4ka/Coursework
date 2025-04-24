document.addEventListener("DOMContentLoaded", async () => {
    const response = await fetch('/api/products'); // Запрашиваем список товаров от сервера
    const data = await response.json();

    const productListSection = document.querySelector('#product-list');

    for (const product of data.products) {
        let truncatedDescription = truncateText(product.description, 100); // Ограничение описания до 100 символов
        createProductCard(product.title, truncatedDescription, product.price, product.image_url, product.description, `/product/${product.product_id}`, product.product_id);
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
    descElement.innerHTML = `<span class="description-truncated" onclick="showMore(this, '${fullDescription.replace(/'/g, "\\'")}')">${description}</span>`;

    // Кнопки редактирования и удаления
    const editButton = document.createElement('button');
    editButton.className = 'edit-button';
    editButton.textContent = 'Редактировать';
    editButton.onclick = function() { editProduct(productId); };

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
function showMore(element, fullDescription) {
    element.style.whiteSpace = 'normal';   // Отменяем ограничение строки
    element.style.overflow = '';           // Показываем полный текст
    element.textContent = fullDescription; // Полностью показываем описание
}

// Редактируем товар
async function editProduct(productId) {
    const response = await fetch(`/api/edit_product?id=${productId}`);
    window.location.href = '/templates/edit_product.html'; // Перенаправление на форму редактирования продукта
}

// Удаляем товар
async function deleteProduct(productId) {
    if (!confirm(`Вы уверены, что хотите удалить продукт №${productId}?`)) return;

    const response = await fetch(`/api/delete_product`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({id: productId})
    });

    const result = await response.json();
    alert(result.message); // Оповещаем пользователя о результате операции
    location.reload(); // Обновляем страницу, чтобы изменения вступили в силу
}

document.addEventListener("DOMContentLoaded", () => {
    // Отправка формы добавления товара
    document.querySelector("#add-product-form")?.addEventListener("submit", async event => {
        event.preventDefault(); // Предотвращаем обычную отправку формы

        const formData = new FormData(event.target);

        const response = await fetch('/api/add_product', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        alert(result.message); // Оповещаем пользователя о результате операции
        location.reload(); // Обновляем страницу, чтобы увидеть новые товары
    });
});