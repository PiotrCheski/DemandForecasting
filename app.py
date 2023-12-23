# Import zewnętrznych modułów/bibliotek
# Nad każdym modułem/bibliotekę istnieje krótki opis wyjaśniający użycie danej biblioteki

# Moduł umożliwiający zapis/odczyt plików .csv
import os

# Bilbioteka umożliwiająca efektywną pracę z plikami .csv
import pandas as pd

# Biblioteka umożliwiająca generowanie wykresów
import matplotlib
import matplotlib.pyplot as plt

# Moduł umożliwający przekształcenia wykresów z postaci .png na postać umożliwającą przesłanie wykresu do przeglądarki
import io, base64

# Framework umożliwiający tworzenie aplikacji webowych
from flask import Flask, render_template, redirect, url_for, request

# Biblioteka umożliwająca bezpieczny zapis plików na serwerze
from werkzeug.utils import secure_filename

# Moduł umożliwiający obliczenie kolejnej daty
from dateutil.relativedelta import relativedelta

app = Flask(__name__)

# Ustawienie trybu pracy biblioteki matplotlib
matplotlib.use("Agg")

# Określenie jakie pliki (z jakim rozszerzeniem) mogą być przesyłane pliki
ALLOWED_EXTENSIONS = {"csv"}

# Określenie folderu, do którego przesyłane będą pliki
UPLOAD_FOLDER = "static/uploads/"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Funkcja odpowiedzialna za wyświetlenie strony głównej
@app.route("/")
def index():
    return render_template("startingPage.html")

# Funkcja odpowiedzialna za sprawdzenie czy przesyłany plik jest plikiem .csv
def is_allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Funkcja odpowiedzialna za sprawdzenie czy przesyłany plik .csv ma właściwą strukturę
def is_valid_columns(file_path):
    # Wczytanie pliku .csv
    df = pd.read_csv(file_path)

    # Określenie oczekiwanych kolumn w pliku .csv
    expected_columns = ["Data transakcji", "Kategoria", "Produkt", "Liczba", "Cena", "Wartość"]

    # Sprawdzenie czy wszystkie spodziewane kolumny są w pliku CSV
    if set(expected_columns).issubset(df.columns):
        return True
    else:
        # Określenie brakujących kolumn
        missing_cols = list(set(expected_columns) - set(df.columns))
        return missing_cols
    
def is_valid_types(file_path):
    # Wczytanie pliku .csv
    df = pd.read_csv(file_path)

    # Określenie oczekiwanych kolumn w pliku .csv
    expected_columns = ["Data transakcji", "Kategoria", "Produkt", "Liczba", "Cena", "Wartość"]

    # Określenie oczekiwanych typów danych dla każdej z kolumn
    expected_types = {
        "Data transakcji": pd.Timestamp,
        "Kategoria": object,
        "Produkt": object,
        "Liczba": "int64",
        "Cena": "float64",
        "Wartość": "float64"
    }

    # Sprawdzenie czy dane w danej kolumnie mają właściwy typ
    for column in expected_columns:
        if df[column].dtype != expected_types[column]:
            print(f"Type mismatch in column {column}")
            print("Expected type:", expected_types[column])
            print("Actual type:", df[column].dtype)
            return column
    return True

# Funkcja odpowiedzialna za przesłanie pliku .csv
@app.route("/send_file", methods=["POST"])
def send_file():
    if "file" in request.files:
        file = request.files["file"]
        # Sprawdzenie czy przesyłany plik jest plikiem .csv
        if is_allowed_file(file.filename):
            # Usunięcie potencjalnie niebezpieczny elementów z nazwy pliku
            filename = secure_filename(file.filename)
            # Zapis pliku w folderz
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)
            # Sprawdzenie czy w pliku znajdują się właściwe kolumny
            validation_columns_result = is_valid_columns(file_path)
            if validation_columns_result == True:
                # Sprawdzenie czy dane w kolumnach mają właściwe typy danych
                validation_types_result = is_valid_types(file_path)
                if validation_types_result == True:
                    return redirect(url_for("exploreFiles"))
                else:
                    return render_template("errorMessage.html", 
                           filename=filename,
                           validation_types_result=validation_types_result
                        )
            else:
                return render_template("errorMessage.html", 
                           filename=filename,
                           validation_columns_result=validation_columns_result
                        )
        else:
            error_message = "Niewłaściwe rozszerzenie pliku. Oczekiwane rozszerzenie to .csv"
            return render_template("errorMessage.html", 
                           error_message=error_message
                        )
    else:
        error_message = "Brak pliku"
        return render_template("errorMessage.html", 
                           error_message=error_message
                        )

