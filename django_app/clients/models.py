from django.db import models

class Client(models.Model):
    tg_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username
