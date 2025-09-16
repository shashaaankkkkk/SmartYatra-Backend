from django.db import models

class User(models.Model):
    first_name=models.CharField(max_length=200)
    last_name=models.CharField(max_length=200,blank=True,null=True)
    phone_number=models.CharField(max_length=15,unique=True,null=True)
    email=models.EmailField(null=True)
    gender=models.CharField(max_length=100)
    age=models.IntegerField(null=True)

    def __str__(self):
        return self.first_name