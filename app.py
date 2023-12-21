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
from dateutil.relativedelta import relativedelta


app = Flask(__name__)

# Stworzenie zmiennej csrf wykorzystywanej do obrony przed atakami CSRF
csrf = CSRFProtect(app)

# Ustawienie trybu pracy biblioteki matplotlib
matplotlib.use('Agg')

# Określenie jakie pliki (z jakim rozszerzeniem) mogą być przesyłane pliki
ALLOWED_EXTENSIONS = {'csv'}

# Określenie folderu, do którego przesyłane będą pliki
UPLOAD_FOLDER = 'static/uploads/'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Sekret wykorzystywany podczas przesyłu formularzy w kontekście obrony przed atakami CSRF
app.config['SECRET_KEY'] = 'aL7#Veiv@bCgm5fB@J8&@GxNS95T^XEPe9DANxt4Z9v*K$@^Fg7uCcH'

# Funkcja odpowiadająca za wyświetlenie strony głównej
@app.route("/")
def index():
    return render_template("startingPage.html")

# Funkcja odpowiedzialna za sprawdzenie czy przesyłany plik jest plikiem .csv
def is_allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Funkcja odpowiedzialna za sprawdzenie czy przesyłany plik .csv ma właściwą strukturę
def is_valid_csv(file_path):
    df = pd.read_csv(file_path)
    expected_columns = ['Data transakcji', 'Kategoria', 'Produkt', 'Liczba', 'Cena', 'Wartość']
    
    # Sprawdzenie czy wszystkie spodziewane kolumny są w pliku CSV
    if set(expected_columns).issubset(df.columns):
        return True
    else:
        # Określenie brakujących kolumn
        missing_cols = list(set(expected_columns) - set(df.columns))
        return missing_cols

# Funkcja dotycząca przesyłu pliku .csv
@app.route("/send_file", methods=["POST"])
def send_file():
    if 'file' in request.files:
        file = request.files['file']
        # Sprawdzenie czy przesyłany plik jest plikiem .csv
        if is_allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            validation_result = is_valid_csv(file_path)
            if validation_result == True:
                return redirect(url_for("exploreFiles"))
            else:
                return render_template("errorMessage.html", 
                           filename=filename,
                           validation_result=validation_result
                           )
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
def exploreFiles():
    # Lista plików w folderze static/uploads
    files = os.listdir("static/uploads")
    return render_template("exploreFiles.html", files=files)

