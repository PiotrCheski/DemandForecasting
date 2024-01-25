// Create variables
var fileInput = document.getElementById('file-upload');
var fileInfo = document.getElementById('fileInfo');
var submitButton = document.getElementById('submitButton');

// Call the "updateFileInfo" function when the page is loaded
document.addEventListener('DOMContentLoaded', function() {
    updateFileInfo();
});

// Function responsible for displaying text in the field with id=="fileInfo"
function updateFileInfo() {
    // If a file is selected
    if (fileInput.files.length == 1) {
        fileInfo.textContent = fileInput.files[0].name;
        submitButton.style.backgroundColor = '';
        submitButton.style.pointerEvents = '';
    } else {
        fileInfo.textContent = 'No file selected';
        submitButton.style.backgroundColor = '#8a7e7d';
        submitButton.style.pointerEvents = 'none';
    }
}
// The "updateFileInfo" function is called when the "fileInput" state changes
fileInput.addEventListener('change', updateFileInfo);
