// Stworzenie zmiennych
var fileInput = document.getElementById('file-upload');
var fileInfo = document.getElementById('fileInfo');
var submitButton = document.getElementById('submitButton');

// Wywołanie funkcji "updateFiloInfo" momencie załadowania strony
document.addEventListener('DOMContentLoaded', function() {
    updateFileInfo();
});

// Funkcja odpowiedzialna za wyświetlany tekst w polu o id=="fileInfo"
function updateFileInfo() {
    // Jeśli wybrano plik
    if (fileInput.files.length == 1) {
        fileInfo.textContent = fileInput.files[0].name;
        submitButton.style.backgroundColor = '';
        submitButton.style.pointerEvents = '';
    } else {
        fileInfo.textContent = 'Nie wybrano pliku';
        submitButton.style.backgroundColor = '#8a7e7d';
        submitButton.style.pointerEvents = 'none';
    }
}
// Funkcja "updateFiloInfo" wywoływana jest przy zmianie stanu "fileInput"
fileInput.addEventListener('change', updateFileInfo);

