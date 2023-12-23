var submitButton = document.getElementById("submitButton");

// Wywołanie funkcji "updateButtonStatus" w momencie załadowania strony
document.addEventListener('DOMContentLoaded', function() {
    updateButtonStatus();
});

function updateButtonStatus() {
    // Pobranie wszystkich checkboxów z pola "Wybierz produkty"
    var checkboxes = document.querySelectorAll('input[name="product"]');
    // Okreśnie listy zaznaczonych checkboxes
    var checkedCheckboxes = Array.from(checkboxes).filter(function (checkbox) {
        return checkbox.checked;
    });

    // Pobranie wszystkich radiobuttons wśród opcji "Jaką metodę chcesz dokonać prognozy popytu?"
    var radioButtons = document.querySelectorAll('input[name="choice_forecast"]');
    // Okreśnie listy zaznaczonych radiobuttons
    var checkedRadioButtons = Array.from(radioButtons).filter(function (radio) {
        return radio.checked;
    });
    // Jeśli żaden checkbox lub radiobutton nie jest zaznaczony
    if (checkedCheckboxes.length === 0 || checkedRadioButtons.length === 0) {
        // Przycisk jest nieaktywny
        submitButton.disabled = true; 
    } else {
        // Przycisk jest aktywny
        submitButton.disabled = false;
    }
}

// Pobranie wszystkich checkboxów z pola "Wybierz produkty"
var checkboxes = document.querySelectorAll('input[name="product"]');
// Jeśli któryś z checkboxów  zostanie zaznaczony lub odznaczony nastąpi wywołanie funkcji "updateButtonStatus"
checkboxes.forEach(function (checkbox) {
    checkbox.addEventListener("change", updateButtonStatus);
});

// Pobranie wszystkich radiobuttons wśród opcji "Jaką metodę chcesz dokonać prognozy popytu?"
var radioButtons = document.querySelectorAll('input[name="choice_forecast"]');
// Jeśli któryś z radiobuttons zostanie zaznaczony nastąpi wywołanie funkcji "updateButtonStatus"
radioButtons.forEach(function (radio) {
    radio.addEventListener("change", updateButtonStatus);
});