from datetime import datetime
from django.db import models

class Student(models.Model):
    s_eml = models.CharField(max_length=100, primary_key=True,default="-.-@-.-")
    s_fname = models.CharField(max_length=30)
    s_lname = models.CharField(max_length=30)

    def __str__(self) -> str:
        return f"{self.s_eml} - {self.s_fname} {self.s_lname}"

class ClassName(models.Model):
    s_className = models.CharField(max_length=100)

    def __str__(self) -> str:
        return f"{self.s_className}"

class Attendance(models.Model):
    s_class = models.ForeignKey(ClassName, on_delete=models.RESTRICT)
    dte_date = models.DateField()
    student = models.ForeignKey(Student, on_delete=models.RESTRICT)

    def __str__(self) -> str:
        return f"{self.dte_date} - {self.student.__str__}"