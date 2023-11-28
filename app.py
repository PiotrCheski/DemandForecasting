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
        return redirect(url_for("explore_files"))
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
    average = calculate_avg(data)

    moving_avg_n3 = calculate_moving_avg(data, 3)
    moving_avg_n6 = calculate_moving_avg(data, 6)
    moving_avg_n9 = calculate_moving_avg(data, 9)

    smoothed_values_010 = calculate_exp_smoothing(data, 0.10)
    smoothed_values_015 = calculate_exp_smoothing(data, 0.15)
    smoothed_values_020 = calculate_exp_smoothing(data, 0.20)


    return render_template("specificFile.html", 
                           file_name=file_name, 
                           data=data.to_dict(orient='records'),
                           average=average,
                           moving_avg_n3=moving_avg_n3,
                           moving_avg_n6=moving_avg_n6,
                           moving_avg_n9=moving_avg_n9,
                           smoothed_values_010=smoothed_values_010,
                           smoothed_values_015=smoothed_values_015,
                           smoothed_values_020=smoothed_values_020)


@app.route('/delete_file/<file_name>', methods=['GET', 'POST'])
def delete_file(file_name):
    file_path = 'static/uploads/' + file_name
    os.remove(file_path)
    return redirect(url_for("explore_files"))

# Funkcja licząca średnią z zestawu danych dla kolumny "Wartosci"
def calculate_avg(data):
    return round(data["Wartosci"].mean())

def calculate_moving_avg(data, n):
    data = data["Wartosci"]
    moving_averages = []

    for i in range(len(data) - n + 1):
        window = data.iloc[i : i + n]
        avg = round(window.mean())
        moving_averages.append(avg)

    return moving_averages

def calculate_exp_smoothing(data, alfa):
    data = data["Wartosci"]
    smoothed_values = [130]  # Initialize with the first value

    for i in range(1, len(data)):
        smoothed_value = round(alfa * data[i] + (1 - alfa) * smoothed_values[-1])
        smoothed_values.append(smoothed_value)

    return smoothed_values

def params_linear_regression(data):
    n = len(data)
    sum_x = sum(data["Okres"])
    sum_y = sum(data["Wartosci"])
    sum_x2 = sum(data["Okres"]**2)
    sum_y2 = sum(data["Wartosci"]**2)
    return n, sum_x, sum_y, sum_x2, sum_y2

if __name__ == "__main__":
    app.run(debug=True)