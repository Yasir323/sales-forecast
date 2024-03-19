import datetime

from flask import Flask, request, jsonify
from pymongo import MongoClient
import pandas as pd


class MongoDb:

    def __init__(self, uri=None):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['sales_forecast']

    def save(self, data, collection):
        if isinstance(data, pd.DataFrame):
            is_inserted = self.save_df(data, collection)
        else:
            col = self.db[collection]
            result = col.insert_many(data)
            is_inserted = result.acknowledged
        return is_inserted

    def save_df(self, data, collection):
        try:
            col = self.db[collection]
            data = data.to_dict("records")
            result = col.insert_many(data)
            return result.acknowledged
        except:
            return False

    def get_sales_data(self):
        try:
            col = self.db["SalesData"]
            docs = [doc for doc in col.find()]
            return docs
        except:
            pass

    def get_budget_data(self):
        try:
            col = self.db["BudgetData"]
            sales_data = {}
            for doc in col.find():  # TODO: Filter the data
                if doc["Year"] not in sales_data:
                    sales_data[doc["Year"]] = {doc["Week"]: doc["Budget"]}
                else:
                    sales_data[doc["Year"]][doc["Week"]] = doc["Budget"]
            return sales_data
        except:
            pass


def get_budget_data(df):
    # Budget data
    df1 = df["BudgetData"]
    df1.reset_index(drop=True, inplace=True)
    return df1


def get_sales_data(df):
    df1 = df["SaleData"]
    df1 = df1.dropna(axis=0, how="all")
    df1.reset_index(drop=True, inplace=True)
    return df1


def get_data_from_excel(file):
    df = pd.read_excel(file, header=[0, 1], index_col=0)
    df.dropna(axis=1, how="all", inplace=True)

    budget_data = get_budget_data(df)
    sales_data = get_sales_data(df)
    return budget_data, sales_data


def generate_forecast():
    """
    Calculation of Quantity:

    Quantity = AvgSales * no of days in that week * BudgetFactor,
    where BudgetFactor = current week budget / previous week budget
    """
    sales_data = db.get_sales_data()
    budget_data = db.get_budget_data()
    day_of_week = datetime.datetime.today().weekday()
    no_of_days_in_the_week = 7 - day_of_week
    current_time = datetime.datetime.now()
    current_week = datetime.date(current_time.year, current_time.month, current_time.day).isocalendar()[1]
    previous_time = current_time + datetime.timedelta(days=no_of_days_in_the_week + 1)
    previous_week = datetime.date(previous_time.year, previous_time.month, previous_time.day).isocalendar()[1]
    forecast = []
    days_left = 60

    for article in sales_data:
        avg_sales = article["AvgSales"]
        current_week_budget = budget_data[current_time.year][current_week]
        previous_week_budget = budget_data[previous_time.year][previous_week]
        budget_factor = current_week_budget / previous_week_budget
        quantity = avg_sales * no_of_days_in_the_week * budget_factor
        forecast.append({"Article": article["Article"], "Week_no": current_week, "Quantity": quantity})

        # Update variables
        previous_time = current_time
        previous_week = current_week
        current_time = previous_time + datetime.timedelta(no_of_days_in_the_week)
        current_week = datetime.date(current_time.year, current_time.month, current_time.day).isocalendar()[1]
        days_left -= no_of_days_in_the_week
        no_of_days_in_the_week = 7 if days_left >= 7 else days_left

    return save_forecast(forecast)


def save_forecast(forecast):
    return db.save(forecast, "SalesForecast")


app = Flask(__name__)
db = MongoDb()


@app.route('/upload', methods=['POST'])
def upload_file():
    """
    End-point Handle file uploads
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        try:

            # Read Excel file
            budget_data, sales_data = get_data_from_excel(file)

            # Store data in MongoDB
            stored = db.save(budget_data, "BudgetData") and db.save(sales_data, "SalesData")
            if stored:
                return jsonify({'message': 'File uploaded successfully'}), 200
            else:
                return jsonify({'message': 'Failed to save data'}), 500

        except Exception as e:
            return jsonify({'error': str(e)}), 500


@app.route('/trigger-forecast', methods=['POST'])
def trigger_forecast():
    """API to trigger forecast generation job"""
    generate_forecast()
    return jsonify({'message': 'Forecast generation triggered successfully'}), 200


# API to download output Excel
@app.route('/download', methods=['GET'])
def download_file():
    # Your download logic here
    return jsonify({'message': 'Download endpoint'}), 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=7080)
