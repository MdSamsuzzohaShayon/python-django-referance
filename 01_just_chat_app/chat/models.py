# GET THE USER
from django.contrib.auth import  get_user_model
from django.db import models

User = get_user_model()

# Create your models here.
def last_10_message():
    return Message.objects.order_by('-timestamp').all()[:10]


class Message (models.Model):
    author = models.ForeignKey(User, related_name="author_messages", on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.author.username