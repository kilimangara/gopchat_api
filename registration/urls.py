from django.conf.urls import url

from registration import views

urlpatterns = [
    url(r'^code/$', views.send_code),
    url(r'^login/$', views.login)
]
