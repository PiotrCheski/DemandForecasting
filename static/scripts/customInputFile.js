var fileInput = document.getElementById('file-upload');
var fileInfo = document.getElementById('fileInfo');
var submitButton = document.getElementById('submitButton');
document.addEventListener('DOMContentLoaded', function() {
    updateFileInfo();
});

function updateFileInfo() {
    if (fileInput.files.length > 0) {
        fileInfo.textContent = fileInput.files[0].name;
        submitButton.style.backgroundColor = '';
        submitButton.style.pointerEvents = '';
    } else {
        fileInfo.textContent = 'Nie wybrano pliku';
        submitButton.style.backgroundColor = '#8a7e7d';
        submitButton.style.pointerEvents = 'none';
    }
}
fileInput.addEventListener('change', updateFileInfo);

