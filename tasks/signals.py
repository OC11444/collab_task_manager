from django.dispatch import receiver

from comments_notifications.signals import comment_created
from comments_notifications.services import create_notification
from tasks.models import Task, TaskSubmission


@receiver(comment_created)
def handle_comment_created(sender, comment, target_object, **kwargs):
    if isinstance(target_object, Task):
        recipients = set()

        recipients.add(target_object.unit.lecturer)

        if target_object.study_groups.exists():
            for study_group in target_object.study_groups.all():
                recipients.update(study_group.members.all())
        else:
            enrollments = target_object.unit.enrolled_students.select_related("student")
            recipients.update(
                enrollment.student for enrollment in enrollments if enrollment.student is not None
            )

        recipients.discard(comment.author)

        for user in recipients:
            create_notification(
                user,
                f"New comment on task: {target_object.title}",
                target_object=target_object,
            )
    elif isinstance(target_object, TaskSubmission):
        student = getattr(target_object, "student", None) or getattr(target_object, "user", None)
        lecturer = target_object.task.unit.lecturer

        if comment.author == student:
            recipient = lecturer
        else:
            recipient = student

        if recipient and recipient != comment.author:
            create_notification(
                recipient,
                f"New feedback on {target_object.task.title}",
                target_object=target_object,
            )