# Funkcja odpowiadająca za wyświetlenie strony dla wybranego, wcześniej przesłanego pliku .csv
@app.route("/explore_file/<file_name>")
def see_specific_file_new(file_name):
    # Określenie ścieżki do pliku
    file_path = 'static/uploads/' + file_name

    # Wczytanie danych przez bilbiotekę pandas
    data = pd.read_csv(file_path)

    # Określenie kategorii w pliku .csv
    unique_categories = data['Kategoria'].unique()
    # Określenie produktów w pliku .csv
    unique_products = data['Produkt'].unique()
    # Określenie relacji kategoria-produkt
    unique_pairs = data.groupby(['Kategoria', 'Produkt']).size().reset_index(name='count')

    # Stworzenie słownika zawierającego kategorie i odpowiadające im produkty
    category_product_dict = {}
    for row in unique_pairs.itertuples(index=False):
        category = row[0]
        product = row[1]
        if category not in category_product_dict:
            category_product_dict[category] = []
        category_product_dict[category].append(product)

    data['Data transakcji'] = pd.to_datetime(data['Data transakcji'])
    # Określenie najmniejszego roku
    min_year = data['Data transakcji'].min().year
    # Określenie największego roku
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
    # Przechwycenie danych zaznaczonych w formularzu
    file_name = request.form['file_name']
    selected_products = request.form.getlist('product')
    start_month = int(request.form.get('start_month'))
    start_year = int(request.form.get('start_year'))
    end_month = int(request.form.get('end_month'))
    end_year = int(request.form.get('end_year'))
    forecast_decision= request.form['choice_forecast']

    # Określenie ścieżki do pliku
    file_path = 'static/uploads/' + file_name

    # Wczytujemy dane przez bibliotekę pandas
    data = pd.read_csv(file_path)
    # Wybieramy tylko wiersze, gdzie kolumna 'Produkt' zawiera wartości z listy selected_products
    data['Data transakcji'] = pd.to_datetime(data['Data transakcji'])
    if end_month == 12:
        end_year += 1
        end_month = 1

    filtered_data = data[
        (data['Data transakcji'] >= pd.Timestamp(start_year, start_month, 1)) &
        (data['Data transakcji'] <= pd.Timestamp(end_year, end_month, 1) - pd.Timedelta(days=1)) &
        (data['Produkt'].isin(selected_products))
    ]
    sums_data = filtered_data.groupby(filtered_data['Data transakcji'].dt.to_period("M"))['Wartość'].sum().reset_index()
    sums_data['Wartość'] = sums_data['Wartość'].round().astype(int)
    data = sums_data

    if forecast_decision == "forecast-no":
        chart_data = generate_chart_new(data)
        return render_template("analysisForecastNo.html",
                                file_name=file_name,
                                data=data.to_dict(orient='records'),
                                selected_products = selected_products,
                                start_month=start_month,
                                start_year=start_year,
                                end_month=end_month,
                                end_year=end_year,
                                chart_data=chart_data,
                            )
    elif forecast_decision == "forecast-average":
         # Wybieramy ostatnią datę w filtered_data
        last_date = filtered_data['Data transakcji'].max()

        # Dodajemy jeden miesiąc do ostatniej daty
        forecast_month = last_date + relativedelta(months=1)
        forecast_month = forecast_month.to_period("M")
        forecast_month = forecast_month.strftime('%Y-%m')

        average = calculate_avg(data)

        data_average = data.copy()
        next_month_index = data_average.index.max() + 1
        data_average.loc[next_month_index, 'Data transakcji'] = data_average['Data transakcji'].max() + 1
        data_average.loc[next_month_index, 'Wartość'] = average
        chart_data = generate_chart_new(data_average, isAverage=True)

        return render_template("analysisForecastAverage.html",
                                file_name=file_name,
                                data=data.to_dict(orient='records'),
                                selected_products=selected_products,
                                chart_data=chart_data,
                                start_month=start_month,
                                start_year=start_year,
                                end_month=end_month,
                                end_year=end_year,
                                average=average,
                                forecast_month=forecast_month
        )
    elif forecast_decision == "forecast-average-moving":
         # Wybieramy ostatnią datę w filtered_data
        last_date = filtered_data['Data transakcji'].max()

        # Dodajemy jeden miesiąc do ostatniej daty
        forecast_month = last_date + relativedelta(months=1)
        forecast_month = forecast_month.to_period("M")
        forecast_month = forecast_month.strftime('%Y-%m')

        if len(data) >= 9:
            moving_avg_n3 = calculate_moving_avg(data, 3)
            moving_avg_n6 = calculate_moving_avg(data, 6)
            moving_avg_n9 = calculate_moving_avg(data, 9)
        elif len(data) >= 6:
            moving_avg_n3 = calculate_moving_avg(data, 3)
            moving_avg_n6 = calculate_moving_avg(data, 6)
        elif len(data) >= 3:
            moving_avg_n3 = calculate_moving_avg(data, 3)
        else:
            return "Zaznacz większy okres danych"

        data_moving = data.copy()
        next_month_index = data_moving.index.max() + 1
        data_moving.loc[next_month_index, 'Data transakcji'] = data_moving['Data transakcji'].max() + 1
        data_moving["n3"] = data_moving["Wartość"]
        data_moving["n6"] = data_moving["Wartość"]
        data_moving["n9"] = data_moving["Wartość"]
        data_moving.loc[next_month_index, 'n3'] = moving_avg_n3
        data_moving.loc[next_month_index, 'n6'] = moving_avg_n6
        data_moving.loc[next_month_index, 'n9'] = moving_avg_n9
        chart_data = generate_chart_new(data_moving, isAverageMoving=True)

        return render_template("analysisForecastAverageMoving.html",
                                file_name=file_name,
                                data=data.to_dict(orient='records'),
                                selected_products=selected_products,
                                start_month=start_month,
                                start_year=start_year,
                                end_month=end_month,
                                end_year=end_year,
                                moving_avg_n3=moving_avg_n3,
                                moving_avg_n6=moving_avg_n6,
                                moving_avg_n9=moving_avg_n9,
                                forecast_month=forecast_month,
                                chart_data=chart_data,
        )

    elif forecast_decision == "forecast-exponential-smoothing":

        # Wybieramy ostatnią datę w filtered_data
        last_date = filtered_data['Data transakcji'].max()

        # Dodajemy jeden miesiąc do ostatniej daty
        forecast_month = last_date + relativedelta(months=1)
        forecast_month = forecast_month.to_period("M")
        forecast_month = forecast_month.strftime('%Y-%m')

        average = calculate_avg(data)
        initial_value = average
        smoothed_values_010 = calculate_exp_smoothing(data, initial_value, 0.10)
        smoothed_values_015 = calculate_exp_smoothing(data, initial_value, 0.15)
        smoothed_values_020 = calculate_exp_smoothing(data, initial_value, 0.20)

        data_exponential_smoothing = data.copy()
        next_month_index = data_exponential_smoothing.index.max() + 1
        data_exponential_smoothing.loc[next_month_index, 'Data transakcji'] = data_exponential_smoothing['Data transakcji'].max() + 1
        data_exponential_smoothing["010"] = data_exponential_smoothing["Wartość"]
        data_exponential_smoothing["015"] = data_exponential_smoothing["Wartość"]
        data_exponential_smoothing["020"] = data_exponential_smoothing["Wartość"]
        data_exponential_smoothing.loc[next_month_index, "010"] = smoothed_values_010
        data_exponential_smoothing.loc[next_month_index, "015"] = smoothed_values_015
        data_exponential_smoothing.loc[next_month_index, "020"] = smoothed_values_020
        chart_data = generate_chart_new(data_exponential_smoothing, isExponentialSmoothing=True)

        return render_template("analysisForecastExponentialSmoothing.html",
                                file_name=file_name,
                                data=data.to_dict(orient='records'),
                                selected_products=selected_products,
                                start_month=start_month,
                                start_year=start_year,
                                end_month=end_month,
                                end_year=end_year,
                                smoothed_values_010=smoothed_values_010,
                                smoothed_values_015=smoothed_values_015,
                                smoothed_values_020=smoothed_values_020,
                                forecast_month=forecast_month,
                                chart_data=chart_data
        )
    elif forecast_decision == "forecast-linear-regression":
        
        # Wybieramy ostatnią datę w filtered_data
        last_date = filtered_data['Data transakcji'].max()

        # Dodajemy jeden miesiąc do ostatniej daty
        forecast_month = last_date + relativedelta(months=1)
        forecast_month = forecast_month.to_period("M")
        forecast_month = forecast_month.strftime('%Y-%m')

        # Określenie parametrów funkcji liniowej y=ax+b odpowiadającej lini trendu przy użyciu regresji liniowej
        a, b = params_linear_regression(data)
        # Określenie prognozy z równania y=ax+b uzysakanego metodą regresji liniowej
        forecast_linear_regression = round(calculate_forecast_linear_regression(data, a, b))

        data_linear_regression = data.copy()
        next_month_index = data_linear_regression.index.max() + 1
        data_linear_regression.loc[next_month_index, 'Data transakcji'] = data_linear_regression['Data transakcji'].max() + 1
        data_linear_regression.loc[next_month_index, 'Wartość'] = forecast_linear_regression
        chart_data = generate_chart_new(data_linear_regression, isLinearRegression=True, a=a, b=b)

        return render_template("analysisForecastLinearRegression.html",
                                file_name=file_name,
                                data=data.to_dict(orient='records'),
                                selected_products=selected_products,
                                start_month=start_month,
                                start_year=start_year,
                                end_month=end_month,
                                end_year=end_year,
                                forecast_month=forecast_month,
                                forecast_linear_regression=forecast_linear_regression,
                                chart_data=chart_data
        )
    
    elif forecast_decision == "forecast-all":
        # Wybieramy ostatnią datę w filtered_data
        last_date = filtered_data['Data transakcji'].max()

        # Dodajemy jeden miesiąc do ostatniej daty
        forecast_month = last_date + relativedelta(months=1)
        forecast_month = forecast_month.to_period("M")
        forecast_month = forecast_month.strftime('%Y-%m')
        average = calculate_avg(data)
        if len(data) >= 9:
            moving_avg_n3 = calculate_moving_avg(data, 3)
            moving_avg_n6 = calculate_moving_avg(data, 6)
            moving_avg_n9 = calculate_moving_avg(data, 9)
        elif len(data) >= 6:
            moving_avg_n3 = calculate_moving_avg(data, 3)
            moving_avg_n6 = calculate_moving_avg(data, 6)
        elif len(data) >= 3:
            moving_avg_n3 = calculate_moving_avg(data, 3)
        else:
            moving_avg_n3 = 0
            moving_avg_n6 = 0
            moving_avg_n9 = 0
        initial_value = average
        smoothed_values_010 = calculate_exp_smoothing(data, initial_value, 0.10)
        smoothed_values_015 = calculate_exp_smoothing(data, initial_value, 0.15)
        smoothed_values_020 = calculate_exp_smoothing(data, initial_value, 0.20)
        a, b = params_linear_regression(data)
        # Określenie prognozy z równania y=ax+b uzysakanego metodą regresji liniowej
        forecast_linear_regression = round(calculate_forecast_linear_regression(data, a, b))
        return render_template("analysisForecastAll.html",
                                file_name=file_name,
                                data=data.to_dict(orient='records'),
                                selected_products=selected_products,
                                start_month=start_month,
                                start_year=start_year,
                                end_month=end_month,
                                end_year=end_year,
                                forecast_month=forecast_month,
                                average=average,
                                moving_avg_n3=moving_avg_n3,
                                moving_avg_n6=moving_avg_n6,
                                moving_avg_n9=moving_avg_n9,
                                smoothed_values_010=smoothed_values_010,
                                smoothed_values_015=smoothed_values_015,
                                smoothed_values_020=smoothed_values_020,
                                forecast_linear_regression=forecast_linear_regression,
        )
