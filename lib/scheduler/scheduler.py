from apscheduler.schedulers.background import BackgroundScheduler


class APS:
    scheduler: BackgroundScheduler

    def __init__(self):
        pass

    @classmethod
    def init_app(cls):
        cls.scheduler = BackgroundScheduler()
    
    def add_task(self, task_name: str, cron_expression: str, callback):
        APS.scheduler.add_job(callback, 'cron', id=task_name, **cron_expression)
    
    def remove_task(self, task_name: str):
        APS.scheduler.remove_job(task_name)
    
    def start(self):
        APS.scheduler.start()
    
    def stop(self):
        APS.scheduler.shutdown()