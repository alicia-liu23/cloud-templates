from django.urls import path

from . import views

urlpatterns = [
    path('', views.contact),
    path('yaml', views.yaml_form),
    path('terraform', views.terraform_form)
]