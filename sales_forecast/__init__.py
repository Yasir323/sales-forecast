import os

from dotenv import load_dotenv

from sales_forecast.database import MongoDb

load_dotenv()

db = MongoDb(uri=os.environ.get("MONGO_URL"))
