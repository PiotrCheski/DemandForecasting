// Function to handle checkbox selection
function checkProducts() {

    // Get all checkboxes from the "Select categories" field that are checked
    var selectedCategories = document.querySelectorAll('input[name="category"]:checked');

    // For each selected category
    selectedCategories.forEach(function (category) {
        // Get corresponding products for that category from the "categoryProductDict" dictionary
        var products = categoryProductDict[category.value];

        // For each product
        products.forEach(function (product) {
            // Find the checkbox for that product and check it
            var productCheckbox = document.querySelector('input[name="product"][value="' + product + '"]');
            if (productCheckbox) {
                productCheckbox.checked = true;
            }
        });
    });
}

// Get all checkboxes from the "Select categories" field that are unchecked
var categoryCheckboxes = document.querySelectorAll('input[name="category"]:not(:checked)');

// If any of the unchecked checkboxes is checked, call the "checkProducts" function
categoryCheckboxes.forEach(function (checkbox) {
    checkbox.addEventListener('change', checkProducts);
});

// Function called when a specific product is unchecked
function uncheckCategory(checkbox) {
    // If the checkbox is unchecked
    if (!checkbox.checked) {
        // Identify the product for which this checkbox applies
        var productValue = checkbox.value;
        // Create a variable "category"
        var category;
        // Find which category corresponds to this product
        for (var key in categoryProductDict) {
            if (categoryProductDict[key].includes(productValue)) {
                category = key;
                break;
            }
        }
        // Find the checkbox for the previously found category
        var categoryCheckbox = document.querySelector('input[name="category"][value="' + category + '"]');
        // Uncheck that category
        if (categoryCheckbox) {
            categoryCheckbox.checked = false;
        }
    }
}
