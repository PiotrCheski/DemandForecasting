# External modules/libraries import
# A brief description explaining the usage of each module/library is provided above it.

# Module enabling the saving/reading of .csv files
import os

# Library facilitating efficient work with .csv files
import pandas as pd

# Library enabling the generation of plots
import matplotlib
import matplotlib.pyplot as plt

# Module allowing the transformation of plots from .png format to a format allowing sending the plot to the browser
import io, base64

# Framework enabling the creation of web applications
from flask import Flask, render_template, redirect, url_for, request

# Library allowing secure file saving on the server
from werkzeug.utils import secure_filename

# Module allowing the calculation of the next date
from dateutil.relativedelta import relativedelta

app = Flask(__name__)

# Setting the working mode of the matplotlib library
matplotlib.use("Agg")

# Determining which files (with which extension) can be uploaded
ALLOWED_EXTENSIONS = {"csv"}

# Determining the folder to which files will be uploaded
UPLOAD_FOLDER = "static/uploads/"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Function responsible for displaying the main page
@app.route("/")
def index():
    return render_template("startingPage.html")

# Function responsible for checking if the uploaded file is a .csv file
def is_allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Function responsible for checking if the uploaded .csv file has the correct structure
def is_valid_columns(file_path):
    # Reading the .csv file
    df = pd.read_csv(file_path)

    # Determining the expected columns in the .csv file
    expected_columns = ["Transaction Date", "Category", "Product", "Quantity", "Price", "Value"]

    # Checking if all expected columns are in the CSV file
    if set(expected_columns).issubset(df.columns):
        return True
    else:
        # Determining the missing columns
        missing_cols = list(set(expected_columns) - set(df.columns))
        return missing_cols
    
def is_valid_types(file_path):
    # Reading the .csv file
    df = pd.read_csv(file_path)

    # Determining the expected columns in the .csv file
    expected_columns = ["Transaction Date", "Category", "Product", "Quantity", "Price", "Value"]

    # Determining the expected data types for each column
    expected_types = {
        "Transaction Date": pd.Timestamp,
        "Category": object,
        "Product": object,
        "Quantity": "int64",
        "Price": "float64",
        "Value": "float64"
    }

    # Checking if the data in each column has the correct type
    for column in expected_columns:
        if df[column].dtype != expected_types[column]:
            return column
    return True

# Function responsible for uploading a .csv file
@app.route("/send_file", methods=["POST"])
def send_file():
    if "file" in request.files:
        file = request.files["file"]
        # Check if the uploaded file is a .csv file
        if is_allowed_file(file.filename):
            # Remove potentially dangerous elements from the file name
            filename = secure_filename(file.filename)
            # Save the file to the folder
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)
            # Check if the file contains the correct columns
            validation_columns_result = is_valid_columns(file_path)
            if validation_columns_result == True:
                # Check if the data in the columns has the correct data types
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
            error_message = "Incorrect file extension. Expected extension is .csv"
            return render_template("errorMessage.html", 
                           error_message=error_message
                        )
    else:
        error_message = "No file uploaded"
        return render_template("errorMessage.html", 
                           error_message=error_message
                        )

# Function responsible for displaying the "How We Work" page
@app.route("/how_we_work")
def howWeWork():
    return render_template("howWeWork.html")

# Function responsible for displaying the "Choose Your File" page
@app.route("/choose_file")
def chooseFile():
    return render_template("chooseFile.html")

# Function responsible for displaying the "Explore Your Data" page
@app.route("/explore_files")
def exploreFiles():
    # Determine which files are in the static/uploads folder
    files = os.listdir("static/uploads")
    return render_template("exploreFiles.html", files=files)

