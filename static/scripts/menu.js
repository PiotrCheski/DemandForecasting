// Create a variable for the rectangular white menu
var menuOverlay = document.getElementById("menuOverlay");

// Create a variable for the menu symbol
var hamburgerMenu = document.getElementById("hamburgerMenu");

// Display the menu by clicking the show-menu
function showMenu() {
    // Add the "show-menu" class
    menuOverlay.classList.add("show-menu");
}

// Close the menu by clicking any area outside the menu
document.addEventListener("click", function(event) {
    // If the user does not click on the menu symbol or inside the white rectangular menu:
    if (!hamburgerMenu.contains(event.target) && !menuOverlay.contains(event.target)) {
        // Remove the "show-menu" class
        menuOverlay.classList.remove("show-menu");
    }
});
