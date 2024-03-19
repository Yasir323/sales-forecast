from flask import Flask

from sales_forecast.routes.upload_file import upload_file_bp
from sales_forecast.routes.generate_forecast import generate_forecast_bp
from sales_forecast.routes.download_file import download_file_bp
from sales_forecast.task_queue import celery_init_app

app = Flask(__name__)

app.register_blueprint(upload_file_bp)
app.register_blueprint(generate_forecast_bp)
app.register_blueprint(download_file_bp)
app.config.from_mapping(
    CELERY=dict(
        broker_url="redis://localhost",
        result_backend="redis://localhost",
        task_ignore_result=False,
    ),
)
celery_app = celery_init_app(app)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=7080, debug=True)
