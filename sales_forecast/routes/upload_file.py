from flask import Blueprint, request, jsonify

from sales_forecast import db
from sales_forecast.processing import get_data_from_excel

upload_file_bp = Blueprint('upload_file', __name__)


@upload_file_bp.route('/upload', methods=['POST'])
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
