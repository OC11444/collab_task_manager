from rest_framework import serializers
from .models import School, Department, Course, Unit, Enrollment

class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = '__all__'

class DepartmentSerializer(serializers.ModelSerializer):
    school_name = serializers.ReadOnlyField(source='school.name')

    class Meta:
        model = Department
        fields = ['id', 'name', 'school', 'school_name', 'description']

class CourseSerializer(serializers.ModelSerializer):
    department_name = serializers.ReadOnlyField(source='department.name')

    class Meta:
        model = Course
        fields = ['id', 'name', 'course_code', 'department', 'department_name']

class UnitSerializer(serializers.ModelSerializer):
    course_name = serializers.ReadOnlyField(source='course.name')

    class Meta:
        model = Unit
        fields = ['id', 'name', 'unit_code', 'course', 'course_name']

class EnrollmentSerializer(serializers.ModelSerializer):
    student_username = serializers.ReadOnlyField(source='student.username')
    unit_name = serializers.ReadOnlyField(source='unit.name')

    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'student_username', 'unit', 'unit_name', 'date_enrolled']