// Funkcja do obsługi zaznaczania checkboxów
function checkProducts() {

    // Pobranie wszystkich checkboxów z pola "Wybierz kategorie", które są zaznaczone
    var selectedCategories = document.querySelectorAll('input[name="category"]:checked');

    // Dla każdej zaznaczonej kategorii
    selectedCategories.forEach(function (category) {
        // Pobranie odpowiadających produktów dla tej kategorii ze słownika "categoryProductDict"
        var products = categoryProductDict[category.value];

        // Dla każdego produktu
        products.forEach(function (product) {
            // Znalezienie checkboxa tego produktu i zazanczenie go
            var productCheckbox = document.querySelector('input[name="product"][value="' + product + '"]');
            if (productCheckbox) {
                productCheckbox.checked = true;
            }
        });
    });
}

// Pobranie wszystkich checkboxów z pola "Wybierz kategorie", które są niezaznaczone
var categoryCheckboxes = document.querySelectorAll('input[name="category"]:not(:checked)');

// Jeśli któryś z checkboxów niezaznaczonych zostanie zaznaczony nastąpi wywołanie funkcji "checkProducts"
categoryCheckboxes.forEach(function (checkbox) {
    checkbox.addEventListener('change', checkProducts);
});

// Funkcja wywoływana jest przy odznaczeniu danego produktu
function uncheckCategory(checkbox) {
    // Jeśli checkbox nie jest już zaznaczony
    if (!checkbox.checked) {
        // Określenie produktu, którego dany checkbox dotyczy
        var productValue = checkbox.value;
        // Stworzenie zmiennej "category"
        var category;
        // Znalezienie, która kategoria odpowiada temu produktowi
        for (var key in categoryProductDict) {
            if (categoryProductDict[key].includes(productValue)) {
                category = key;
                break;
            }
        }
        // Znalezienie checkboxa dla odszukanej wcześniej kategorii
        var categoryCheckbox = document.querySelector('input[name="category"][value="' + category + '"]');
        // Odznaczenie tej kategorii
        if (categoryCheckbox) {
            categoryCheckbox.checked = false;
        }
    }
}