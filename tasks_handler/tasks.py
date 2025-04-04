from tasks_handler.celery import app


@app.tasks
def handle_transaction():
    pass
