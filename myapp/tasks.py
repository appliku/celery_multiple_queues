import logging
import dns.resolver
from celery import shared_task, current_app
from django.core.cache import cache
from django.db import transaction
from django.urls import reverse

from myapp.models import ContactUpload, Contact
from myapp.tuples import CONTACT_UPLOAD_STATUSES

logger = logging.getLogger(__name__)


@shared_task(name="process_uploaded_file")
def process_uploaded_file(upload_id: int):
    try:
        contact_upload = ContactUpload.objects.get(pk=upload_id)
    except ContactUpload.DoesNotExist:
        return
    contact_upload.status = CONTACT_UPLOAD_STATUSES.processing
    contact_upload.save(update_fields=['status', ])
    try:
        file_data = contact_upload.contact_file.read()
        lines = file_data.decode('utf-8').split('\n')
        for line in lines:
            contact = contact_upload.contact_set.create(email=line)
            transaction.on_commit(
                lambda: current_app.send_task(
                    'process_contact_mx_records',
                    kwargs={"contact_id": contact.id},
                    queue="numerous"))
        contact_upload.status = CONTACT_UPLOAD_STATUSES.finished
        contact_upload.save(update_fields=['status', ])
    except Exception as e:
        contact_upload.status = CONTACT_UPLOAD_STATUSES.failed
        contact_upload.error_message = str(e)
        contact_upload.save(update_fields=['error_message', 'status', ])


@shared_task(name="process_contact_mx_records")
def process_contact_mx_records(contact_id: int):
    try:
        contact = Contact.objects.get(pk=contact_id)
    except Contact.DoesNotExist:
        return False
    domain = contact.email.split('@')[1]
    try:
        nameservers = dns.resolver.resolve(domain, rdtype='MX', search=True)
    except Exception as e:
        _ = e
        logger.error(f"Exception while getting MX records for domain {domain}: {e}")
        contact.has_mx_records = False
        contact.save(update_fields=['has_mx_records', ])
        return
    logger.debug(f"{nameservers} {dir(nameservers)}")
    contact.has_mx_records = len(list(nameservers)) > 0
    contact.save(update_fields=['has_mx_records', ])


@shared_task(name="update_contact_lists_numbers")
def update_contact_lists_numbers():
    with cache.lock("update_contact_list_numbers", timeout=60, blocking_timeout=1):
        contact_lists = [{
            "pk": c.pk,
            "url": reverse('contact_upload_detail', args=(str(c.pk),)),
            "file": c.contact_file.name,
            "status": c.get_status_display()
        } for c in ContactUpload.objects.all()]
        cache.set("contact_lists", contact_lists, 60 * 2)
