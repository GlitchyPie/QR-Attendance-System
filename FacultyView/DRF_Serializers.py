from rest_framework import serializers
from .models import Student, ModuleName, ClassName, Attendance

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ["s_eml", "s_fname", "s_lname"]

class ModuleNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModuleName
        fields = ["id", "s_moduleName"]

class ClassNameSerializer(serializers.ModelSerializer):
    moduleName = ModuleNameSerializer()  # NESTED

    class Meta:
        model = ClassName
        fields = ["id", "s_className", "moduleName"]

class AttendanceSerializer(serializers.ModelSerializer):
    student = StudentSerializer()     # NESTED
    className = ClassNameSerializer() # NESTED

    class Meta:
        model = Attendance
        fields = ["id", "dte_date", "date_only", "time_only", "student", "className"]