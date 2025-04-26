from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util

from ...tasks import make_spreadsheet, email_users



def spreadsheet():
    print("Made Daily Spreadsheet")
    make_spreadsheet()

def logging_email():
    print("Sending Logging Email")
    email_users()
    


# The `close_old_connections` decorator ensures that database connections, that have become
# unusable or are obsolete, are closed before and after your job has run. You should use it
# to wrap any jobs that you schedule that access the Django database in any way. 
@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    """
    This job deletes APScheduler job execution entries older than `max_age` from the database.
    It helps to prevent the database from filling up with old historical records that are no
    longer useful.
  
    :param max_age: The maximum length of time to retain historical job execution records.
                  Defaults to 7 days.
    """
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            spreadsheet,
            trigger=CronTrigger(hour='7', minute='30'),  # At 7:30am each day, send database
            id="spreadsheet",  # The `id` assigned to each job MUST be unique
            max_instances=1,
            replace_existing=True,
        )
        print("Added job 'spreadsheet'.")
        
        scheduler.add_job(
            logging_email,
            trigger=CronTrigger(day_of_week="mon", hour='7', minute='0'),
            id="logging_email",
            max_instances=1,
            replace_existing=True,
        )
        print("Added job 'logging_email'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),  # Midnight on Monday, before start of the next work week.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        print(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            print("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            print("Stopping scheduler...")
            scheduler.shutdown()
        print("Scheduler shut down successfully!")