# Function responsible for displaying the page for a selected .csv file
@app.route("/explore_file/<file_name>")
def view_file(file_name):
    # Determine the path to the file
    file_path = "static/uploads/" + file_name

    # Read the .csv file
    data = pd.read_csv(file_path)

    # Determine product categories in the .csv file
    unique_categories = data["Category"].unique()
    # Determine products in the .csv file
    unique_products = data["Product"].unique()
    # Determine the relationship between category and product
    unique_pairs = data.groupby(["Category", "Product"]).size().reset_index(name="count")

    # Create a dictionary containing categories and their corresponding products
    category_product_dict = {}
    for row in unique_pairs.itertuples(index=False):
        category = row[0]
        product = row[1]
        if category not in category_product_dict:
            category_product_dict[category] = []
        category_product_dict[category].append(product)

    # Convert the data type in the "Transaction Date" column
    data["Transaction Date"] = pd.to_datetime(data["Transaction Date"])
    # Determine the earliest year
    min_year = data["Transaction Date"].min().year
    # Determine the latest year
    max_year = data["Transaction Date"].max().year

    return render_template("generateAnalysis.html", 
                           file_name=file_name, 
                           data=data.to_dict(orient="records"),
                           unique_categories=unique_categories,
                           unique_products=unique_products,
                           category_product_dict=category_product_dict,
                           min_year=min_year,
                           max_year=max_year,
                           )

