import os
import pandas as pd
from flask import Flask, render_template, redirect, url_for, request
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Funkcja opisująca główną stronę 
@app.route("/", methods=["GET"])
def index():
    return render_template("startingpage.html")

# Funkcja dotycząca przesyłu pliku .csv
@app.route("/send_file", methods=["POST"])
def senf_file():
    if 'file' in request.files:
        file = request.files['file']
        print(file)
        filename = secure_filename(file.filename)
        print(filename)
        file.save("static/uploads/"+filename)
        return redirect("/")
    else:
        return "No file"

# Obsłużenie żądania przycisku open_how_we_work
@app.route("/open_how_we_work", methods=["POST"])
def open_how_we_work():
    return redirect(url_for("howWeWork"))

# Funkcja opisująca stronę hoWeWork
@app.route("/how_we_work", methods=["GET"])
def howWeWork():
    return render_template("howWeWork.html")

# Obsłużenie żądania przycisku open_how_we_work
@app.route("/open_choose_file", methods=["POST"])
def open_choose_file():
    return redirect(url_for("chooseFile"))

# Funkcja opisująca stronę hoWeWork
@app.route("/choose_file", methods=["GET"])
def chooseFile():
    return render_template("chooseFile.html")

# Obsłużenie żądania przycisku open_how_we_work
@app.route("/explore_your_files", methods=["POST"])
def explore_your_files():
    return redirect(url_for("explore_files"))

# Funkcja opisująca stronę hoWeWork
@app.route("/explore_files", methods=["GET", "POST"])
def explore_files():
    # Lista plików w folderze static/uploads
    files = os.listdir("static/uploads")

    return render_template("exploreFiles.html", files=files)

@app.route("/explore_files/<file_name>")
def see_specific_file(file_name):

    # Określenie ścieżki do pliku
    file_path = 'static/uploads/' + file_name

    # Wczytanie danych przez bilbiotekę pandas
    data = pd.read_csv(file_path)

    # Obliczenie średniej
    average = round(calculate_avg(data))

    return render_template("specificFile.html", 
                           file_name=file_name, 
                           data=data.to_dict(orient='records'),
                           average=average)


@app.route('/delete_file/<file_name>', methods=['GET', 'POST'])
def delete_file(file_name):
    file_path = 'static/uploads/' + file_name
    os.remove(file_path)
    return redirect(url_for("explore_files"))

# Funkcja licząca średnią z zestawu danych dla kolumny "Wartosci"
def calculate_avg(data):
    return data["Wartosci"].mean()

if __name__ == "__main__":
    app.run(debug=True)