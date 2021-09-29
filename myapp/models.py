from django.db import models

from myapp.tuples import CONTACT_UPLOAD_STATUSES


class ContactUpload(models.Model):
    STATUS_CHOICES = (
        (CONTACT_UPLOAD_STATUSES.pending, 'Pending'),
        (CONTACT_UPLOAD_STATUSES.processing, 'Processing'),
        (CONTACT_UPLOAD_STATUSES.finished, 'Finished'),
        (CONTACT_UPLOAD_STATUSES.failed, 'Failed'),
    )
    contact_file = models.FileField(upload_to='uploads/%Y/%m/%d/')
    created_dt = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=CONTACT_UPLOAD_STATUSES.pending
    )

    class Meta:
        verbose_name = 'Contact Upload'
        verbose_name_plural = 'Contact Uploads'
        ordering = ('-pk',)


class Contact(models.Model):
    email = models.EmailField()
    has_mx_records = models.BooleanField(default=None, null=True)
    upload = models.ForeignKey(ContactUpload, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'
        ordering = ('email',)
