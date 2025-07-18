# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import traceback

import pyscada.hmi.models
from pyscada.core import version as core_version
from pyscada.models import VariableProperty, Variable, Device
from pyscada.models import Log
from pyscada.models import DeviceWriteTask, DeviceReadTask
from pyscada.hmi.models import ControlItem
from pyscada.hmi.models import Form
from pyscada.hmi.models import GroupDisplayPermission
from pyscada.hmi.models import Widget
from pyscada.hmi.models import CustomHTMLPanel
from pyscada.hmi.models import Chart
from pyscada.hmi.models import View
from pyscada.hmi.models import ProcessFlowDiagram
from pyscada.hmi.models import Pie
from pyscada.hmi.models import Page
from pyscada.hmi.models import SlidingPanelMenu
from pyscada.utils import gen_hiddenConfigHtml, get_group_display_permission_list

from django.http import HttpResponse
from django.template.loader import get_template
from django.template.response import TemplateResponse
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.views.decorators.csrf import requires_csrf_token
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db.models.fields.related import OneToOneRel

import time
import json
import logging

logger = logging.getLogger(__name__)

class ViewDummy:
    def __init__(
        self,
        title="",
        link_title=None,
        link_url="",
        description="",
        url="",
        visible=True,
    ):
        self.title = title
        self.link_title = link_title
        self.link_url = link_url
        self.description = description

        class Logo:
            def __init__(self, url):
                self.url = url

            def __eq__(self, obj):
                return obj == self.url

            def __hash__(self):
                return hash(self.url)

            def __bool__(self):
                return bool(self.url)

        self.logo = Logo(url=url)
        self.visible = visible

@login_required
def index(request, link_title=""):
    if GroupDisplayPermission.objects.count() == 0:
        view_list = View.objects.all()
    else:
        view_list = list(
            get_group_display_permission_list(View.objects, request.user.groups.all())
        )

    if hasattr(settings, "OVERVIEW_ADDITIONAL_LINKS"):
        for view_data in settings.OVERVIEW_ADDITIONAL_LINKS:
            view = ViewDummy()
            view.logo.url = view_data["logo_url"] if "logo_url" in view_data else None
            view.title = view_data["title"] if "title" in view_data else ""
            view.link_title = (
                view_data["link_title"] if "link_title" in view_data else None
            )
            view.link_url = view_data["link_url"] if "link_url" in view_data else ""
            view.description = (
                view_data["description"] if "description" in view_data else ""
            )
        view_list.append(view)

    c = {
        "user": request.user,
        "view_list": view_list,
        "version_string": core_version,
        "link_target": settings.LINK_TARGET
        if hasattr(settings, "LINK_TARGET")
        else "_blank",
    }
    return TemplateResponse(
        request, "view_overview.html", c
    )  # HttpResponse(t.render(c))


