from datetime import datetime
from django.db import models
from django_case_insensitive_field import CaseInsensitiveFieldMixin
from django.core.validators import RegexValidator

class LowerCharField(CaseInsensitiveFieldMixin, models.CharField):
    """[summary]
    Makes django CharField case insensitive \n
    Extends both the `CaseInsensitiveFieldMixin` and  CharField \n
    Then you can import 
    """
    def __init__(self, *args, **kwargs):
        super(CaseInsensitiveFieldMixin, self).__init__(*args, **kwargs)


s_eml_validator = RegexValidator(
    regex=r"(?i)^([a-z]+)\.(([a-z]+\.?)+)(?<!\.)@student\.cat\.org\.uk$",
    message="Value should be in the form <first name>.<last name>@student.cat.org.uk",
)
class Student(models.Model):
    s_eml = LowerCharField(max_length=100, primary_key=True,validators=[s_eml_validator])
    s_fname = models.CharField(max_length=30)
    s_lname = models.CharField(max_length=30)

    def save(self, *args, **kwargs):
        # Run validation before saving
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.s_eml} - {self.s_fname} {self.s_lname}"


def get_default_module():
    return ModuleName.objects.get_or_create(s_moduleName='Default Module')[0].id  # pyright: ignore[reportAttributeAccessIssue]

class ModuleName(models.Model):
    s_moduleName = models.CharField(max_length=100)

    def __str__(self) -> str:
        return f"{self.s_moduleName}"

class ClassName(models.Model):
    s_className = models.CharField(max_length=100)
    moduleName = models.ForeignKey(ModuleName, on_delete=models.RESTRICT,default=get_default_module)

    def __str__(self) -> str:
        return f"{self.moduleName} - {self.s_className}"
    
    class Meta:
        ordering = ['moduleName__s_moduleName','s_className']

class Attendance(models.Model):
    className = models.ForeignKey(ClassName, on_delete=models.RESTRICT)
    dte_date = models.DateTimeField()
    student = models.ForeignKey(Student, on_delete=models.RESTRICT)

    def __str__(self) -> str:
        return f"{self.dte_date} - {self.className} - {self.student}"
    
    class Meta:
        ordering = ['dte_date','className']