import datetime
import os

from flask import Blueprint, jsonify, send_from_directory

download_file_bp = Blueprint("download_file_bp", __name__)


@download_file_bp.route('/download', methods=['GET'])
def download_file():
    """API to download output Excel"""
    try:
        postfix = datetime.datetime.now().isoformat().replace("-", "_").split("T")[0]
        out_dir = os.path.join("resources", "generated_reports")
        file_name = f"SalesForecast{postfix}.xlsx"
        file = os.path.join(out_dir, file_name)
        if not os.path.exists(file):
            print("File nhi mili!!!", file)
            return {"message": "File not found"}, 404
        return send_from_directory(out_dir, file_name)
    except Exception as err:
        print(f"{type(err).__name__}: {str(err)}")
        return {"message": "Some error occurred"}, 500
