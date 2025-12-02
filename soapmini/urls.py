from django.contrib import admin
from django.urls import path
from calcapp.views import soap_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path("soap/", soap_view),
]
