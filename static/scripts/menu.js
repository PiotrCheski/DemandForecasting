
// Wyświetlenie menu poprzez kliknięcie toggleMenu
function toggleMenu() {
    var menuOverlay = document.getElementById("menuOverlay");
    menuOverlay.classList.toggle("show-menu");
}
// Zamknięcie menu poprzez kliknięcie dowolnego obszaru poza menu
document.addEventListener("click", function(event) {
    var menuOverlay = document.getElementById("menuOverlay");
    var hamburgerMenu = document.getElementById("hamburgerMenu");

    if (!menuOverlay.contains(event.target) && !hamburgerMenu.contains(event.target)) {
        menuOverlay.classList.remove("show-menu");
    }
});