@login_required
def get_hidden_config2(request, link_title):
    try:
        v = (
            get_group_display_permission_list(View.objects, request.user.groups.all())
            .filter(link_title=link_title)
            .first()
        )
        if v is None:
            raise View.DoesNotExist
        # v = View.objects.get(link_title=link_title)
    except View.DoesNotExist as e:
        logger.warning(f"{request.user} has no permission for view {link_title}")
        raise PermissionDenied("You don't have access to this view.")
    except View.MultipleObjectsReturned as e:
        logger.error(f"{e} for view link_title", exc_info=True)
        raise PermissionDenied(f"Multiples views with this link : {link_title}")
        # return HttpResponse(status=404)

    object_config_list = dict()
    custom_fields_list = dict()
    exclude_fields_list = dict()
    visible_objects_lists = dict()

    items = [
        field
        for field in GroupDisplayPermission._meta.get_fields()
        if issubclass(type(field), OneToOneRel)
    ]
    if GroupDisplayPermission.objects.count() == 0:
        # no groups
        for item in items:
            item_str = item.related_model.m2m_related_model._meta.object_name.lower()
            visible_objects_lists[
                f"visible_{item_str}_list"
            ] = item.related_model.m2m_related_model.objects.all().values_list(
                "pk", flat=True
            )
        visible_objects_lists["visible_page_list"] = v.pages.all().values_list(
            "pk", flat=True
        )
        visible_objects_lists[
            "visible_slidingpanelmenu_list"
        ] = v.sliding_panel_menus.all().values_list("pk", flat=True)
    else:
        for item in items:
            item_str = item.related_model.m2m_related_model._meta.object_name.lower()
            visible_objects_lists[
                f"visible_{item_str}_list"
            ] = get_group_display_permission_list(
                item.related_model.m2m_related_model.objects, request.user.groups.all()
            ).values_list(
                "pk", flat=True
            )
        visible_objects_lists["visible_page_list"] = get_group_display_permission_list(
            v.pages, request.user.groups.all()
        ).values_list("pk", flat=True)
        visible_objects_lists[
            "visible_slidingpanelmenu_list"
        ] = get_group_display_permission_list(
            v.sliding_panel_menus, request.user.groups.all()
        ).values_list(
            "pk", flat=True
        )

    panel_list = SlidingPanelMenu.objects.filter(
        id__in=visible_objects_lists["visible_slidingpanelmenu_list"]
    ).filter(
        position__in=(
            1,
            2,
        )
    )
    control_list = SlidingPanelMenu.objects.filter(
        id__in=visible_objects_lists["visible_slidingpanelmenu_list"]
    ).filter(position=0)

    for page_pk in visible_objects_lists["visible_page_list"]:
        page = Page.objects.get(id=page_pk)
        for widget in page.widget_set.all():
            if widget.pk not in visible_objects_lists["visible_widget_list"]:
                continue
            if not widget.visible:
                continue
            if widget.content is None:
                continue
            widget_extra_css_class = (
                widget.extra_css_class.css_class
                if widget.extra_css_class is not None
                else ""
            )
            opts = widget.content.get_hidden_config2(
                visible_objects_lists=visible_objects_lists,
            )
            if (
                type(opts) == dict
                and "object_config_list" in opts
                and type(opts["object_config_list"] == list)
            ):
                for obj in opts["object_config_list"]:
                    model_name = str(obj._meta.model_name).lower()
                    if model_name not in object_config_list:
                        object_config_list[model_name] = list()
                    if obj not in object_config_list[model_name]:
                        object_config_list[model_name].append(obj)
            if (
                type(opts) == dict
                and "custom_fields_list" in opts
                and type(opts["custom_fields_list"] == list)
            ):
                for model in opts["custom_fields_list"]:
                    custom_fields_list[str(model).lower()] = opts["custom_fields_list"][
                        model
                    ]

            if (
                type(opts) == dict
                and "exclude_fields_list" in opts
                and type(opts["exclude_fields_list"] == list)
            ):
                for model in opts["exclude_fields_list"]:
                    exclude_fields_list[str(model).lower()] = opts[
                        "exclude_fields_list"
                    ][model]

    # Adding SlidingPanelMenu to hidden config
    for s_pk in visible_objects_lists["visible_slidingpanelmenu_list"]:
        s = SlidingPanelMenu.objects.get(id=s_pk)
        if s.control_panel is not None:
            for obj in s.control_panel._get_objects_for_html(obj=s):
                if obj._meta.model_name not in object_config_list:
                    object_config_list[obj._meta.model_name] = list()
                if obj not in object_config_list[obj._meta.model_name]:
                    object_config_list[obj._meta.model_name].append(obj)
    # Generate html object hidden config
    hidden_globalConfig_html = ""
    for model, val in sorted(object_config_list.items(), key=lambda ele: ele[0]):
        hidden_globalConfig_html += '<div class="hidden ' + str(model) + 'Config2">'
        for obj in val:
            hidden_globalConfig_html += gen_hiddenConfigHtml(
                obj,
                custom_fields_list.get(model, None),
                exclude_fields_list.get(model, None),
            )
        hidden_globalConfig_html += "</div>"

    return HttpResponse(hidden_globalConfig_html, content_type="text/plain")


