from django.db import models


class Questions(models.Model):
    id = models.IntegerField(primary_key=True)
    qid = models.TextField()
    text = models.TextField()

    class Meta:
        managed = False
        db_table = 'questions'

class Coders(models.Model):
    id = models.IntegerField(primary_key=True)
    label = models.TextField()

    class Meta:
        managed = False
        db_table = 'coders'

class ResponseCodes(models.Model):
    id = models.IntegerField(primary_key=True)
    qid = models.TextField()
    pid = models.IntegerField()
    coder_combo = models.TextField()
    codes = models.TextField()

    class Meta:
        managed = False
        db_table = 'response_codes'

class Responses(models.Model):
    id = models.IntegerField(primary_key=True)
    pid = models.IntegerField()
    qid = models.TextField()
    response = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'responses'


class Terms(models.Model):
    #id = models.AutoField(unique=True)
    id = models.IntegerField(primary_key=True)
    term = models.TextField()
    definition = models.TextField()
    qid = models.TextField()

    class Meta:
        managed = False
        db_table = 'terms'