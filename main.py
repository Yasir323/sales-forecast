from flask import Flask, request, jsonify
from pymongo import MongoClient
import pandas as pd

app = Flask(__name__)


class MongoDb:

    def __init__(self, uri=None):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['sales_forecast']

    def save(self, data, collection):
        if isinstance(data, pd.DataFrame):
            return self.save_df(data, collection)
        return False

    def save_df(self, data, collection):
        col = self.db[collection]
        data = data.to_dict("records")
        col.insert_many(data)
        return True


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


# API to trigger forecast generation job
@app.route('/trigger-forecast', methods=['POST'])
def trigger_forecast():
    # Your forecast generation logic here
    return jsonify({'message': 'Forecast generation triggered successfully'}), 200


# API to download output Excel
@app.route('/download', methods=['GET'])
def download_file():
    # Your download logic here
    return jsonify({'message': 'Download endpoint'}), 200


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



def main():
    get_data_from_excel("resources/Assessment Inputs.xlsx")


if __name__ == "__main__":
    main()
