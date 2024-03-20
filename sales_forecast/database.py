import os
from typing import Union, List

from pymongo import MongoClient
import pandas as pd


class MongoDb:
    """
    Singleton class for managing MongoDB connections and operations.

    This class provides methods for interacting with a MongoDB database,
    including saving data, retrieving sales and budget data, and fetching
    multiple documents from a specified collection.

    Attributes:
        __instance: Singleton instance of the MongoDb class.
        client: MongoClient instance for connecting to the MongoDB server.
        db: MongoDB database instance.
    """

    __instance = None

    def __new__(cls, *args, **kwargs):
        """
        Create a new instance of the MongoDb class if it doesn't exist.

        This method ensures that only one instance of the MongoDb class is
        created throughout the application.

        Args:
            cls: The class object.

        Returns:
            MongoDb: The singleton instance of the MongoDb class.
        """
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, uri: str):
        """
        Initialize the MongoDb class with the MongoDB connection URI.

        Args:
            uri (str): The MongoDB connection URI.
        """
        self.client = MongoClient(uri)
        self.db = self.client[os.environ.get("MONGO_DBNAME")]

    def save(self, data: Union[pd.DataFrame, List[dict]], collection: str) -> bool:
        """
        Save data to the specified collection in the MongoDB database.

        Args:
            data (Union[pd.DataFrame, List[dict]]): The data to be saved.
                It can be a Pandas DataFrame or a list of dictionaries.
            collection (str): The name of the collection in the MongoDB database.

        Returns:
            bool: True if the data is successfully saved, False otherwise.
        """
        if isinstance(data, pd.DataFrame):
            is_inserted = self.save_df(data, collection)
        else:
            col = self.db[collection]
            result = col.insert_many(data)
            is_inserted = result.acknowledged
        return is_inserted

    def save_df(self, data: pd.DataFrame, collection: str) -> bool:
        """
        Save a Pandas DataFrame to the specified collection in the MongoDB database.

        Args:
            data (pandas.DataFrame): The DataFrame to be saved.
            collection (str): The name of the collection in the MongoDB database.

        Returns:
            bool: True if the DataFrame is successfully saved, False otherwise.
        """
        is_saved = False
        try:
            col = self.db[collection]
            data = data.to_dict("records")
            result = col.insert_many(data)
            is_saved = result.acknowledged
        except:
            pass
        return is_saved

    def get_sales_data(self) -> List[dict]:
        """
        Retrieve sales data from its respective collection.

        Returns:
            List[dict]: A list of dictionaries representing sales data documents.
        """
        docs = []
        try:
            col = self.db[os.environ.get("SALES_DATA_COLLECTION")]
            docs = [doc for doc in col.find()]
        except:
            pass
        return docs

    def get_budget_data(self) -> dict:
        """
        Retrieve budget data from the 'BudgetData' collection.

        Returns:
            dict: A dictionary containing budget data grouped by year and week.
        """

        sales_data = {}
        try:
            col = self.db[os.environ.get("BUDGET_DATA_COLLECTION")]
            for doc in col.find():
                if doc["Year"] not in sales_data:
                    sales_data[doc["Year"]] = {doc["Week"]: doc["Budget"]}
                else:
                    sales_data[doc["Year"]][doc["Week"]] = doc["Budget"]
            return sales_data
        except:
            pass
        return sales_data

    def get_many(self, collection_name: str) -> List[dict]:
        """
        Retrieve multiple documents from the specified collection.

        Args:
            collection_name (str): The name of the collection in the MongoDB database.

        Returns:
            List[dict]: A list of dictionaries representing the retrieved documents.
        """

        data = []
        try:
            col = self.db[collection_name]
            data = [doc for doc in col.find()]
        except:
            pass
        return data
