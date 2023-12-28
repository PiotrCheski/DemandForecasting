// Stworzenie zmiennej dotyczącej prostokątnego białego menu
var menuOverlay = document.getElementById("menuOverlay");

// Stworzenie zmiennej dla symbolu menu
var hamburgerMenu = document.getElementById("hamburgerMenu");

// Wyświetlenie menu poprzez kliknięcie toggleMenu
function showMenu() {
    // Dodanie klasy "show-menu"
    menuOverlay.classList.add("show-menu");
}

// Zamknięcie menu poprzez kliknięcie dowolnego obszaru poza menu
document.addEventListener("click", function(event) {
    // Jeśli użytkownik nie naciśnie na symbol menu lub na wnętrze białego prostokątnego menu to:
    if (!hamburgerMenu.contains(event.target) && !menuOverlay.contains(event.target)) {
        // Usuń klasę "show-menu"
        menuOverlay.classList.remove("show-menu");
    }
});
