function updateFileInfo() {
    var fileInput = document.getElementById('file-upload');
    var fileInfo = document.getElementById('fileInfo');

    if (fileInput.files.length > 0) {
        fileInfo.textContent = fileInput.files[0].name;
    } else {
        fileInfo.textContent = 'Nie wybrano pliku';
    }
}