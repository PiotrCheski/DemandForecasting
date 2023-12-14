# Import bibliotek
import os
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import io, base64
from flask import Flask, render_template, redirect, url_for, request
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect

# Ustawienie trybu pracy biblioteki matplotlib
matplotlib.use('Agg')

# Określenie folderu, do którego przesyłane będą pliki
UPLOAD_FOLDER = 'static/uploads/'

# Określenie jakie pliki (z jakim rozszerzeniem) mogą być przesyłane pliki
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__)
csrf = CSRFProtect(app)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'tutaj_wpisz_dowolny_sekretny_klucz'

# Funkcja odpowiadająca za wyświetlenie strony głównej
@app.route("/")
def index():
    return render_template("startingPage.html")

def is_allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_valid_csv(file_path):
    #df = pd.read_csv(file_path)
    #num_columns = len(df.columns)
    #if num_columns != 2:
    #    return False  
    #for column in df.columns:
    #    num_values = len(df[column])
    #    if num_values != 12:
    #        return False 
    return True

# Funkcja dotycząca przesyłu pliku .csv
@app.route("/send_file", methods=["POST"])
def send_file():
    if 'file' in request.files:
        file = request.files['file']
        if is_allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            if is_valid_csv(file_path):
                return redirect(url_for("explore_files"))
            else:
                return "Niewłaściwa struktura pliku"
        else:
            return "Niewłaściwe rozszerzenie pliku"
    else:
        return "Brak pliku"

# Funkcja odpowiadająca za wyświetlenie strony "Jak działamy"
@app.route("/how_we_work")
def howWeWork():
    return render_template("howWeWork.html")

# Funkcja odpowiadająca za wyświetlenie strony "Prześlij swoje dane"
@app.route("/choose_file")
def chooseFile():
    return render_template("chooseFile.html")

# Funkcja odpowiadająca za wyświetlenie strony "Wyświetl swoje dane"
@app.route("/explore_files")
def explore_files():
    # Lista plików w folderze static/uploads
    files = os.listdir("static/uploads")
    return render_template("exploreFiles.html", files=files)

# Funkcja odpowiadająca za wyświetlenie strony dla wybranego, wcześniej przesłanego pliku .csv
@app.route("/explore_files_new/<file_name>")
def see_specific_file_new(file_name):
    # Określenie ścieżki do pliku
    file_path = 'static/uploads/' + file_name

    # Wczytanie danych przez bilbiotekę pandas
    data = pd.read_csv(file_path)

    unique_categories = data['Kategoria'].unique()
    unique_products = data['Produkt'].unique()

    # Grupowanie danych
    unique_pairs = data.groupby(['Kategoria', 'Produkt']).size().reset_index(name='count')

    # Tworzenie słownika
    category_product_dict = {}
    for row in unique_pairs.itertuples(index=False):
        category = row[0]  # Kategoria
        product = row[1]   # Produkt

        if category not in category_product_dict:
            category_product_dict[category] = []

        category_product_dict[category].append(product)

    data['Data transakcji'] = pd.to_datetime(data['Data transakcji'])
    min_year = data['Data transakcji'].min().year
    max_year = data['Data transakcji'].max().year

    return render_template("seeData.html", 
                           file_name=file_name, 
                           data=data.to_dict(orient='records'),
                           unique_categories=unique_categories,
                           unique_products=unique_products,
                           category_product_dict=category_product_dict,
                           min_year=min_year,
                           max_year=max_year,
                           )

@app.route('/przeslij-dane', methods=['POST'])
def przeslij_dane():
    file_name = request.form['file_name']
    selected_categories = request.form.getlist('category')
    selected_products = request.form.getlist('product')
    start_month = int(request.form.get('start_month'))
    start_year = int(request.form.get('start_year'))
    end_month = int(request.form.get('end_month'))
    end_year = int(request.form.get('end_year'))

    # Określamy ścieżkę do pliku
    file_path = 'static/uploads/' + file_name

    # Wczytujemy dane przez bibliotekę pandas
    data = pd.read_csv(file_path)
    # Wybieramy tylko wiersze, gdzie kolumna 'Produkt' zawiera wartości z listy selected_products
    data['Data transakcji'] = pd.to_datetime(data['Data transakcji'])

    filtered_data = data[
    (data['Data transakcji'] >= pd.Timestamp(start_year, start_month, 1)) &
    (data['Data transakcji'] <= pd.Timestamp(end_year, end_month + 1, 1) - pd.Timedelta(days=1)) &
    (data['Produkt'].isin(selected_products))
    ]
    print(filtered_data)
    return "Dane zostały przesłane pomyślnie!"