# Funkcja odpowiedzialna za wyświetlenie strony "Jak działamy"
@app.route("/how_we_work")
def howWeWork():
    return render_template("howWeWork.html")

# Funkcja odpowiedzialna za wyświetlenie strony "Prześlij swoje dane"
@app.route("/choose_file")
def chooseFile():
    return render_template("chooseFile.html")

# Funkcja odpowiedzialna za wyświetlenie strony "Wyświetl swoje dane"
@app.route("/explore_files")
def exploreFiles():
    # Określenie jakie pliki znajdują się w folderze static/uploads
    files = os.listdir("static/uploads")
    return render_template("exploreFiles.html", files=files)

# Funkcja odpowiadająca za wyświetlenie strony dla wybranego pliku .csv
@app.route("/explore_file/<file_name>")
def view_file(file_name):
    # Określenie ścieżki do pliku
    file_path = "static/uploads/" + file_name

    # Wczytanie pliku .csv
    data = pd.read_csv(file_path)

    # Określenie kategorii produktów w pliku .csv
    unique_categories = data["Kategoria"].unique()
    # Określenie produktów w pliku .csv
    unique_products = data["Produkt"].unique()
    # Określenie relacji kategoria-produkt
    unique_pairs = data.groupby(["Kategoria", "Produkt"]).size().reset_index(name="count")

    # Stworzenie słownika zawierającego kategorie i odpowiadające im produkty
    category_product_dict = {}
    for row in unique_pairs.itertuples(index=False):
        category = row[0]
        product = row[1]
        if category not in category_product_dict:
            category_product_dict[category] = []
        category_product_dict[category].append(product)

    # Zamiana typu danych w kolumnie "Data transakcji"
    data["Data transakcji"] = pd.to_datetime(data["Data transakcji"])
    # Określenie najwcześniejszego roku
    min_year = data["Data transakcji"].min().year
    # Określenie najpóźniejszego roku
    max_year = data["Data transakcji"].max().year

    return render_template("generateAnalysis.html", 
                           file_name=file_name, 
                           data=data.to_dict(orient="records"),
                           unique_categories=unique_categories,
                           unique_products=unique_products,
                           category_product_dict=category_product_dict,
                           min_year=min_year,
                           max_year=max_year,
                           )