def generate_chart_new(data, isAverage=None, isAverageMoving=None, isExponentialSmoothing=None, isLinearRegression=None, a=None, b=None):
    fig, ax = plt.subplots()
    fig.set_size_inches(10, 6)
    fig.set_facecolor('#5c78a3')
    ax.set_facecolor('#5c78a3')

    data['Data transakcji'] = data['Data transakcji'].astype(str)
    plt.bar(data['Data transakcji'], data['Wartość'], color='b', alpha=1.0, zorder=2)

    # Dodanie etykiet i tytułu
    plt.ylabel('Wartość transakcji [zł]')
    plt.title('Łączna wartość transakcji w danym miesięcu')

    if isAverage == True:
        plt.bar(data['Data transakcji'].iloc[-1], data['Wartość'].iloc[-1], color='yellow', zorder=3)
        plt.title('Łączna wartość transakcji w danym miesięcu wraz z prognozą łącznej wartości transakcji w kolejnym miesiącu')
        
    if isAverageMoving==True:
        data['Data transakcji TMP'] = pd.to_datetime(data['Data transakcji'])


        next_month = data['Data transakcji TMP'].iloc[-1] + pd.DateOffset(months=1)
        next_month = next_month.strftime('%Y-%m')

        next_next_month = data['Data transakcji TMP'].iloc[-1] + pd.DateOffset(months=2)
        next_next_month = next_next_month.strftime('%Y-%m')


        # Plot the bars with slightly moved x positions
        ax.bar(data['Data transakcji'].iloc[-1], data['n3'].iloc[-1], color='yellow', zorder=53)
        ax.bar(next_month, data['n6'].iloc[-1], color='red', zorder=3)
        ax.bar(next_next_month, data['n9'].iloc[-1], color='#B15EFF', zorder=3)

    if isExponentialSmoothing==True:
        plt.plot(data['Data transakcji'], data['010'], marker='o', linestyle='-', markersize=5, linewidth=2, color='black')
        plt.scatter(data['Data transakcji'].iloc[-1], data['010'].iloc[-1], color='yellow', s=70, zorder=10)

        plt.plot(data['Data transakcji'], data['015'], marker='o', linestyle='-', markersize=5, linewidth=2, color='black')
        plt.scatter(data['Data transakcji'].iloc[-1], data['015'].iloc[-1], color='red', s=70, zorder=10)

        plt.plot(data['Data transakcji'], data['020'], marker='o', linestyle='-', markersize=5, linewidth=2, color='black')
        plt.scatter(data['Data transakcji'].iloc[-1], data['020'].iloc[-1], color='#B15EFF', s=70, zorder=10) 

    if isLinearRegression==True:
            plt.scatter(data['Data transakcji'].iloc[-1], data['Wartość'].iloc[-1], color='yellow', s=70, zorder=10)
            x_values = range(1, len(data))
            y_values = [a * x + b for x in x_values]
            plt.plot(x_values, y_values, color="red", label="Linia trendu")
    if len(data) >= 12:
        num_labels = 12
        # Calculate the step size to select the labels
        step_size = len(data) // (num_labels - 1)
        # Get the labels and include the last one
        xticks = data['Data transakcji'].iloc[::step_size].tolist() + [data['Data transakcji'].iloc[-1]]
        ax.set_xticks(xticks)
    # Rotate and align the tick labels
    plt.xticks(rotation=45, ha='right')
    plt.grid(True, zorder=1)
    obraz = io.BytesIO()
    plt.savefig(obraz, format='png')
    obraz.seek(0)
    obraz64 = base64.b64encode(obraz.read()).decode()
    plt.close(fig)
    return obraz64

