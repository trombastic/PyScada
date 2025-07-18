# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import path
from . import views
from pyscada.admin import admin_site
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Public pages
    path("", views.index, name="view-overview"),
    path("pyscada_admin/", admin_site.urls),
    path("accounts/logout/", auth_views.LogoutView.as_view()),
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(template_name="login.html"),
        name="login_view",
    ),
    path(
        "accounts/choose_login/",
        auth_views.LoginView.as_view(template_name="choose_login.html"),
        name="choose_login_view",
    ),
    path(
        "accounts/password_change/",
        auth_views.PasswordChangeView.as_view(template_name="password_change.html"),
        name="password_change",
    ),
    path(
        "accounts/password_change_done/",
        auth_views.PasswordChangeView.as_view(
            template_name="password_change_done.html"
        ),
        name="password_change_done",
    ),
    path("json/cache_data/", views.get_cache_data),
    path("json/log_data/", views.log_data),
    path("form/write_task/", views.form_write_task),
    path("form/read_task/", views.form_read_task),
    path("form/read_all_task/", views.form_read_all_task),
    path("view/<link_title>/", views.view, name="main-view"),
    path(
        "getHiddenConfig2/<link_title>/",
        views.get_hidden_config2,
        name="get-hidden-config2",
    ),
    path(
        "<link_title>/", views.index, name="view-overview-link"
    ),  # this is used to add special links to the view-overview
]