@login_required
@requires_csrf_token
def view(request, link_title):
    base_template = "base.html"
    view_template = "view.html"
    page_template = get_template("content_page.html")
    widget_row_template = get_template("widget_row.html")
    STATIC_URL = (
        str(settings.STATIC_URL) if hasattr(settings, "STATIC_URL") else "/static/"
    )

    try:
        v = (
            get_group_display_permission_list(View.objects, request.user.groups.all())
            .filter(link_title=link_title, visible=True)
            .first()
        )
        if v is None:
            raise View.DoesNotExist
        # v = View.objects.get(link_title=link_title)
    except View.DoesNotExist as e:
        logger.warning(f"{request.user} has no permission for view {link_title}")
        raise PermissionDenied("You don't have access to this view.")
    except View.MultipleObjectsReturned as e:
        logger.error(f"{e} for view link_title", exc_info=True)
        raise PermissionDenied(f"Multiples views with this link : {link_title}")
        # return HttpResponse(status=404)

    if v.theme is not None:
        base_template = str(v.theme.base_filename) + ".html"
        view_template = str(v.theme.view_filename) + ".html"

    visible_objects_lists = {}
    items = [
        field
        for field in GroupDisplayPermission._meta.get_fields()
        if issubclass(type(field), OneToOneRel)
    ]
    if GroupDisplayPermission.objects.count() == 0:
        # no groups
        for item in items:
            item_str = item.related_model.m2m_related_model._meta.object_name.lower()
            visible_objects_lists[
                f"visible_{item_str}_list"
            ] = item.related_model.m2m_related_model.objects.all().values_list(
                "pk", flat=True
            )
        visible_objects_lists["visible_page_list"] = v.pages.all().values_list(
            "pk", flat=True
        )
        visible_objects_lists[
            "visible_slidingpanelmenu_list"
        ] = v.sliding_panel_menus.all().values_list("pk", flat=True)
    else:
        for item in items:
            item_str = item.related_model.m2m_related_model._meta.object_name.lower()
            visible_objects_lists[
                f"visible_{item_str}_list"
            ] = get_group_display_permission_list(
                item.related_model.m2m_related_model.objects, request.user.groups.all()
            ).values_list(
                "pk", flat=True
            )
        visible_objects_lists["visible_page_list"] = get_group_display_permission_list(
            v.pages, request.user.groups.all()
        ).values_list("pk", flat=True)
        visible_objects_lists[
            "visible_slidingpanelmenu_list"
        ] = get_group_display_permission_list(
            v.sliding_panel_menus, request.user.groups.all()
        ).values_list(
            "pk", flat=True
        )

    panel_list = SlidingPanelMenu.objects.filter(
        id__in=visible_objects_lists["visible_slidingpanelmenu_list"]
    ).filter(
        position__in=(
            1,
            2,
        )
    )
    control_list = SlidingPanelMenu.objects.filter(
        id__in=visible_objects_lists["visible_slidingpanelmenu_list"]
    ).filter(position=0)

    pages_html = ""
    object_config_list = dict()
    custom_fields_list = dict()
    exclude_fields_list = dict()
    javascript_files_list = list()
    css_files_list = list()
    show_daterangepicker = False
    has_flot_chart = False
    add_context = {}

    for page_pk in visible_objects_lists["visible_page_list"]:
        # process content row by row
        page = Page.objects.get(id=page_pk)
        current_row = 0
        widget_rows_html = ""
        main_content = list()
        sidebar_content = list()
        topbar = False

        show_daterangepicker_temp = False
        show_timeline_temp = False

        for widget in page.widget_set.all():
            # check if row has changed
            if current_row != widget.row:
                # render new widget row and reset all loop variables
                widget_rows_html += widget_row_template.render(
                    {
                        "row": current_row,
                        "main_content": main_content,
                        "sidebar_content": sidebar_content,
                        "sidebar_visible": len(sidebar_content) > 0,
                        "topbar": topbar,
                    },
                    request,
                )
                current_row = widget.row
                main_content = list()
                sidebar_content = list()
                topbar = False
            if widget.pk not in visible_objects_lists["visible_widget_list"]:
                continue
            if not widget.visible:
                continue
            if widget.content is None:
                continue
            widget_extra_css_class = (
                widget.extra_css_class.css_class
                if widget.extra_css_class is not None
                else ""
            )
            mc, sbc, opts = widget.content.create_panel_html(
                widget_pk=widget.pk,
                widget_extra_css_class=widget_extra_css_class,
                visible_objects_lists=visible_objects_lists,
                request=request,
                view=v,
            )
            # main content
            if mc is None:
                logger.info(
                    f"User {request.user} not allowed to see the content of widget {widget}"
                )
            else:
                main_content.append(dict(html=mc, widget=widget, topbar=sbc))
            # sidebar content
            if sbc is not None:
                sidebar_content.append(dict(html=sbc, widget=widget))
            # options
            if type(opts) == dict:
                if "topbar" in opts and opts["topbar"] == True:
                    topbar = True
                if (
                    "show_daterangepicker" in opts
                    and opts["show_daterangepicker"] == True
                ):
                    show_daterangepicker = True
                    show_daterangepicker_temp = True
                if "show_timeline" in opts and opts["show_timeline"] == True:
                    show_timeline_temp = True
                if "flot" in opts and opts["flot"]:
                    has_flot_chart = True
                if "base_template" in opts:
                    base_template = opts["base_template"]
                if "view_template" in opts:
                    view_template = opts["view_template"]
                if "add_context" in opts:
                    add_context.update(opts["add_context"])
                if "javascript_files_list" in opts:
                    for file_src in opts["javascript_files_list"]:
                        if {"src": file_src} not in javascript_files_list:
                            javascript_files_list.append({"src": file_src})
                if "css_files_list" in opts:
                    for file_src in opts["css_files_list"]:
                        if {"src": file_src} not in css_files_list:
                            css_files_list.append({"src": file_src})
                if "object_config_list" in opts and type(
                    opts["object_config_list"] == list
                ):
                    for obj in opts["object_config_list"]:
                        model_name = str(obj._meta.model_name).lower()
                        if model_name not in object_config_list:
                            object_config_list[model_name] = list()
                        if obj not in object_config_list[model_name]:
                            object_config_list[model_name].append(obj)
                if "custom_fields_list" in opts and type(
                    opts["custom_fields_list"] == list
                ):
                    for model in opts["custom_fields_list"]:
                        custom_fields_list[str(model).lower()] = opts[
                            "custom_fields_list"
                        ][model]

                if "exclude_fields_list" in opts and type(
                    opts["exclude_fields_list"] == list
                ):
                    for model in opts["exclude_fields_list"]:
                        exclude_fields_list[str(model).lower()] = opts[
                            "exclude_fields_list"
                        ][model]
            else:
                logger.info(f"Widget {widget} options is not a dict, it is {opts}")
        widget_rows_html += widget_row_template.render(
            {
                "row": current_row,
                "main_content": main_content,
                "sidebar_content": sidebar_content,
                "sidebar_visible": len(sidebar_content) > 0,
                "topbar": topbar,
            },
            request,
        )

        pages_html += page_template.render(
            {
                "page": page,
                "widget_rows_html": widget_rows_html,
                "show_daterangepicker": show_daterangepicker_temp,
                "show_timeline": show_timeline_temp,
            },
            request,
        )

    # Generate javascript files list
    if has_flot_chart:
        javascript_files_list.append(
            {"src": STATIC_URL + "pyscada/js/jquery/jquery.tablesorter.min.js"}
        )
        # tablesorter parser for checkbox
        javascript_files_list.append(
            {"src": STATIC_URL + "pyscada/js/jquery/parser-input-select.js"}
        )
        javascript_files_list.append(
            {"src": STATIC_URL + "pyscada/js/flot/lib/jquery.event.drag.js"}
        )
        javascript_files_list.append(
            {"src": STATIC_URL + "pyscada/js/flot/lib/jquery.mousewheel.js"}
        )
        javascript_files_list.append(
            {"src": STATIC_URL + "pyscada/js/flot/source/jquery.canvaswrapper.js"}
        )
        javascript_files_list.append(
            {"src": STATIC_URL + "pyscada/js/flot/source/jquery.colorhelpers.js"}
        )
        javascript_files_list.append(
            {"src": STATIC_URL + "pyscada/js/flot/source/jquery.flot.js"}
        )
        javascript_files_list.append(
            {"src": STATIC_URL + "pyscada/js/flot/source/jquery.flot.saturated.js"}
        )
        javascript_files_list.append(
            {"src": STATIC_URL + "pyscada/js/flot/source/jquery.flot.browser.js"}
        )
        javascript_files_list.append(
            {"src": STATIC_URL + "pyscada/js/flot/source/jquery.flot.drawSeries.js"}
        )
        javascript_files_list.append(
            {"src": STATIC_URL + "pyscada/js/flot/source/jquery.flot.errorbars.js"}
        )
        javascript_files_list.append(
            {"src": STATIC_URL + "pyscada/js/flot/source/jquery.flot.uiConstants.js"}
        )
        javascript_files_list.append(
            {"src": STATIC_URL + "pyscada/js/flot/source/jquery.flot.logaxis.js"}
        )
        javascript_files_list.append(
            {"src": STATIC_URL + "pyscada/js/flot/source/jquery.flot.symbol.js"}
        )
        javascript_files_list.append(
            {"src": STATIC_URL + "pyscada/js/flot/source/jquery.flot.flatdata.js"}
        )
        javascript_files_list.append(
            {"src": STATIC_URL + "pyscada/js/flot/source/jquery.flot.navigate.js"}
        )
        javascript_files_list.append(
            {"src": STATIC_URL + "pyscada/js/flot/source/jquery.flot.fillbetween.js"}
        )
        javascript_files_list.append(
            {"src": STATIC_URL + "pyscada/js/flot/source/jquery.flot.stack.js"}
        )
        javascript_files_list.append(
            {"src": STATIC_URL + "pyscada/js/flot/source/jquery.flot.touchNavigate.js"}
        )
        javascript_files_list.append(
            {"src": STATIC_URL + "pyscada/js/flot/source/jquery.flot.hover.js"}
        )
        javascript_files_list.append(
            {"src": STATIC_URL + "pyscada/js/flot/source/jquery.flot.touch.js"}
        )
        javascript_files_list.append(
            {"src": STATIC_URL + "pyscada/js/flot/source/jquery.flot.time.js"}
        )
        javascript_files_list.append(
            {"src": STATIC_URL + "pyscada/js/flot/source/jquery.flot.axislabels.js"}
        )
        javascript_files_list.append(
            {"src": STATIC_URL + "pyscada/js/flot/source/jquery.flot.selection.js"}
        )
        javascript_files_list.append(
            {"src": STATIC_URL + "pyscada/js/flot/source/jquery.flot.composeImages.js"}
        )
        javascript_files_list.append(
            {"src": STATIC_URL + "pyscada/js/flot/source/jquery.flot.legend.js"}
        )
        javascript_files_list.append(
            {"src": STATIC_URL + "pyscada/js/flot/source/jquery.flot.pie.js"}
        )
        javascript_files_list.append(
            {"src": STATIC_URL + "pyscada/js/flot/source/jquery.flot.crosshair.js"}
        )
        javascript_files_list.append(
            {"src": STATIC_URL + "pyscada/js/flot/source/jquery.flot.gauge.js"}
        )
        javascript_files_list.append(
            {"src": STATIC_URL + "pyscada/js/jquery.flot.axisvalues.js"}
        )

    if show_daterangepicker:
        javascript_files_list.append(
            {"src": STATIC_URL + "pyscada/js/daterangepicker/moment.min.js"}
        )
        javascript_files_list.append(
            {"src": STATIC_URL + "pyscada/js/daterangepicker/daterangepicker.min.js"}
        )

    javascript_files_list.append(
        {"src": STATIC_URL + "pyscada/js/pyscada/pyscada_v0-8-3.js"}
    )

    # Generate css files list
    css_files_list.append(
        {"src": STATIC_URL + "pyscada/css/daterangepicker/daterangepicker.css"}
    )

    # Adding SlidingPanelMenu to hidden config
    for s_pk in visible_objects_lists["visible_slidingpanelmenu_list"]:
        s = SlidingPanelMenu.objects.get(id=s_pk)
        if s.control_panel is not None:
            for obj in s.control_panel._get_objects_for_html(obj=s):
                if obj._meta.model_name not in object_config_list:
                    object_config_list[obj._meta.model_name] = list()
                if obj not in object_config_list[obj._meta.model_name]:
                    object_config_list[obj._meta.model_name].append(obj)
    # Add html object hidden config div so that it can be filled in later
    pages_html += '<div class="hidden globalConfig2">'
    pages_html += "</div>"

    context = {
        "base_html": base_template,
        "include": [],
        "page_list": Page.objects.filter(
            id__in=visible_objects_lists["visible_page_list"]
        ),
        "pages_html": pages_html,
        "panel_list": panel_list,
        "control_list": control_list,
        "user": request.user,
        "visible_control_element_list": visible_objects_lists[
            "visible_controlitem_list"
        ],
        "visible_form_list": visible_objects_lists["visible_form_list"],
        "view_object": v,
        "view_title": v.title,
        "view_link_title": link_title,
        "view_show_timeline": v.show_timeline,
        "view_time_delta": v.default_time_delta.total_seconds(),
        "version_string": core_version,
        "link_target": settings.LINK_TARGET
        if hasattr(settings, "LINK_TARGET")
        else "_blank",
        "javascript_files_list": javascript_files_list,
        "css_files_list": css_files_list,
    }
    context.update(add_context)

    return TemplateResponse(request, view_template, context)


