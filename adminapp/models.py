from django.db import models

# Create your models here.
class manage_users_model(models.Model):
    User_id = models.AutoField(primary_key = True)
    user_Profile = models.FileField(upload_to = 'images/')
    User_Email = models.EmailField(max_length = 50)
    User_Status = models.CharField(max_length = 10)
    
    class Meta:
        db_table = 'manage_users'
        
class Train_test_split_model(models.Model):
    User_id = models.AutoField(primary_key=True)
    training_images = models.CharField(max_length=10, null=True)
    validation_images = models.CharField(max_length=10, null=True)
    testing_images = models.CharField(max_length=10, null=True)
    classes_images = models.CharField(max_length=10, null=True)

    class Meta:
        db_table = "Traintestsplit"
        
class Inception(models.Model):
    User_id = models.AutoField(primary_key=True)
    Model_accuracy = models.CharField(max_length=100)
    Executed = models.CharField(max_length=50, null=True)

    class Meta:
        db_table = "Inception"

class Resonet(models.Model):
    User_id = models.AutoField(primary_key=True)
    Model_accuracy = models.CharField(max_length=100)
    Executed = models.CharField(max_length=50, null=True)

    class Meta:
        db_table = "resonent"
        
class Mobilenet(models.Model):
    User_id = models.AutoField(primary_key=True)
    Model_accuracy = models.CharField(max_length=100)
    Executed = models.CharField(max_length=50, null=True)

    class Meta:
        db_table = "mobilenet"