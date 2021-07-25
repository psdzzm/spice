# !usr/bin/env python
# -*- coding:utf-8 -*-
'''
 Description:
 Author: Yichen Zhang
 Date: 11-07-2021 14:55:00
 LastEditors: Yichen Zhang
 LastEditTime: 11-07-2021 15:17:24
 FilePath: /spice/src/report/report/urls.py
'''
"""report URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from htmlreport import views as htmlreport_views

urlpatterns = [
    path('', htmlreport_views.base),
    path('admin/', admin.site.urls),
]