@login_required
def log_data(request):
    if "timestamp" in request.POST:
        timestamp = float(request.POST["timestamp"])
    else:
        timestamp = (time.time() - 300) * 1000  # get log of last 5 minutes

    data = Log.objects.filter(
        level__gte=6, id__gt=int(int(timestamp) * 2097152) + 2097151
    ).order_by("-timestamp")
    odata = []
    for item in data:
        odata.append(
            {
                "timestamp": item.timestamp * 1000,
                "level": item.level,
                "message": item.message,
                "username": item.user.username if item.user else "None",
            }
        )
    jdata = json.dumps(odata, indent=2)

    return HttpResponse(jdata, content_type="application/json")


@login_required
def form_read_all_task(request):
    crts = []
    for device in Device.objects.all():
        crts.append(DeviceReadTask(device=device, start=time.time(), user=request.user))
    if len(crts) > 0:
        crts[0].create_and_notificate(crts)
    return HttpResponse(status=200)


@login_required
def form_read_task(request):
    if "key" in request.POST and "type" in request.POST:
        key = int(request.POST["key"])
        item_type = request.POST["type"]
        if GroupDisplayPermission.objects.count() == 0:
            if item_type == "variable":
                crt = DeviceReadTask(
                    device=Variable.objects.get(pk=key).device,
                    start=time.time(),
                    user=request.user,
                )
                crt.create_and_notificate(crt)
                return HttpResponse(status=200)
            elif item_type == "variable_property":
                crt = DeviceReadTask(
                    device=VariableProperty.objects.get(pk=key).variable.device,
                    start=time.time(),
                    user=request.user,
                )
                crt.create_and_notificate(crt)
                return HttpResponse(status=200)
        else:
            if item_type == "variable":
                if (
                    get_group_display_permission_list(
                        ControlItem.objects, request.user.groups.all()
                    )
                    .filter(type=1, variable_id=key)
                    .exists()
                ):
                    crt = DeviceReadTask(
                        device=Variable.objects.get(pk=key).device,
                        start=time.time(),
                        user=request.user,
                    )
                    crt.create_and_notificate(crt)
                    return HttpResponse(status=200)
                else:
                    logger.warning(
                        f"User {request.user} has no right to add read task "
                        f"for variable {Variable.objects.get(pk=key)}"
                    )
                    return HttpResponse(status=404)
            elif item_type == "variable_property":
                if (
                    get_group_display_permission_list(
                        ControlItem.objects, request.user.groups.all()
                    )
                    .filter(type=1, variable_property_id=key)
                    .exists()
                ):
                    crt = DeviceReadTask(
                        device=VariableProperty.objects.get(pk=key).variable.device,
                        start=time.time(),
                        user=request.user,
                    )
                    crt.create_and_notificate(crt)
                    return HttpResponse(status=200)
                else:
                    logger.warning(
                        f"User {request.user} has no right to add read task "
                        f"for variable property {VariableProperty.objects.get(pk=key)}"
                    )
                    return HttpResponse(status=404)
        logger.warning(f"Wrong read task request, POST is : {request.POST}")
    return HttpResponse(status=404)


