from celery import Celery, Task
from flask import Flask


def celery_init_app(app: Flask) -> Celery:
    """
    Initialize and configure a Celery application for use with a Flask application.

    Args:
        app (Flask): The Flask application instance.

    Returns:
        Celery: The initialized Celery application instance.
    """

    class FlaskTask(Task):
        """
        Custom Celery task class for integrating Flask application context.

        This class ensures that each Celery task runs within a Flask application context,
        allowing access to Flask extensions and other application components.

        Args:
            Task: The base class for Celery tasks.

        Methods:
            __call__: Method to execute the task with Flask application context.
        """

        def __call__(self, *args: object, **kwargs: object) -> object:
            """
            Execute the task with Flask application context.

            This method wraps the task execution within a Flask application context
            to enable access to Flask application components.

            Args:
                *args: Positional arguments passed to the task function.
                **kwargs: Keyword arguments passed to the task function.

            Returns:
                object: The result of the task execution.
            """

            with app.app_context():
                return self.run(*args, **kwargs)

    # celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app = Celery(app.name)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.Task = FlaskTask
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app
