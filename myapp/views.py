from io import BytesIO

from celery import current_app
from django.core.cache import cache
from django.db import transaction
from django.http import FileResponse
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, DetailView, TemplateView
from faker import Faker

from myapp.models import ContactUpload
from myapp.tuples import CONTACT_UPLOAD_STATUSES


class ContactUploadListView(TemplateView):
    model = ContactUpload
    template_name = 'myapp/list.html'

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['object_list'] = cache.get('contact_lists', [])
        return kwargs


class ContactUploadCreateView(CreateView):
    template_name = 'myapp/create.html'
    model = ContactUpload
    fields = ('contact_file',)

    def get_success_url(self):
        return reverse('contact_upload_detail', args=(str(self.object.pk),))

    def form_valid(self, form):
        response = super().form_valid(form)
        transaction.on_commit(
            lambda: current_app.send_task(
                "process_uploaded_file",
                kwargs={"upload_id": self.object.id}, queue="long"))
        return response


class ContactUploadDetailView(DetailView):
    template_name = 'myapp/detail.html'
    model = ContactUpload
    object: ContactUpload

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        if self.object.status == CONTACT_UPLOAD_STATUSES.finished:
            kwargs['processing_finished'] = True
        return kwargs


class GenerateFakeContactList(View):
    def generate_data(self, number_contacts):
        fake = Faker('en_US')

        memory_file = BytesIO()
        content = '\n'.join([fake.email() for i in range(number_contacts)]).encode('utf-8')
        memory_file.write(content)
        memory_file.seek(0)
        return memory_file

    def get(self, request, *args, **kwargs):
        number_contacts = 100
        if request.GET.get('number_contacts'):
            number_contacts = int(request.GET.get('number_contacts'))
        return FileResponse(self.generate_data(number_contacts), filename="output.csv", as_attachment=True)