@app.route("/generate_analysis", methods=["POST"])
def generate_analysis():
    # Przechwycenie danych zaznaczonych w formularzu
    file_name = request.form["file_name"]
    selected_products = request.form.getlist("product")
    start_month = int(request.form.get("start_month"))
    start_year = int(request.form.get("start_year"))
    end_month = int(request.form.get("end_month"))
    end_year = int(request.form.get("end_year"))
    forecast_decision= request.form["choice_forecast"]

    # Sprawdzenie warunków granicznych
    # Rok początkowy nie może być później niż rok końcowy
    if start_year > end_year:
        error_message = "Niepoprawny zakres danych. Rok końcowy nie może być przed rokiem początkowym."
        return render_template("errorMessage.html", 
                           error_message=error_message
                        )
    
    # W tym samym roku miesiąc poczatkowy nie może być później niż miesiąc końcowy
    if start_year == end_year and start_month > end_month:
        error_message = "Niepoprawny zakres danych. Miesiąc końcowy nie może być przed miesiącem początkowym."
        return render_template("errorMessage.html", 
                           error_message=error_message
                        )
    
    # Określenie ścieżki do pliku
    file_path = "static/uploads/" + file_name

    # Wczytanie pliku .csv
    data = pd.read_csv(file_path)

    # Zamiana typu danych w kolumnie "Data transakcji"
    data["Data transakcji"] = pd.to_datetime(data["Data transakcji"])

    # Filtracja historii transakcji na podstawie zakresu dat i zaznaczonych produktów
    # Przypadki graniczne w zależności od wyboru dat
    if start_month == end_month and start_month != 12:
        filtered_data = data[
            (data["Data transakcji"] >= pd.Timestamp(start_year, start_month, 1)) &
            (data["Data transakcji"] <= pd.Timestamp(end_year, end_month+1, 1)) &
            (data["Produkt"].isin(selected_products))
        ]
    elif start_month == end_month:
        filtered_data = data[
            (data["Data transakcji"] >= pd.Timestamp(start_year, start_month, 1)) &
            (data["Data transakcji"] <= pd.Timestamp(end_year+1, 1, 1)) &
            (data["Produkt"].isin(selected_products))
        ]
    elif end_month == 12:
        filtered_data = data[
            (data["Data transakcji"] >= pd.Timestamp(start_year, start_month, 1)) &
            (data["Data transakcji"] <= pd.Timestamp(end_year+1, 1, 1)) &
            (data["Produkt"].isin(selected_products))
        ]
    else:
        filtered_data = data[
            (data["Data transakcji"] >= pd.Timestamp(start_year, start_month, 1)) &
            (data["Data transakcji"] <= pd.Timestamp(end_year, end_month+1, 1)) &
            (data["Produkt"].isin(selected_products))
        ]
    
    # Określenie pełnego zakresu dat
    full_date_range = pd.date_range(start=pd.Timestamp(start_year, start_month, 1),
                                    end=pd.Timestamp(end_year, end_month, 1),
                                    freq="MS").to_period("M") 
    filtered_date_range = filtered_data["Data transakcji"].dt.to_period("M")
    
    # Jeśli w analizowanym okresie dla zaznaczonych produktów nie nastąpiła żadna transakcja
    if filtered_date_range.empty:
        error_message = "Dla zaznaczonych produktów w zaznaczonym zakresie czasowym nie zanatowano żadnych transakcji."
        return render_template("errorMessage.html", 
                                error_message=error_message
                            )    

    # Wykonanie operacji sumowania dla poszczególnych miesięcy i zaznaczonych produktów według kolumny "Wartość"
    sums_data = filtered_data.groupby(filtered_data["Data transakcji"].dt.to_period("M"))["Wartość"].sum().reset_index()
    
    # Określenie brakujących miesięcy z wcześńiejszej filtracji
    missing_periods = full_date_range.difference(filtered_date_range)
    # Dla brakujących miesięcy suma z kolumny "Wartość" wynosi 0
    missing_data = pd.DataFrame({"Data transakcji": missing_periods, "Wartość": 0})

    # Połączenie dwóch zestawów danych "sums_data" i "missing_dat" oraz posortowanie nowego zestawu danych według kolumny "Data transakcji"
    sums_data = pd.concat([sums_data, missing_data]).sort_values("Data transakcji")

    # Zaokrąglenie wartości z kolumna "Wartość" oraz zamiana ich typu na int
    sums_data["Wartość"] = sums_data["Wartość"].round().astype(int)

    # Na potrzeby czytelności zestaw danych "sums_data" przypisany jest do zmiennej "data"
    data = sums_data
    
    # Przygotowanie pod prognozę
    # Znalezienie ostatniej (najpóźniejszej) daty
    last_date = filtered_data["Data transakcji"].max()
    # Dodanie jednego miesiąca do ostatniej (najpóźniejszej) daty
    forecast_month = last_date + relativedelta(months=1)
    forecast_month = forecast_month.to_period("M")
    forecast_month = forecast_month.strftime("%Y-%m")

    # Drzewo decyzyjne w zależności od wyboru użytkownika w formularzu
    # Wybór opcji "Chcę tylko wyświetlić dane"
    if forecast_decision == "forecast-no":
        chart_data = generate_chart_new(data)
        return render_template("analysisForecastNo.html",
                                file_name=file_name,
                                data=data.to_dict(orient="records"),
                                selected_products = selected_products,
                                start_month=start_month,
                                start_year=start_year,
                                end_month=end_month,
                                end_year=end_year,
                                chart_data=chart_data,
                            )
    
    # Wybór opcji "Metodą średnich stałych"
    elif forecast_decision == "forecast-average":
        # Obliczenie średniej dla kolumny "Wartość"
        average = calculate_avg(data)
        data_average = data.copy()
        next_month_index = data_average.index.max() + 1
        data_average.loc[next_month_index, "Data transakcji"] = data_average["Data transakcji"].max() + 1
        data_average.loc[next_month_index, "Wartość"] = average

        # Wygenerowanie wykresu
        chart_data = generate_chart_new(data_average, isAverage=True)

        return render_template("analysisForecastAverage.html",
                                file_name=file_name,
                                data=data.to_dict(orient="records"),
                                selected_products=selected_products,
                                chart_data=chart_data,
                                start_month=start_month,
                                start_year=start_year,
                                end_month=end_month,
                                end_year=end_year,
                                average=average,
                                forecast_month=forecast_month
        )
    
    # Wybór opcji "Metodą średnich ruchomych"
    elif forecast_decision == "forecast-average-moving":
        data_moving = data.copy()
        next_month_index = data_moving.index.max() + 1
        data_moving.loc[next_month_index, "Data transakcji"] = data_moving["Data transakcji"].max() + 1
        data_moving["n3"] = data_moving["Wartość"]
        data_moving["n6"] = data_moving["Wartość"]
        data_moving["n9"] = data_moving["Wartość"]

        # Stworzenie słownika przechowującego prognozy
        moving_avgs_dict = {}

        #  Możliwość obliczenia konkretnych średnich ruchomych uzależniona jest od wystarczającej liczby okresów, na podstawie, których można dokonać prognozy
        if len(data) >= 9:
            moving_avg_n3 = calculate_moving_avg(data, 3)
            moving_avg_n6 = calculate_moving_avg(data, 6)
            moving_avg_n9 = calculate_moving_avg(data, 9)
            moving_avgs_dict["n3"] = moving_avg_n3
            moving_avgs_dict["n6"] = moving_avg_n6
            moving_avgs_dict["n9"] = moving_avg_n9
            data_moving.loc[next_month_index, "n3"] = moving_avg_n3
            data_moving.loc[next_month_index, "n6"] = moving_avg_n6
            data_moving.loc[next_month_index, "n9"] = moving_avg_n9
        elif len(data) >= 6:
            moving_avg_n3 = calculate_moving_avg(data, 3)
            moving_avg_n6 = calculate_moving_avg(data, 6)
            moving_avgs_dict["n3"] = moving_avg_n3
            moving_avgs_dict["n6"] = moving_avg_n6
            data_moving.loc[next_month_index, "n3"] = moving_avg_n3
            data_moving.loc[next_month_index, "n6"] = moving_avg_n6
        elif len(data) >= 3:
            moving_avg_n3 = calculate_moving_avg(data, 3)
            moving_avgs_dict["n3"] = moving_avg_n3
            data_moving.loc[next_month_index, "n3"] = moving_avg_n3
        else:
            error_message = "Zaznacz większy zakres danych."
            return render_template("errorMessage.html", 
                            error_message=error_message
                            )
        
        # Wygenerowanie wykresu
        chart_data = generate_chart_new(data_moving, isAverageMoving=True)

        return render_template("analysisForecastAverageMoving.html",
                                file_name=file_name,
                                data=data.to_dict(orient="records"),
                                selected_products=selected_products,
                                start_month=start_month,
                                start_year=start_year,
                                end_month=end_month,
                                end_year=end_year,
                                moving_avgs_dict=moving_avgs_dict,
                                forecast_month=forecast_month,
                                chart_data=chart_data
        )
    
    # Wybór opcji " Metodą wykładzenia wykładniczego"
    elif forecast_decision == "forecast-exponential-smoothing":
        average = calculate_avg(data)
        initial_value = average
        smoothed_values_010 = calculate_exp_smoothing(data, initial_value, 0.10)
        smoothed_values_015 = calculate_exp_smoothing(data, initial_value, 0.15)
        smoothed_values_020 = calculate_exp_smoothing(data, initial_value, 0.20)

        data_exponential_smoothing = data.copy()
        next_month_index = data_exponential_smoothing.index.max() + 1
        data_exponential_smoothing.loc[next_month_index, "Data transakcji"] = data_exponential_smoothing["Data transakcji"].max() + 1
        data_exponential_smoothing["010"] = data_exponential_smoothing["Wartość"]
        data_exponential_smoothing["015"] = data_exponential_smoothing["Wartość"]
        data_exponential_smoothing["020"] = data_exponential_smoothing["Wartość"]
        data_exponential_smoothing.loc[next_month_index, "010"] = smoothed_values_010
        data_exponential_smoothing.loc[next_month_index, "015"] = smoothed_values_015
        data_exponential_smoothing.loc[next_month_index, "020"] = smoothed_values_020

        # Wygenerowanie wykresu
        chart_data = generate_chart_new(data_exponential_smoothing, isExponentialSmoothing=True)

        return render_template("analysisForecastExponentialSmoothing.html",
                                file_name=file_name,
                                data=data.to_dict(orient="records"),
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
    
    # Wybór opcji "Metodą regresji liniowej"
    elif forecast_decision == "forecast-linear-regression":
        # Określenie parametrów funkcji liniowej y=ax+b odpowiadającej lini trendu przy użyciu regresji liniowej
        a, b = params_linear_regression(data)
        # Określenie prognozy z równania y=ax+b uzysakanego metodą regresji liniowej
        forecast_linear_regression = round(calculate_forecast_linear_regression(data, a, b))

        data_linear_regression = data.copy()
        next_month_index = data_linear_regression.index.max() + 1
        data_linear_regression.loc[next_month_index, "Data transakcji"] = data_linear_regression["Data transakcji"].max() + 1
        data_linear_regression.loc[next_month_index, "Wartość"] = forecast_linear_regression

        # Wygenerowanie wykresu
        chart_data = generate_chart_new(data_linear_regression, isLinearRegression=True, a=a, b=b)

        return render_template("analysisForecastLinearRegression.html",
                                file_name=file_name,
                                data=data.to_dict(orient="records"),
                                selected_products=selected_products,
                                start_month=start_month,
                                start_year=start_year,
                                end_month=end_month,
                                end_year=end_year,
                                forecast_month=forecast_month,
                                forecast_linear_regression=forecast_linear_regression,
                                chart_data=chart_data
        )
    # Wybór opcji "Chcę wyświetlić porównanie wyników wszystkich wymienionych wyżej metod"
    elif forecast_decision == "forecast-all":
        # Wykorzystanie wszystkich poprzednio zaprogramowanych metod
        average = calculate_avg(data)
        moving_avgs_dict = {}
        if len(data) >= 9:
            moving_avg_n3 = calculate_moving_avg(data, 3)
            moving_avg_n6 = calculate_moving_avg(data, 6)
            moving_avg_n9 = calculate_moving_avg(data, 9)
            moving_avgs_dict["n3"] = moving_avg_n3
            moving_avgs_dict["n6"] = moving_avg_n6
            moving_avgs_dict["n9"] = moving_avg_n9

        elif len(data) >= 6:
            moving_avg_n3 = calculate_moving_avg(data, 3)
            moving_avg_n6 = calculate_moving_avg(data, 6)
            moving_avgs_dict["n3"] = moving_avg_n3
            moving_avgs_dict["n6"] = moving_avg_n6
            moving_avgs_dict["n9"] = "-" 
        elif len(data) >= 3:
            moving_avg_n3 = calculate_moving_avg(data, 3)
            moving_avgs_dict["n6"] = "-"
            moving_avgs_dict["n9"] = "-" 
        else:
            moving_avgs_dict["n3"] = "-"
            moving_avgs_dict["n6"] = "-"
            moving_avgs_dict["n9"] = "-" 
    
        initial_value = average
        smoothed_values_010 = calculate_exp_smoothing(data, initial_value, 0.10)
        smoothed_values_015 = calculate_exp_smoothing(data, initial_value, 0.15)
        smoothed_values_020 = calculate_exp_smoothing(data, initial_value, 0.20)

        a, b = params_linear_regression(data)

        # Określenie prognozy z równania y=ax+b uzysakanego metodą regresji liniowej
        forecast_linear_regression = round(calculate_forecast_linear_regression(data, a, b))
        return render_template("analysisForecastAll.html",
                                file_name=file_name,
                                data=data.to_dict(orient="records"),
                                selected_products=selected_products,
                                start_month=start_month,
                                start_year=start_year,
                                end_month=end_month,
                                end_year=end_year,
                                forecast_month=forecast_month,
                                average=average,
                                moving_avgs_dict=moving_avgs_dict,
                                smoothed_values_010=smoothed_values_010,
                                smoothed_values_015=smoothed_values_015,
                                smoothed_values_020=smoothed_values_020,
                                forecast_linear_regression=forecast_linear_regression,
        )
    
# Funkcja odpowiedzialna za wygenerowanie wykresów. Poszczególne parametry w funkcji poza "data" uzależnione są od tego dla jakiej metody generowany jest wykres.
def generate_chart_new(data, isAverage=None, isAverageMoving=None, isExponentialSmoothing=None, isLinearRegression=None, a=None, b=None):
    fig, ax = plt.subplots()
    fig.set_size_inches(10, 6)
    fig.set_facecolor("#5c78a3")
    ax.set_facecolor("#5c78a3")

    data["Data transakcji"] = data["Data transakcji"].astype(str)
    plt.bar(data["Data transakcji"], data["Wartość"], color="blue", alpha=1.0, zorder=2)

    plt.ylabel("Wartość transakcji [zł]", color="white", fontsize=15)
    plt.title("Łączna wartość transakcji w danym miesięcu", color="white", fontsize=15)

    if isAverage == True:
        plt.bar(data["Data transakcji"].iloc[-1], data["Wartość"].iloc[-1], color="yellow", zorder=3, label="Prognoza")
        plt.title("Łączna wartość transakcji w danym miesięcu wraz z prognozą łącznej wartości transakcji w kolejnym miesiącu")
        plt.legend()

    if isAverageMoving==True:
        # Poniższe linijki mają jedynie na celu manipulacje biblioteką matplotlib w celu wyświetlenia trzech słupków obok siebie
        # Stworzenie tymczasowego pliku z datami transakcjami
        data["Data transakcji TMP"] = pd.to_datetime(data["Data transakcji"])

        # Określenie miesiąca po miesiącu prognozowanym 
        next_month = data["Data transakcji TMP"].iloc[-1] + pd.DateOffset(months=1)
        next_month = next_month.strftime("%Y-%m")

        # Określenie miesiąca po miesiącu po miesiącu prognozowanym 
        next_next_month = data["Data transakcji TMP"].iloc[-1] + pd.DateOffset(months=2)
        next_next_month = next_next_month.strftime("%Y-%m")

        ax.bar(data["Data transakcji"].iloc[-1], data["n3"].iloc[-1], color="yellow", zorder=53, label="n3")
        ax.bar(next_month, data["n6"].iloc[-1], color="red", zorder=3, label="n6")
        ax.bar(next_next_month, data["n9"].iloc[-1], color="#B15EFF", zorder=3, label="n9")
        ax.legend()

    if isExponentialSmoothing==True:
        # Poniższe linijki mają jedynie na celu manipulacje biblioteką matplotlib w celu wyświetlenia trzech słupków obok siebie
        # Stworzenie tymczasowego pliku z datami transakcjami
        data["Data transakcji TMP"] = pd.to_datetime(data["Data transakcji"])

        # Określenie miesiąca po miesiącu prognozowanym 
        next_month = data["Data transakcji TMP"].iloc[-1] + pd.DateOffset(months=1)
        next_month = next_month.strftime("%Y-%m")

        # Określenie miesiąca po miesiącu po miesiącu prognozowanym 
        next_next_month = data["Data transakcji TMP"].iloc[-1] + pd.DateOffset(months=2)
        next_next_month = next_next_month.strftime("%Y-%m")

        ax.bar(data["Data transakcji"].iloc[-1], data["010"].iloc[-1], color="yellow", zorder=53, label="α = 0,10")
        ax.bar(next_month, data["015"].iloc[-1], color="red", zorder=3, label="α = 0,15")
        ax.bar(next_next_month, data["020"].iloc[-1], color="#B15EFF", zorder=3, label="α = 0,20")
        ax.legend()

    if isLinearRegression==True:
            # Jeśli prognoza wynosi 0 to w takim wypadku wartość przedstawiona będzie za pomocą punktu, zamiast słupka
            if data["Wartość"].iloc[-1] == 0:
                plt.scatter(data["Data transakcji"].iloc[-1], data["Wartość"].iloc[-1], color="yellow", zorder=10)
            else:
                plt.bar(data["Data transakcji"].iloc[-1], data["Wartość"].iloc[-1], color="yellow", zorder=10)

            x_values = range(0, len(data))
            y_values = [a * x + b for x in x_values]
            plt.plot(x_values, y_values, color="red", linewidth=4, label="Linia trendu")
            ax.legend()
    # Jeśli liczba okresów jest większa lub równa 12 to na osi X oznaczonych będzie 12 wartości
    if len(data) >= 12:
        num_labels = 12
        # Określenie odstępu między wartościami
        step_size = len(data) // (num_labels - 1)
        xticks = data["Data transakcji"].iloc[::step_size].tolist() + [data["Data transakcji"].iloc[-1]]
        ax.set_xticks(xticks)
    plt.yticks(color="white", fontsize=11)
    plt.xticks(rotation=45, ha="right", color="white", fontsize=11)
    plt.grid(True, zorder=1)
    obraz = io.BytesIO()
    plt.savefig(obraz, format="png")
    obraz.seek(0)
    obraz64 = base64.b64encode(obraz.read()).decode()
    plt.close(fig)
    return obraz64

# Funkcja odpowiedzialna za usunięcie pliku .csv
@app.route("/delete_file/<file_name>")
def delete_file(file_name):
    file_path = "static/uploads/" + file_name
    os.remove(file_path)
    return redirect(url_for("exploreFiles"))

# Funkcja odpowiedzialna za obliczenie średniej stałej
def calculate_avg(data):
    return round(data["Wartość"].mean())

# Funkcja odpowiedzialna za obliczenie średnich ruchomych
def calculate_moving_avg(data, n):
    data = data["Wartość"]
    sum_of_n_values = 0
    for value in data[-n:]:
        sum_of_n_values += value
    moving_average = round(sum_of_n_values / n)
    return moving_average

# Funkcja odpowiedzialna za obliczenie prognoz metodą wygładzenia wykładniczego
def calculate_exp_smoothing(data, initial_value, alfa):
    data = data["Wartość"]
    smoothed_values = [initial_value] 

    for i in range(1, len(data)+1):
        smoothed_value = round(alfa * data[i-1] + (1 - alfa) * smoothed_values[-1])
        smoothed_values.append(smoothed_value)

    return smoothed_values[-1]

# Funkcja odpowiedzialna za obliczenie parametrów funkcji liniowej y=ax+b odpowiadającej linii trendu
def params_linear_regression(data):
    n = len(data)
    data["Index"] = list(range(1, len(data) + 1))
    sum_x = sum(data["Index"])
    sum_y = sum(data["Wartość"])
    sum_x2 = sum(data["Index"]**2)
    sum_xy = sum(data["Index"]*data["Wartość"])
    
    a = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x**2)
    b = (sum_y - a * sum_x) / n

    return a, b

# Funkcja odpowiedzialna za prognozę wartości z funkcji liniowej y=ax+b odpowiadającej linii trendu
def calculate_forecast_linear_regression(data, a, b):
    n = len(data)+2
    forecast_linear_regression = n * a + b

    # Sytuacja, gdy prognoza jest ujemna, wtedy wartość zamieniana jest na 0
    forecast_linear_regression = max(forecast_linear_regression, 0)
    return forecast_linear_regression

if __name__ == "__main__":
    app.run(debug=True)