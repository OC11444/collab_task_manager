from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from academic.models import School, Department, Course, Unit # Add this line
# ... keep your other imports like Task, Comment, etc.

# Adjust these imports based on your exact model locations!
from academic.models import Course, Unit, StudyGroup
from tasks.models import Task
from .models import Comment, Notification
from .services import create_comment

User = get_user_model()


class CommentPrivacyAndNotificationTests(APITestCase):
    def setUp(self):
        # Create the required hierarchy
        self.school = School.objects.create(name="Engineering")
        self.dept = Department.objects.create(name="Software", school=self.school)

        self.course = Course.objects.create(
            name="Computer Science",
            department=self.dept,
        )

        self.teacher = User.objects.create_user(
            username="<teacher_username>",
            password="<teacher_password>",
        )
        self.student_a = User.objects.create_user(
            username="<student_a_username>",
            password="<student_a_password>",
        )
        self.student_b = User.objects.create_user(
            username="<student_b_username>",
            password="<student_b_password>",
        )
        self.student_c = User.objects.create_user(
            username="<student_c_username>",
            password="<student_c_password>",
        )

        self.unit = Unit.objects.create(
            name="Programming",
            code="CS101",
            course=self.course,
            lecturer=self.teacher,
        )

        self.group = StudyGroup.objects.create(
            name="Group A",
            unit=self.unit,
        )
        self.group.members.add(self.student_a, self.student_b)

        self.individual_task = Task.objects.create(
            title="Individual Task",
            description="Complete the individual assignment",
            created_by=self.teacher,
            unit=self.unit,
        )

        self.group_task = Task.objects.create(
            title="Group Task",
            description="Complete the group assignment",
            created_by=self.teacher,
            unit=self.unit,
        )
        self.group_task.study_groups.add(self.group)

    def test_student_cannot_see_other_students_comments(self):
        """Test that Student B cannot see Student A's comments on a general task."""
        # Student A makes a comment
        create_comment(author=self.student_a, content="Here is my draft.", target_object=self.individual_task)

        # Student B tries to view comments for this task
        self.client.force_authenticate(user=self.student_b)
        response = self.client.get(f'/api/comments/task/{self.individual_task.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # The list should be empty for Student B because of our RBAC selector
        self.assertEqual(len(response.data), 0)

    def test_teacher_can_see_all_comments(self):
        """Test that a Teacher sees everyone's comments."""
        create_comment(author=self.student_a, content="Help me", target_object=self.individual_task)
        create_comment(author=self.student_b, content="I am done", target_object=self.individual_task)

        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(f'/api/comments/task/{self.individual_task.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_teacher_reply_reaches_student_privately(self):
        """Test that a Teacher's reply to Student A is NOT visible to Student B."""
        # Student A asks a question
        student_comment = create_comment(author=self.student_a, content="I am stuck",
                                         target_object=self.individual_task)

        # Teacher replies specifically to Student A
        create_comment(author=self.teacher, content="Check page 4.", target_object=self.individual_task,
                       parent=student_comment)

        # Student A logs in and checks
        self.client.force_authenticate(user=self.student_a)
        response_a = self.client.get(f'/api/comments/task/{self.individual_task.id}/')
        self.assertEqual(len(response_a.data), 1)  # Sees their top level comment
        self.assertEqual(len(response_a.data[0]['replies']), 1)  # Sees the teacher's reply

        # Student B logs in and checks
        self.client.force_authenticate(user=self.student_b)
        response_b = self.client.get(f'/api/comments/task/{self.individual_task.id}/')
        self.assertEqual(len(response_b.data), 0)  # Sees absolutely nothing

    def test_group_task_visibility(self):
        """Test that Student C sees Student A's comment on a group task, but Student B does not."""
        # Student A comments on the group task
        create_comment(author=self.student_a, content="I uploaded the code.", target_object=self.group_task)

        # Student C (Group Member) checks
        self.client.force_authenticate(user=self.student_c)
        response_c = self.client.get(f'/api/comments/task/{self.group_task.id}/')
        self.assertEqual(len(response_c.data), 1)  # Should see it!

        # Student B (Not in Group) checks
        self.client.force_authenticate(user=self.student_b)
        response_b = self.client.get(f'/api/comments/task/{self.group_task.id}/')
        self.assertEqual(len(response_b.data), 0)  # Should NOT see it!

    def test_notification_not_sent_to_sender(self):
        """Test that when a Teacher comments, the Teacher does NOT get a notification."""
        student_comment = create_comment(author=self.student_a, content="Review my work",
                                         target_object=self.individual_task)

        # Teacher replies
        create_comment(author=self.teacher, content="Looks good.", target_object=self.individual_task,
                       parent=student_comment)

        # Check notifications
        teacher_notifications = Notification.objects.filter(recipient=self.teacher)
        student_notifications = Notification.objects.filter(recipient=self.student_a)

        self.assertEqual(teacher_notifications.count(), 0)  # Teacher shouldn't notify themselves
        self.assertEqual(student_notifications.count(), 1)  # Student A should get notified!