@app.route("/explore_files/<file_name>")
def see_specific_file(file_name):

    # Określenie ścieżki do pliku
    file_path = 'static/uploads/' + file_name

    # Wczytanie danych przez bilbiotekę pandas
    data = pd.read_csv(file_path)

    # Obliczenie średniej stałej
    average = calculate_avg(data)

    # Obliczenie średniej ruchomej dla n = 3, n = 6 oraz n = 9
    moving_avg_n3 = calculate_moving_avg(data, 3)
    moving_avg_n6 = calculate_moving_avg(data, 6)
    moving_avg_n9 = calculate_moving_avg(data, 9)

    # Obliczenie prognozy metodą wygładzenia wykładniczego dla α = 0.10, α = 0.15 oraz α = 0.20
    initial_value = average
    smoothed_values_010 = calculate_exp_smoothing(data, initial_value, 0.10)
    smoothed_values_015 = calculate_exp_smoothing(data, initial_value, 0.15)
    smoothed_values_020 = calculate_exp_smoothing(data, initial_value, 0.20)

    # Określenie parametrów funkcji liniowej y=ax+b odpowiadającej lini trendu przy użyciu regresji liniowej
    a, b = params_linear_regression(data)
    # Określenie prognozy z równania y=ax+b uzysakanego metodą regresji liniowej
    forecast_linear_regression = round(calculate_forecast_linear_regression(data, a, b))

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
    data_moving.loc[next_month_index, 'n3'] = moving_avg_n3
    data_moving.loc[next_month_index, 'n6'] = moving_avg_n6
    data_moving.loc[next_month_index, 'n9'] = moving_avg_n9
    chart_moving = generate_chart(data_moving, isAverageMoving=True)

    # Wykres dla prognozy metodą wygładzenia wykładniczego
    data_exponential_smoothing = data.copy()
    next_month_index = data_exponential_smoothing.index.max() + 1
    data_exponential_smoothing.loc[next_month_index, 'Okres'] = data_exponential_smoothing['Okres'].max() + 1
    data_exponential_smoothing["010"] = data_exponential_smoothing["Wartosci"]
    data_exponential_smoothing["015"] = data_exponential_smoothing["Wartosci"]
    data_exponential_smoothing["020"] = data_exponential_smoothing["Wartosci"]
    data_exponential_smoothing.loc[next_month_index, "010"] = smoothed_values_010
    data_exponential_smoothing.loc[next_month_index, "015"] = smoothed_values_015
    data_exponential_smoothing.loc[next_month_index, "020"] = smoothed_values_020
    chart_exponential_smoothing = generate_chart(data_exponential_smoothing, isExponentialSmoothing=True)

    # Wykres dla prognozy metodą regresji liniowej
    data_linear_regression = data.copy()
    next_month_index = data_linear_regression.index.max() + 1
    data_linear_regression.loc[next_month_index, 'Okres'] = data_linear_regression['Okres'].max() + 1
    data_linear_regression.loc[next_month_index, 'Wartosci'] = forecast_linear_regression
    chart_linear_regression = generate_chart(data_linear_regression, isLinearRegression=True, a=a, b=b)

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
                           forecast_linear_regression=forecast_linear_regression, 
                           chart_data=chart_data,
                           chart_average=chart_average,
                           chart_moving=chart_moving,
                           chart_exponential_smoothing=chart_exponential_smoothing,
                           chart_linear_regression=chart_linear_regression
                           )

# Funkcja dotycząca usunięcia pliku .csv
@app.route('/delete_file/<file_name>', methods=['GET', 'POST'])
def delete_file(file_name):
    file_path = 'static/uploads/' + file_name
    os.remove(file_path)
    return redirect(url_for("explore_files"))

# Funkcja licząca średnią stałą
def calculate_avg(data):
    return round(data["Wartosci"].mean())

# Funkcja licząca średnią ruchomą
def calculate_moving_avg(data, n):
    data = data["Wartosci"]
    sum_of_n_values = 0
    for value in data[-n:]:
        sum_of_n_values += value
    moving_average = round(sum_of_n_values / n)
    return moving_average

