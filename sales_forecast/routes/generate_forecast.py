from flask import Blueprint, jsonify

from sales_forecast.processing import generate_forecast

generate_forecast_bp = Blueprint("generate_forecast_bp", __name__)


@generate_forecast_bp.route('/generate-forecast', methods=['POST'])
def trigger_forecast():
    """API to trigger forecast generation job"""
    generate_forecast()
    return jsonify({'message': 'Forecast generation triggered successfully'}), 200
