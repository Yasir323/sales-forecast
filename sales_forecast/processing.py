import datetime
import os
import pandas as pd
from celery import shared_task

from sales_forecast import db


@shared_task
def generate_forecast():
    """
    Calculation of Quantity:

    Quantity = AvgSales * no of days in that week * BudgetFactor,
    where BudgetFactor = current week budget / previous week budget
    """
    print("Started")
    postfix = datetime.datetime.now().isoformat().replace("-", "_").split("T")[0]
    file_name = f"SalesForecast{postfix}.xlsx"
    out_dir = os.path.join("resources", "generated_reports")
    file = os.path.join(out_dir, file_name)
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    elif os.path.exists(file):
        return

    forecast = []
    sales_data = db.get_sales_data()
    budget_data = db.get_budget_data()

    for article in sales_data:
        avg_sales = article["AvgSales"]
        article_name = article["Article"]
        day_of_week = datetime.datetime.today().weekday()
        no_of_days_in_the_week = 7 - day_of_week
        current_time = datetime.datetime.now()
        current_week = datetime.date(current_time.year, current_time.month, current_time.day).isocalendar()[1]
        previous_time = current_time + datetime.timedelta(days=no_of_days_in_the_week + 1)
        previous_week = datetime.date(previous_time.year, previous_time.month, previous_time.day).isocalendar()[1]
        days_left = 60
        while days_left > 0:
            current_week_budget = budget_data[current_time.year][current_week]
            previous_week_budget = budget_data[previous_time.year][previous_week]
            budget_factor = current_week_budget / previous_week_budget
            quantity = avg_sales * no_of_days_in_the_week * budget_factor
            forecast.append({"Article": article_name, "Week_no": current_week, "Quantity": quantity})

            # Update variables
            previous_time = current_time
            previous_week = current_week
            current_time = previous_time + datetime.timedelta(no_of_days_in_the_week)
            current_week = datetime.date(current_time.year, current_time.month, current_time.day).isocalendar()[1]
            days_left -= no_of_days_in_the_week
            no_of_days_in_the_week = 7 if days_left >= 7 else days_left

    pd.DataFrame(forecast).to_excel(file)


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


def get_sales_report(postfix: str):
    data = db.get_many("SalesReport" + postfix)
    return pd.DataFrame(data)
