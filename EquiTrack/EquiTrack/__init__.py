from __future__ import absolute_import

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app


__title__ = 'eTools Platform'
__version__ = '1.9.0'
__license__ = 'GNU AGPL v3'
