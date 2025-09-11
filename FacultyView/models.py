from datetime import datetime
from django.db import models
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
)

class Student(models.Model):
    s_eml = models.CharField(max_length=40, primary_key=True)
    s_fname = models.CharField(max_length=20)
    s_lname = models.CharField(max_length=20)

    def __str__(self) -> str:
        return f"{self.s_eml} - {self.s_fname} {self.s_lname}"

class ClassName(models.Model):
    s_className = models.CharField(max_length=40)

    def __str__(self) -> str:
        return f"{self.s_className}"

class Attendance(models.Model):
    s_class = models.ForeignKey(ClassName, on_delete=models.RESTRICT)
    dte_date = models.DateField()
    student = models.ForeignKey(Student, on_delete=models.RESTRICT)

    def __str__(self) -> str:
        return f"{self.dte_date} - {self.student.__str__}"