# Funkcja dotycząca usunięcia pliku .csv
@app.route('/delete_file/<file_name>', methods=['GET', 'POST'])
def delete_file(file_name):
    file_path = 'static/uploads/' + file_name
    os.remove(file_path)
    return redirect(url_for("explore_files"))

# Funkcja licząca średnią stałą
def calculate_avg(data):
    return round(data["Wartość"].mean())

# Funkcja licząca średnią ruchomą
def calculate_moving_avg(data, n):
    data = data["Wartość"]
    sum_of_n_values = 0
    for value in data[-n:]:
        sum_of_n_values += value
    moving_average = round(sum_of_n_values / n)
    return moving_average

# Funkcja licząca prognozę metodą wygładzenia wykładniczego
def calculate_exp_smoothing(data, initial_value, alfa):
    data = data["Wartość"]
    smoothed_values = [initial_value] 

    for i in range(1, len(data)+1):
        smoothed_value = round(alfa * data[i-1] + (1 - alfa) * smoothed_values[-1])
        smoothed_values.append(smoothed_value)

    return smoothed_values[-1]

# Funkcja określająca parametry funkcji liniowej y=ax+b odpowiadającej lini trendu przy użyciu regresji liniowej
def params_linear_regression(data):
    n = len(data)
    data["Index"] = np.arange(1, len(data) + 1)
    sum_x = sum(data["Index"])
    sum_y = sum(data["Wartość"])
    sum_x2 = sum(data["Index"]**2)
    sum_xy = sum(data["Index"]*data["Wartość"])
    
    a = (n * sum_xy - sum_x*sum_y) / (n * sum_x2 - sum_x**2)
    b = (sum_y/n) - (a*(sum_x)/n)
    return a, b

# Funkcja określająca prognozę z równania y=ax+b uzysakanego metodą regresji liniowej
def calculate_forecast_linear_regression(data, a, b):
    n = len(data)
    forecast_linear_regression = (n+1) * a + b
    return forecast_linear_regression

if __name__ == "__main__":
    app.run(debug=True)