# Route responsible for generating analysis
@app.route("/generate_analysis", methods=["POST"])
def generate_analysis():
    # Capture data selected in the form
    file_name = request.form["file_name"]
    selected_products = request.form.getlist("product")
    start_month = int(request.form.get("start_month"))
    start_year = int(request.form.get("start_year"))
    end_month = int(request.form.get("end_month"))
    end_year = int(request.form.get("end_year"))
    forecast_decision = request.form["choice_forecast"]

    # Check boundary conditions
    # The starting year cannot be later than the ending year
    if start_year > end_year:
        error_message = "Invalid data range. The ending year cannot precede the starting year."
        return render_template("errorMessage.html", 
                           error_message=error_message
                        )
    
    # In the same year, the starting month cannot be later than the ending month
    if start_year == end_year and start_month > end_month:
        error_message = "Invalid data range. The ending month cannot precede the starting month."
        return render_template("errorMessage.html", 
                           error_message=error_message
                        )
    
    # Determine the path to the file
    file_path = "static/uploads/" + file_name

    # Read the .csv file
    data = pd.read_csv(file_path)

    # Convert data type in the "Transaction Date" column
    data["Transaction Date"] = pd.to_datetime(data["Transaction Date"])

    # Filter transaction history based on date range and selected products
    # Boundary cases depending on the date choice
    if start_month == end_month and start_month != 12:
        filtered_data = data[
            (data["Transaction Date"] >= pd.Timestamp(start_year, start_month, 1)) &
            (data["Transaction Date"] <= pd.Timestamp(end_year, end_month+1, 1)) &
            (data["Product"].isin(selected_products))
        ]
    elif start_month == end_month:
        filtered_data = data[
            (data["Transaction Date"] >= pd.Timestamp(start_year, start_month, 1)) &
            (data["Transaction Date"] <= pd.Timestamp(end_year+1, 1, 1)) &
            (data["Product"].isin(selected_products))
        ]
    elif end_month == 12:
        filtered_data = data[
            (data["Transaction Date"] >= pd.Timestamp(start_year, start_month, 1)) &
            (data["Transaction Date"] <= pd.Timestamp(end_year+1, 1, 1)) &
            (data["Product"].isin(selected_products))
        ]
    else:
        filtered_data = data[
            (data["Transaction Date"] >= pd.Timestamp(start_year, start_month, 1)) &
            (data["Transaction Date"] <= pd.Timestamp(end_year, end_month+1, 1)) &
            (data["Product"].isin(selected_products))
        ]
    
    # Determine the full date range
    full_date_range = pd.date_range(start=pd.Timestamp(start_year, start_month, 1),
                                    end=pd.Timestamp(end_year, end_month, 1),
                                    freq="MS").to_period("M") 
    filtered_date_range = filtered_data["Transaction Date"].dt.to_period("M")
    
    # If no transactions occurred for the selected products in the selected time range
    if filtered_date_range.empty:
        error_message = "No transactions were recorded for the selected products in the selected time range."
        return render_template("errorMessage.html", 
                                error_message=error_message
                            )    

    # Perform sum operation for each month and selected products based on the "Value" column
    sums_data = filtered_data.groupby(filtered_data["Transaction Date"].dt.to_period("M"))["Value"].sum().reset_index()
    
    # Determine missing months from the previous filtration
    missing_periods = full_date_range.difference(filtered_date_range)
    # For missing months, the sum in the "Value" column is 0
    missing_data = pd.DataFrame({"Transaction Date": missing_periods, "Value": 0})

    # Concatenate two data sets "sums_data" and "missing_data" and sort the new data set by the "Transaction Date" column
    sums_data = pd.concat([sums_data, missing_data]).sort_values("Transaction Date")

    # Round values in the "Value" column and change their type to int
    sums_data["Value"] = sums_data["Value"].round().astype(int)

    # For readability, the data set "sums_data" is assigned to the variable "data"
    data = sums_data

    # Preparation for forecasting
    # Find the last (latest) date
    last_date = filtered_data["Transaction Date"].max()
    # Add one month to the last date
    forecast_month = last_date + relativedelta(months=1)
    forecast_month = forecast_month.to_period("M")
    forecast_month = forecast_month.strftime("%Y-%m")

    # Decision tree depending on the user's choice in the form
    # Option "I just want to display the data"
    if forecast_decision == "forecast-no":
        chart_data = generate_chart_new(data)
        return render_template("analysisForecastNo.html",
                                file_name=file_name,
                                data=data.to_dict(orient="records"),
                                selected_products=selected_products,
                                start_month=start_month,
                                start_year=start_year,
                                end_month=end_month,
                                end_year=end_year,
                                chart_data=chart_data,
                            )
    
    # Option "Method of Constant Averages"
    elif forecast_decision == "forecast-average":
        # Calculate the average for the "Value" column
        average = calculate_avg(data)
        data_average = data.copy()
        next_month_index = data_average.index.max() + 1
        data_average.loc[next_month_index, "Transaction Date"] = data_average["Transaction Date"].max() + 1
        data_average.loc[next_month_index, "Value"] = average

        # Generate a chart
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
    
    # Option "Method of Moving Averages"
    elif forecast_decision == "forecast-average-moving":
        data_moving = data.copy()
        next_month_index = data_moving.index.max() + 1
        data_moving.loc[next_month_index, "Transaction Date"] = data_moving["Transaction Date"].max() + 1
        data_moving["n3"] = data_moving["Value"]
        data_moving["n6"] = data_moving["Value"]
        data_moving["n9"] = data_moving["Value"]

        # Create a dictionary to store forecasts
        moving_avgs_dict = {}

        # The possibility of calculating specific moving averages depends on a sufficient number of periods on which the forecast can be based
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
            error_message = "Select a larger data range."
            return render_template("errorMessage.html", 
                            error_message=error_message
                            )
        
        # Generate a chart
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

    # Option "Method of Exponential Smoothing"
    elif forecast_decision == "forecast-exponential-smoothing":
        average = calculate_avg(data)
        initial_value = average
        smoothed_values_010 = calculate_exp_smoothing(data, initial_value, 0.10)
        smoothed_values_015 = calculate_exp_smoothing(data, initial_value, 0.15)
        smoothed_values_020 = calculate_exp_smoothing(data, initial_value, 0.20)

        data_exponential_smoothing = data.copy()
        next_month_index = data_exponential_smoothing.index.max() + 1
        data_exponential_smoothing.loc[next_month_index, "Transaction Date"] = data_exponential_smoothing["Transaction Date"].max() + 1
        data_exponential_smoothing["010"] = data_exponential_smoothing["Value"]
        data_exponential_smoothing["015"] = data_exponential_smoothing["Value"]
        data_exponential_smoothing["020"] = data_exponential_smoothing["Value"]
        data_exponential_smoothing.loc[next_month_index, "010"] = smoothed_values_010
        data_exponential_smoothing.loc[next_month_index, "015"] = smoothed_values_015
        data_exponential_smoothing.loc[next_month_index, "020"] = smoothed_values_020

        # Generate a chart
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
    
    # Option "Method of Linear Regression"
    elif forecast_decision == "forecast-linear-regression":
        # Determine the parameters of the linear function y=ax+b corresponding to the trend line using linear regression
        a, b = params_linear_regression(data)
        # Determine the forecast from the equation y=ax+b obtained by linear regression
        forecast_linear_regression = round(calculate_forecast_linear_regression(data, a, b))

        data_linear_regression = data.copy()
        next_month_index = data_linear_regression.index.max() + 1
        data_linear_regression.loc[next_month_index, "Transaction Date"] = data_linear_regression["Transaction Date"].max() + 1
        data_linear_regression.loc[next_month_index, "Value"] = forecast_linear_regression

        # Generate a chart
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
    
    # Option "I want to display a comparison of the results of all the methods mentioned above"
    elif forecast_decision == "forecast-all":
        # Use all previously programmed methods
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

        # Determine the forecast from the equation y=ax+b obtained by linear regression
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

    
# Function responsible for generating charts. Parameters in the function, apart from "data", depend on the method for which the chart is generated.
def generate_chart_new(data, isAverage=None, isAverageMoving=None, isExponentialSmoothing=None, isLinearRegression=None, a=None, b=None):
    fig, ax = plt.subplots()
    fig.set_size_inches(10, 6)
    fig.set_facecolor("#5c78a3")
    ax.set_facecolor("#5c78a3")

    data["Transaction Date"] = data["Transaction Date"].astype(str)
    plt.bar(data["Transaction Date"], data["Value"], color="blue", alpha=1.0, zorder=2)

    plt.ylabel("Transaction Value [USD]", color="white", fontsize=15)
    plt.title("Total transaction value in a given month", color="white", fontsize=15)

    if isAverage == True:
        plt.bar(data["Transaction Date"].iloc[-1], data["Value"].iloc[-1], color="yellow", zorder=3, label="Forecast")
        plt.title("Total transaction value in a given month with the forecast of the total transaction value in the next month")
        plt.legend()

    if isAverageMoving == True:
        # The following lines are only for manipulating the matplotlib library to display three bars next to each other
        # Create a temporary file with transaction dates
        data["Transaction Date TMP"] = pd.to_datetime(data["Transaction Date"])

        # Determine the month for the forecasted month
        next_month = data["Transaction Date TMP"].iloc[-1] + pd.DateOffset(months=1)
        next_month = next_month.strftime("%Y-%m")

        # Determine the month for the month after the forecasted month
        next_next_month = data["Transaction Date TMP"].iloc[-1] + pd.DateOffset(months=2)
        next_next_month = next_next_month.strftime("%Y-%m")

        ax.bar(data["Transaction Date"].iloc[-1], data["n3"].iloc[-1], color="yellow", zorder=53, label="n = 3")
        ax.bar(next_month, data["n6"].iloc[-1], color="red", zorder=3, label="n = 6")
        ax.bar(next_next_month, data["n9"].iloc[-1], color="#B15EFF", zorder=3, label="n = 9")
        plt.title("Total transaction value in a given month with the forecast of the total transaction value in the next month")
        ax.legend()

    if isExponentialSmoothing == True:
        # The following lines are only for manipulating the matplotlib library to display three bars next to each other
        # Create a temporary file with transaction dates
        data["Transaction Date TMP"] = pd.to_datetime(data["Transaction Date"])

        # Determine the month for the forecasted month
        next_month = data["Transaction Date TMP"].iloc[-1] + pd.DateOffset(months=1)
        next_month = next_month.strftime("%Y-%m")

        # Determine the month for the month after the forecasted month
        next_next_month = data["Transaction Date TMP"].iloc[-1] + pd.DateOffset(months=2)
        next_next_month = next_next_month.strftime("%Y-%m")

        ax.bar(data["Transaction Date"].iloc[-1], data["010"].iloc[-1], color="yellow", zorder=53, label="α = 0.10")
        ax.bar(next_month, data["015"].iloc[-1], color="red", zorder=3, label="α = 0.15")
        ax.bar(next_next_month, data["020"].iloc[-1], color="#B15EFF", zorder=3, label="α = 0.20")
        plt.title("Total transaction value in a given month with the forecast of the total transaction value in the next month")
        ax.legend()

    if isLinearRegression == True:
        # If the forecast is 0, the value will be represented by a point instead of a bar
        if data["Value"].iloc[-1] == 0:
            plt.scatter(data["Transaction Date"].iloc[-1], data["Value"].iloc[-1], color="yellow", zorder=10)
        else:
            plt.bar(data["Transaction Date"].iloc[-1], data["Value"].iloc[-1], color="yellow", zorder=10)

        x_values = range(0, len(data))
        y_values = [a * x + b for x in x_values]
        plt.plot(x_values, y_values, color="red", linewidth=4, label="Trend Line")
        plt.title("Total transaction value in a given month with the forecast of the total transaction value in the next month")
        ax.legend()
    # If the number of periods is greater than or equal to 12, 12 values will be marked on the X-axis
    if len(data) >= 12:
        num_labels = 12
        # Determine the spacing between values
        step_size = len(data) // (num_labels - 1)
        xticks = data["Transaction Date"].iloc[::step_size].tolist() + [data["Transaction Date"].iloc[-1]]
        ax.set_xticks(xticks)
    plt.yticks(color="white", fontsize=11)
    plt.xticks(rotation=45, ha="right", color="white", fontsize=11)
    plt.grid(True, zorder=1)
    image = io.BytesIO()
    plt.savefig(image, format="png")
    image.seek(0)
    image64 = base64.b64encode(image.read()).decode()
    plt.close(fig)
    return image64

