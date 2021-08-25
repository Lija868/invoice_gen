# -*- coding: utf-8 -*-
"""djangobasics URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import LoginViewSet, loaddata_general, dumpdata_general
from .views import LogoutViewSet
from .views import RegisterViewSet, InvoiceViewSet


router = DefaultRouter(trailing_slash=False)
router.register(r"register", RegisterViewSet, basename="register")
router.register(r"login", LoginViewSet, basename="login")
router.register(r"logout", LogoutViewSet, basename="logout")
router.register(r"invoice", InvoiceViewSet, basename="logout")


urlpatterns = [
    path(r"", include(router.urls)),
    path("loaddata/<model>", loaddata_general, name="loaddata_general"),
    path("dumpdata/<model>", dumpdata_general, name="dumpdata_general"),
]
