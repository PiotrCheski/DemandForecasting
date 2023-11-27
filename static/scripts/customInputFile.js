var fileInput = document.getElementById('file-upload');
var fileInfo = document.getElementById('fileInfo');
var submitButton = document.getElementById('submitButton');
// Run the initial check when the page loads
document.addEventListener('DOMContentLoaded', function() {
    updateFileInfo();
});

function updateFileInfo() {
    // Check if there are files selected
    if (fileInput.files.length > 0) {
        fileInfo.textContent = fileInput.files[0].name;
        submitButton.style.backgroundColor = '';
        submitButton.style.pointerEvents = '';
    } else {
        fileInfo.textContent = 'Nie wybrano pliku';
        submitButton.style.backgroundColor = '#8a7e7d';
        submitButton.style.pointerEvents = 'none';
        // You can leave the style as is or customize it further
    }
}
fileInput.addEventListener('change', updateFileInfo);

