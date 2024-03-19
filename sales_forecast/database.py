from pymongo import MongoClient
import pandas as pd


class MongoDb:

    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls, *args, **kwargs)
        return cls.__instance

    def __init__(self, uri="mongodb://localhost:27017"):
        self.client = MongoClient(uri)
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
            for doc in col.find():
                if doc["Year"] not in sales_data:
                    sales_data[doc["Year"]] = {doc["Week"]: doc["Budget"]}
                else:
                    sales_data[doc["Year"]][doc["Week"]] = doc["Budget"]
            return sales_data
        except:
            pass

    def get_many(self, collection_name: str):
        try:
            col = self.db[collection_name]
            data = [doc for doc in col.find()]
        except:
            data = []
        return data
