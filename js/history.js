document.addEventListener('DOMContentLoaded', function () {
    const tableBody = document.querySelector('#orders-table tbody');

    fetch('/history')
        .then(response => response.json())
        .then(data => {
            // Очистим старую таблицу
            while(tableBody.firstChild){
                tableBody.removeChild(tableBody.lastChild);
            }

            // Заполним таблицу новыми данными
            data.forEach(order => {
                let row = `
                    <tr>
                        <td>${order.order_id}</td>
                        <td>${order.items.join(', ')}</td>
                        <td>${order.total_cost} руб.</td>
                        <td>${order.created_at}</td>
                        <td>${order.status}</td>
                    </tr>
                `;
                tableBody.insertAdjacentHTML('beforeend', row);
            });
        })
        .catch(error => console.error('Ошибка при получении данных:', error));
});