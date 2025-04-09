function togglePopup() {
    var menu = document.getElementById("popup-menu");
    if (menu.style.display === "none") {
        menu.style.display = "block"; // Открыть меню
    } else {
        menu.style.display = "none"; // Скрыть меню
    }
}

// Закрытие меню при клике вне логотипа
window.onclick = function(event) {
    var menu = document.getElementById("popup-menu");
    if (!event.target.matches('.logo') && menu.style.display === "block") {
        menu.style.display = "none"; // Скрыть меню при клике вне логотипа
    }
};
