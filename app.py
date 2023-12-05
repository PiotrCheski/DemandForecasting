import os
import pandas as pd
from flask import Flask, render_template, redirect, url_for, request
from werkzeug.utils import secure_filename
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import io, base64

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

    # Wykres dla oryginalnego zestawu danych
    chart_data = generate_chart(data)

    # Wykres dla prognozy metodą średniej stałej
    data_average = data.copy()
    next_month_index = data_average.index.max() + 1
    data_average.loc[next_month_index, 'Okres'] = data_average['Okres'].max() + 1
    data_average.loc[next_month_index, 'Wartosci'] = average
    chart_average = generate_chart(data_average, isAverage=True)

    # Wykres dla prognozy metodą średniej ruchomej
    data_moving = data.copy()
    next_month_index = data_moving.index.max() + 1
    data_moving.loc[next_month_index, 'Okres'] = data_moving['Okres'].max() + 1
    data_moving["n3"] = data_moving["Wartosci"]
    data_moving["n6"] = data_moving["Wartosci"]
    data_moving["n9"] = data_moving["Wartosci"]
    
    data_moving.loc[next_month_index, 'n3'] = moving_avg_n3[-1]
    data_moving.loc[next_month_index, 'n6'] = moving_avg_n6[-1]
    data_moving.loc[next_month_index, 'n9'] = moving_avg_n9[-1]
    print(data_moving)
    chart_moving = generate_chart(data_moving, isAverageMoving=True)

    return render_template("specificFile.html", 
                           file_name=file_name, 
                           data=data.to_dict(orient='records'),
                           average=average,
                           moving_avg_n3=moving_avg_n3,
                           moving_avg_n6=moving_avg_n6,
                           moving_avg_n9=moving_avg_n9,
                           smoothed_values_010=smoothed_values_010,
                           smoothed_values_015=smoothed_values_015,
                           smoothed_values_020=smoothed_values_020, 
                           chart_data=chart_data,
                           chart_average=chart_average,
                           chart_moving=chart_moving
                           )


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

def generate_chart(data, isAverage=None, isAverageMoving=None):
    fig, ax = plt.subplots()

    # Set the background color for the figure and axis
    fig.set_facecolor('#5c78a3')
    ax.set_facecolor('#5c78a3')

    # Create a bar chart
    plt.plot(data['Okres'], data['Wartosci'], marker='o', linestyle='-', markersize=5, color='#00cc00')
    if isAverage==True:
            # Color the last point in yellow
            plt.scatter(data['Okres'].iloc[-1], data['Wartosci'].iloc[-1], color='yellow', s=50, zorder=10)
    # Add labels to the axes
    plt.xlabel('Okres', fontsize=14)
    plt.ylabel('Wartość', fontsize=14)

    # Set x-axis ticks to display all values
    plt.xticks(data['Okres'])  # Adjust rotation and ha as needed
    max_value = max(data['Wartosci'])
    y_ticks = np.arange(0, 1.1*max_value, 50)
    plt.yticks(y_ticks)
    plt.grid(True, linestyle='--', alpha=0.7)
    # Save the figure to a BytesIO object
    obraz = io.BytesIO()
    plt.savefig(obraz, format='png')
    obraz.seek(0)
    # Convert the image to base64
    obraz64 = base64.b64encode(obraz.read()).decode()

    # Close the figure to free up resources
    plt.close(fig)

    return obraz64

if __name__ == "__main__":
    app.run(debug=True)