@login_required
def form_write_task(request):
    if "key" in request.POST and "value" in request.POST:
        key = int(request.POST["key"])
        item_type = request.POST["item_type"]
        value = request.POST["value"]
        # check if float as DeviceWriteTask doesn't support string values
        try:
            float(value)
        except ValueError:
            try:
                vp = VariableProperty.objects.get(id=key)
                if item_type == "variable_property" and vp.value_class.upper() in [
                    "STRING"
                ]:
                    VariableProperty.objects.update_property(
                        variable_property=vp,
                        value=value,
                    )
                    # TODO: write string
                    # cwt = DeviceWriteTask(
                    #    variable_property_id=key,
                    #    value=value,
                    #    start=time.time(),
                    #    user=request.user,
                    # )
                    # cwt.create_and_notificate(cwt)
                    return HttpResponse(status=200)
            except VariableProperty.DoesNotExist:
                pass
            logger.info(f"Cannot write STRING '{value}' to {item_type} {key}")
            return HttpResponse(status=403)
        if GroupDisplayPermission.objects.count() == 0:
            if item_type == "variable":
                cwt = DeviceWriteTask(
                    variable_id=key, value=value, start=time.time(), user=request.user
                )
                cwt.create_and_notificate(cwt)
                return HttpResponse(status=200)
            elif item_type == "variable_property":
                cwt = DeviceWriteTask(
                    variable_property_id=key,
                    value=value,
                    start=time.time(),
                    user=request.user,
                )
                cwt.create_and_notificate(cwt)
                return HttpResponse(status=200)
        else:
            if "view_id" in request.POST:
                # for a view, get the list of variables and variable properties for which the user can retrieve and write data
                view_id = int(request.POST["view_id"])
                vdo = View.objects.get(id=view_id).data_objects(request.user)
            else:
                vdo = None  # should it get data objets for all views ?

            if item_type == "variable":
                can_write = False
                if vdo is not None:
                    # filter active_variables using variables from which the user can write data
                    if "variable_write" in vdo and int(key) in vdo["variable_write"]:
                        can_write = True
                    else:
                        logger.info(
                            f"variable {key} not allowed to write in view {view_id} for user {request.user}"
                        )
                else:
                    # keeping old check, remove it later
                    if (
                        get_group_display_permission_list(
                            ControlItem.objects, request.user.groups.all()
                        )
                        .filter(type=0, variable_id=key)
                        .exists()
                    ):
                        can_write = True
                    else:
                        logger.debug(
                            "Missing group display permission for write task (variable %s)"
                            % key
                        )
                if can_write:
                    cwt = DeviceWriteTask(
                        variable_id=key,
                        value=value,
                        start=time.time(),
                        user=request.user,
                    )
                    cwt.create_and_notificate(cwt)
                    return HttpResponse(status=200)
            elif item_type == "variable_property":
                can_write = False
                if vdo is not None:
                    # filter active_variables using variables from which the user can write data
                    if (
                        "variable_property_write" in vdo
                        and int(key) in vdo["variable_property_write"]
                    ):
                        can_write = True
                    else:
                        logger.info(
                            f"variable property {key} not allowed to write in view {view_id} for user {request.user}"
                        )
                else:
                    # keeping old check, remove it later
                    if (
                        get_group_display_permission_list(
                            ControlItem.objects, request.user.groups.all()
                        )
                        .filter(type=0, variable_property_id=key)
                        .exists()
                    ):
                        can_write = True
                    else:
                        logger.debug(
                            "Missing group display permission for write task (VP %s)"
                            % key
                        )
                if can_write:
                    cwt = DeviceWriteTask(
                        variable_property_id=key,
                        value=value,
                        start=time.time(),
                        user=request.user,
                    )
                    cwt.create_and_notificate(cwt)
                    return HttpResponse(status=200)
    else:
        logger.debug("key or value missing in request : %s" % request.POST)
    return HttpResponse(status=404)


