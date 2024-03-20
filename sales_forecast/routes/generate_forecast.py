from flask import Blueprint, jsonify

from sales_forecast.processing import generate_forecast

generate_forecast_bp = Blueprint("generate_forecast_bp", __name__)


@generate_forecast_bp.route('/generate-forecast', methods=['POST'])
def trigger_forecast():
    """
    API endpoint to trigger the generation of sales forecast.

    This endpoint triggers the asynchronous execution of the generate_forecast task
    using Celery's apply_async method. Upon successful triggering of the forecast
    generation job, it returns a JSON response with a success message and status code 200.

    Returns:
        Response: JSON response indicating the status of the forecast generation trigger.
            - If the forecast generation job is triggered successfully, returns a success message (status code 200).
    """

    generate_forecast.apply_async()
    return jsonify({'message': 'Forecast generation triggered successfully'}), 200
