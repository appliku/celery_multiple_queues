from django.urls import path
from myapp import views

urlpatterns = [
    path("", views.ContactUploadListView.as_view(), name="contact_upload_list"),
    path("create", views.ContactUploadCreateView.as_view(), name="contact_upload_create"),
    path("detail/<pk>", views.ContactUploadDetailView.as_view(), name="contact_upload_detail"),
    path("csv", views.GenerateFakeContactList.as_view(), name="contact_generate"),
]