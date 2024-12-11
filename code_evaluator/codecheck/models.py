from django.db import models

class User(models.Model):
  pass
class Events(models.Model):
  pass
class Problems(models.Model):
  pass
class Submission(models.Model):
  submission_id = models.IntegerField()
  problem_id = models.IntegerField()
  user_id = models.IntegerField()
  code = models.TextField()
  submitted_at = models.TimeField()
class Evaluation(models.Model):
  evaluation_id = models.IntegerField()
  submission_id = models.IntegerField()
  score = models.TextField()
  feedback = models.IntegerField()
  evaluated_at = models.TimeField()
class Leaderboard(models.Model):
  event_id = models.IntegerField()
  user_id = models.IntegerField()
  total_score = models.IntegerField()
  rank = models.IntegerField()
class Reports(models.Model):
  report_id = models.IntegerField()
  event_id = models.IntegerField()
  content = models.TextField()
  generated_at = models.TimeField()