def int_filter(someList):
    for v in someList:
        try:
            int(v)
            yield v  # Keep these
        except ValueError:
            continue  # Skip these


@login_required
def get_cache_data(request):
    if "view_id" in request.POST:
        # for a view, get the list of variables and variable properties for which the user can retrieve and write data
        view_id = int(request.POST["view_id"])
        vdo = View.objects.get(id=view_id).data_objects(request.user)
    else:
        vdo = None  # should it get data objets for all views ?

    if "init" in request.POST:
        init = bool(float(request.POST["init"]))
    else:
        init = False
    active_variables = []
    if "variables" in request.POST:
        active_variables = request.POST.get("variables")
        active_variables = list(int_filter(active_variables.split(",")))
        if vdo is not None:
            # filter active_variables using variables from which the user can retrieve data
            variables_filtered = []
            for var_pk in active_variables:
                if "variable" in vdo and int(var_pk) in vdo["variable"]:
                    variables_filtered.append(var_pk)
                else:
                    logger.info(
                        f"variable {var_pk} not allowed in view {view_id} for user {request.user}"
                    )
            active_variables = variables_filtered

    """
    else:
        active_variables = list(
            GroupDisplayPermission.objects.filter(hmi_group__in=request.user.groups.iterator()).values_list(
                'charts__variables', flat=True))
        active_variables += list(
            GroupDisplayPermission.objects.filter(hmi_group__in=request.user.groups.iterator()).values_list(
                'control_items__variable', flat=True))
        active_variables += list(
            GroupDisplayPermission.objects.filter(hmi_group__in=request.user.groups.iterator()).values_list(
                'custom_html_panels__variables', flat=True))
        active_variables = list(set(active_variables))
    """

    active_variable_properties = []
    if "variable_properties" in request.POST:
        active_variable_properties = request.POST.get("variable_properties")
        active_variable_properties = list(
            int_filter(active_variable_properties.split(","))
        )
        if vdo is not None:
            # filter active_variable_properties using variables from which the user can retrieve data
            variable_properties_filtered = []
            for var_pk in active_variable_properties:
                if (
                    "variable_property" in vdo
                    and int(var_pk) in vdo["variable_property"]
                ):
                    variable_properties_filtered.append(var_pk)
                else:
                    logger.info(
                        f"variable property {var_pk} not allowed in view {view_id} for user {request.user}"
                    )
            active_variable_properties = variable_properties_filtered

    timestamp_from = time.time()
    if "timestamp_from" in request.POST:
        timestamp_from = float(request.POST["timestamp_from"]) / 1000.0
    if timestamp_from == 0:
        timestamp_from = time.time() - 60

    timestamp_to = time.time()
    if "timestamp_to" in request.POST:
        timestamp_to = min(timestamp_to, float(request.POST["timestamp_to"]) / 1000.0)
    if timestamp_to == 0:
        timestamp_to = time.time()

    # if timestamp_to - timestamp_from > 120 * 60 and not init:
    #    timestamp_from = timestamp_to - 120 * 60

    # if not init:
    # timestamp_to = min(timestamp_from + 30, timestamp_to)

    if len(active_variables) > 0:
        kwargs = {
            "variable_ids": active_variables,
            "time_min": timestamp_from,
            "time_max": timestamp_to,
            "time_in_ms": True,
            "query_first_value": init,
        }
        data = Variable.objects.read_multiple(**kwargs)
    else:
        data = None

    if data is None:
        data = {}

    # Add data for variable not logging to RecordedData model (as systemstat timestamps).
    for v_id in active_variables:
        if int(v_id) not in data:
            try:
                v = Variable.objects.get(id=v_id)
                v.query_prev_value(timestamp_from / 1000)
                # add 5 seconds to let the request from the server to come
                if (
                    v.timestamp_old is not None
                    and v.timestamp_old <= timestamp_to + 5
                    and v.prev_value is not None
                ):
                    data[int(v_id)] = [[v.timestamp_old * 1000, v.prev_value]]
            except:
                # logger.warning(traceback.format_exc())
                pass

    data["variable_properties"] = {}
    data["variable_properties_last_modified"] = {}

    for item in VariableProperty.objects.filter(pk__in=active_variable_properties):
        data["variable_properties"][item.pk] = item.value()
        data["variable_properties_last_modified"][item.pk] = (
            item.last_modified.timestamp() * 1000
        )

    data["server_time"] = time.time() * 1000
    return HttpResponse(json.dumps(data), content_type="application/json")