# Function responsible for deleting a .csv file
@app.route("/delete_file/<file_name>")
def delete_file(file_name):
    file_path = "static/uploads/" + file_name
    os.remove(file_path)
    return redirect(url_for("exploreFiles"))

# Function responsible for calculating the constant average
def calculate_avg(data):
    return round(data["Value"].mean())

# Function responsible for calculating moving averages
def calculate_moving_avg(data, n):
    data = data["Value"]
    sum_of_n_values = 0
    for value in data[-n:]:
        sum_of_n_values += value
    moving_average = round(sum_of_n_values / n)
    return moving_average

# Function responsible for calculating forecasts using exponential smoothing
def calculate_exp_smoothing(data, initial_value, alpha):
    data = data["Value"]
    smoothed_values = [initial_value] 

    for i in range(1, len(data)+1):
        smoothed_value = round(alpha * data[i-1] + (1 - alpha) * smoothed_values[-1])
        smoothed_values.append(smoothed_value)

    return smoothed_values[-1]

# Function responsible for calculating the parameters of the linear function y=ax+b corresponding to the trend line
def params_linear_regression(data):
    n = len(data)
    data["Index"] = list(range(1, len(data) + 1))
    sum_x = sum(data["Index"])
    sum_y = sum(data["Value"])
    sum_x2 = sum(data["Index"]**2)
    sum_xy = sum(data["Index"]*data["Value"])
    a = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x**2)
    b = (sum_y - a * sum_x) / n
    return a, b

# Function responsible for calculating the forecast values from the linear function y=ax+b corresponding to the trend line
def calculate_forecast_linear_regression(data, a, b):
    n = len(data) + 1
    forecast_linear_regression = n * a + b

    # If the forecast is negative, the value is set to 0
    forecast_linear_regression = max(forecast_linear_regression, 0)
    return forecast_linear_regression

if __name__ == "__main__":
    app.run(debug=True)
