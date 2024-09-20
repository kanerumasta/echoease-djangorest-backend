from django.db import models

class Notification(models.Model):
    notificationn_choices = [
        ('general', 'General'),
        ('message', 'Message'),
        ('')

    ]
    notification_type = models.CharField(max_length=50)
    message= models.TextField()
