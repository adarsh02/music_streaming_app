from website.__init__ import create_app
from website.auth import auth
from website.tracks import track
from website.user import user
from website.albums import albums
from website.worker import celery_init_app
import flask_excel as excel
from celery.schedules import crontab
from website.tasks import daily_reminder,monthly_pdf_reminder


app = create_app()
app.register_blueprint(auth, url_prefix="/auth")
app.register_blueprint(track,url_prefix="/tracks")
app.register_blueprint(user,url_prefix="/user")
app.register_blueprint(albums,url_prefix="/albums")
celery_app = celery_init_app(app)


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Daily reminder task
    sender.add_periodic_task(
        crontab(hour=2, minute=20),
        daily_reminder.s('21f1000112@gmail.com', 'Daily Reminder'),
    )

    # Monthly PDF reminder task
    sender.add_periodic_task(
        crontab(hour=2, minute=20, day_of_month=15),
         monthly_pdf_reminder.s(),
    )

        

if __name__ == "__main__":
    app.run(debug=True)