# Funkcja licząca prognozę metodą wygładzenia wykładniczego
def calculate_exp_smoothing(data, initial_value, alfa):
    data = data["Wartosci"]
    smoothed_values = [initial_value] 

    for i in range(1, len(data)+1):
        smoothed_value = round(alfa * data[i-1] + (1 - alfa) * smoothed_values[-1])
        smoothed_values.append(smoothed_value)

    return smoothed_values[-1]

# Funkcja określająca parametry funkcji liniowej y=ax+b odpowiadającej lini trendu przy użyciu regresji liniowej
def params_linear_regression(data):
    n = len(data)
    sum_x = sum(data["Okres"])
    sum_y = sum(data["Wartosci"])
    sum_x2 = sum(data["Okres"]**2)
    sum_xy = sum(data["Okres"]*data["Wartosci"])
    
    a = (n * sum_xy - sum_x*sum_y) / (n * sum_x2 - sum_x**2)
    b = (sum_y/n) - (a*(sum_x)/n)
    return a, b

# Funkcja określająca prognozę z równania y=ax+b uzysakanego metodą regresji liniowej
def calculate_forecast_linear_regression(data, a, b):
    n = len(data)
    forecast_linear_regression = (n+1) * a + b
    return forecast_linear_regression

#Funkcja odpowiadająca za wygenerowanie wykresów
def generate_chart(data, isAverage=None, isAverageMoving=None, isExponentialSmoothing=None, isLinearRegression=None, a=None, b=None):
    fig, ax = plt.subplots()
    fig.set_size_inches(10, 6)
    fig.set_facecolor('#5c78a3')
    ax.set_facecolor('#5c78a3')

    plt.plot(data['Okres'], data['Wartosci'], marker='o', linestyle='-', markersize=5, linewidth=2, color='black')
    plt.scatter(data['Okres'], data['Wartosci'], color='white', s=50, zorder=10)

    if isAverage==True:
            plt.scatter(data['Okres'].iloc[-1], data['Wartosci'].iloc[-1], color='yellow', s=70, zorder=10)

    if isAverageMoving==True:
        plt.plot(data['Okres'], data['n3'], marker='o', linestyle='-', markersize=5, linewidth=2, color='black')
        plt.scatter(data['Okres'].iloc[-1], data['n3'].iloc[-1], color='yellow', s=70, zorder=10)

        plt.plot(data['Okres'], data['n6'], marker='o', linestyle='-', markersize=5, linewidth=2, color='black')
        plt.scatter(data['Okres'].iloc[-1], data['n6'].iloc[-1], color='red', s=70, zorder=10)

        plt.plot(data['Okres'], data['n9'], marker='o', linestyle='-', markersize=5, linewidth=2, color='black')
        plt.scatter(data['Okres'].iloc[-1], data['n9'].iloc[-1], color='#B15EFF', s=70, zorder=10)

    if isExponentialSmoothing==True:
        plt.plot(data['Okres'], data['010'], marker='o', linestyle='-', markersize=5, linewidth=2, color='black')
        plt.scatter(data['Okres'].iloc[-1], data['010'].iloc[-1], color='yellow', s=70, zorder=10)

        plt.plot(data['Okres'], data['015'], marker='o', linestyle='-', markersize=5, linewidth=2, color='black')
        plt.scatter(data['Okres'].iloc[-1], data['015'].iloc[-1], color='red', s=70, zorder=10)

        plt.plot(data['Okres'], data['020'], marker='o', linestyle='-', markersize=5, linewidth=2, color='black')
        plt.scatter(data['Okres'].iloc[-1], data['020'].iloc[-1], color='#B15EFF', s=70, zorder=10) 

    if isLinearRegression==True:
            plt.scatter(data['Okres'].iloc[-1], data['Wartosci'].iloc[-1], color='yellow', s=70, zorder=10)
            x_values = range(1, len(data) + 1)
            y_values = [a * x + b for x in x_values]
            plt.plot(x_values, y_values, color="red", label="Linia trendu")
            
    plt.xlabel('Okres', fontsize=14)
    plt.ylabel('Wartość', fontsize=14)
    plt.xticks(data['Okres'])
    max_value = max(data['Wartosci'])
    y_ticks = np.arange(0, 1.1*max_value, 50)
    plt.yticks(y_ticks)
    plt.grid(True, linestyle='--', alpha=0.7, color='white')
    obraz = io.BytesIO()
    plt.savefig(obraz, format='png')
    obraz.seek(0)
    obraz64 = base64.b64encode(obraz.read()).decode()
    plt.close(fig)
    return obraz64

if __name__ == "__main__":
    app.run(debug=True)