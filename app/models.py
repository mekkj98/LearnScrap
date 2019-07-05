from django.db import models

# Create your models here.
class Movies(models.Model):
    prime_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    release_date = models.IntegerField()
    
    rating = models.FloatField()
    meta_score = models.IntegerField()
    votes = models.IntegerField()
    
    objects = models.Manager()

    def __str__(self):
        return self.name
    