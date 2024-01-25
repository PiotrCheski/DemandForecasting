var submitButton = document.getElementById("submitButton");

// Call the "updateButtonStatus" function when the page is loaded
document.addEventListener('DOMContentLoaded', function() {
    updateButtonStatus();
});

function updateButtonStatus() {
    // Get all checkboxes from the "Choose products" field
    var checkboxes = document.querySelectorAll('input[name="product"]');
    // Determine the list of selected checkboxes
    var checkedCheckboxes = Array.from(checkboxes).filter(function (checkbox) {
        return checkbox.checked;
    });

    // Get all radiobuttons among the options "Which method do you want to use for demand forecast?"
    var radioButtons = document.querySelectorAll('input[name="choice_forecast"]');
    // Determine the list of selected radiobuttons
    var checkedRadioButtons = Array.from(radioButtons).filter(function (radio) {
        return radio.checked;
    });
    // If no checkbox or radiobutton is selected
    if (checkedCheckboxes.length === 0 || checkedRadioButtons.length === 0) {
        // The button is disabled
        submitButton.disabled = true; 
    } else {
        // The button is enabled
        submitButton.disabled = false;
    }
}

// Get all checkboxes from the "Choose products" field
var checkboxes = document.querySelectorAll('input[name="product"]');
// If any checkbox is selected or deselected, call the "updateButtonStatus" function
checkboxes.forEach(function (checkbox) {
    checkbox.addEventListener("change", updateButtonStatus);
});

// Get all radiobuttons among the options "Which method do you want to use for demand forecast?"
var radioButtons = document.querySelectorAll('input[name="choice_forecast"]');
// If any radiobutton is selected, call the "updateButtonStatus" function
radioButtons.forEach(function (radio) {
    radio.addEventListener("change", updateButtonStatus);
});
