# -*- coding: utf-8 -*-
import os
import datetime

import pandas as pd
from django.apps import apps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.html import format_html
from django.views.decorators.cache import cache_control
from rest_framework.decorators import action

from authentication.authentication import JwtTokensAuthentication

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.core import management
from django.utils import timezone
from jwt_utils.jwt_generator import jwt_generator
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

from users.models import Token, Invoice

from utils.message_utils import get_message

from utils.validation_utils import validate_email
from utils.validation_utils import validate_null_or_empty
from utils.validation_utils import validate_password
from .forms import ConfirmationForm

from .serializers import RegisterSerializer, LoginSerializer, InvoiceSerializer
from invoice_gen import settings
from invoice_gen.settings import logger

# Create your views here.


class RegisterViewSet(viewsets.ModelViewSet):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = RegisterSerializer
    queryset = get_user_model().objects.all()

    def create(self, request, *args, **kwargs):

        email = request.data.get("email")
        user_name = request.data.get("user_name", "")
        password = request.data.get("password", None)

        # display what are the fields which tent to empty.
        validations = []
        validations = validate_null_or_empty(email, 307, validations)
        validations = validate_null_or_empty(password, 305, validations)
        validations = validate_null_or_empty(user_name, 304, validations)

        if len(validations) > 0:
            resp = {}
            resp["code"] = 600
            resp["validations"] = validations
            return Response(resp, status=status.HTTP_412_PRECONDITION_FAILED)

        if not validate_email(email):
            return Response(
                {"code": 604, "message": get_message(604)},
                status=status.HTTP_412_PRECONDITION_FAILED,
            )

        if not validate_password(password):
            return Response(
                {"code": 618, "message": get_message(618)},
                status=status.HTTP_412_PRECONDITION_FAILED,
            )

        user_obj = get_user_model().objects.filter(email=email).count()
        if user_obj >= 1:
            return Response(
                {"code": 621, "message": get_message(621)},
                status=status.HTTP_412_PRECONDITION_FAILED,
            )

        user = get_user_model().objects.create_user(request.data)

        return Response(
            {"code": 200, "message": get_message(200), "user_id": user._get_pk_val()}
        )


class LoginViewSet(viewsets.ModelViewSet):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = LoginSerializer

    def create(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")
        # display what are the fields which tent to empty.
        validations = []
        validations = validate_null_or_empty(email, 307, validations)
        validations = validate_null_or_empty(password, 305, validations)

        if len(validations) > 0:
            resp = {}
            resp["code"] = 600
            resp["validations"] = validations
            return Response(resp, status=status.HTTP_412_PRECONDITION_FAILED)
        try:
            user_obj = get_user_model().objects.get(email=email, is_verified=True)
            valid = user_obj.check_password(password)

            if not valid:
                # logger.error({"code": 503, "message": get_message(503)})
                return Response(
                    {"code": 503, "message": get_message(503)},
                    status.HTTP_412_PRECONDITION_FAILED,
                )
            access_token = jwt_generator(
                user_obj.id,
                settings.JWT_SECRET,
                settings.TOKEN_EXPIRY,
                "access",
                user_obj.is_superuser,
            )
            refresh_token = jwt_generator(
                user_obj.id,
                settings.JWT_SECRET,
                settings.REFRESH_TOKEN_EXPIRY,
                "refresh",
                user_obj.is_superuser,
            )
            Token.objects.filter(user_id=user_obj).update(is_expired=1)

            Token.objects.update_or_create(
                user_id=user_obj,
                access_token=access_token,
                refresh_token=refresh_token,
                defaults={"updated_at": timezone.now()},
            )
            return Response(
                {
                    "code": 200,
                    "message": get_message(200),
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user_id": user_obj.pk,
                    "email": user_obj.email,
                }
            )

        except ObjectDoesNotExist as ex:
            logger.error(ex)
            return Response(
                {"code": 204, "message": get_message(204)},
                status.HTTP_400_BAD_REQUEST,
            )


class LogoutViewSet(viewsets.ModelViewSet):
    permission_classes = ()
    authentication_classes = [JwtTokensAuthentication]
    serializer_class = ()

    def create(self, request, *args, **kwargs):
        user_id = request.user.get("user_id")
        token_id = request.headers.get("Authorization", "")
        try:
            get_user_model().objects.get(pk=user_id, is_verified=True)
        except ObjectDoesNotExist as ex:
            logger.error(ex)
            return Response(
                {"code": 204, "message": get_message(204)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token_obj = Token.objects.get(access_token=token_id, user_id=user_id)
            token_obj.is_expired = 1
            token_obj.save()
            return Response({"code": 200, "message": get_message(200)})
        except Exception as ex:
            logger.error(ex)
            return Response(
                {"code": 114, "message": get_message(114)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class InvoiceViewSet(viewsets.ModelViewSet):
    authentication_classes = (JwtTokensAuthentication,)
    permission_classes = ()
    serializer_class = InvoiceSerializer
    queryset = get_user_model().objects.all()

    def create(self, request, *args, **kwargs):
        invoices = request.data.get("invoices", [])
        # display what are the fields which tent to empty.
        validations = []
        validations = validate_null_or_empty(invoices, 325, validations)
        if len(validations) > 0:
            resp = {}
            resp["code"] = 600
            resp["validations"] = validations
            return Response(resp, status=status.HTTP_412_PRECONDITION_FAILED)
        lines = []
        remaining_lines = []
        for data in invoices:
            if data.get("quantity") and data.get("quantity") > 0:
                data["user_id_id"] = request.user.get("user_id")
                lines.append(Invoice(**data))
            else:
                remaining_lines.append(data)

        try:
            Invoice.objects.bulk_create(lines)
            return Response(
                {
                    "code": 200,
                    "message": get_message(200),
                    "error_lines": remaining_lines,
                }
            )

        except Exception:
            return Response(
                {
                    "success": False,
                    "message": get_message(114),
                    "code": 114,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @cache_control(max_age=0)
    @action(detail=False, url_path="generate-invoice", methods=["POST"])
    def generate_invoice(self, request, *args, **kwargs):
        sub_total = 0
        sub_total_tax = 0
        final_amount = 0
        item = []
        user_id = request.user.get("user_id")
        for invoice in Invoice.objects.filter(user_id=user_id):
            item.append({"name": invoice.name, "total": invoice.total_price})
            sub_total += invoice.total_price
            sub_total_tax += invoice.total_price + invoice.tax_amount
            final_amount += sub_total_tax - invoice.discount_amount

        labels = [i for i in range(1, len(item) + 1)]
        columns = ["Name", "Total Price"]
        df = pd.DataFrame(0.00, index=labels, columns=columns)

        for index, data in enumerate(item):
            df.loc[index + 1] = list(data.values())

        html_content = str(df.to_html())
        html_content += """
        <div>
                        <div>Subtotal without tax: {{tax}}</div>
                        <div>Subtotal with tax: {{with_tax}}</div>
                        <div>Final amount with discount applied : {{amount}}</div>
        </div>
                    """

        html_content = html_content.replace("{{tax}}", str(sub_total))
        html_content = html_content.replace("{{with_tax}}", str(sub_total_tax))
        html_content = html_content.replace("{{amount}}", str(final_amount))

        from weasyprint import HTML

        name = "report_" + str(user_id) + ".pdf"
        path = os.path.join(settings.MEDIA_ROOT, name)
        HTML(string=html_content).write_pdf(path, stylesheets=["users/style.css"])

        return Response(
            {
                "code": 200,
                "message": get_message(200),
                "path": settings.BASIC_PDF_URL + name,
            }
        )


@login_required
def loaddata_general(request, model):
    if request.method == "POST":
        application = request.POST.get("application")
        model = request.POST.get("model")
        file = model.lower() + ".json"
        management.call_command("loaddata", file)
        messages.add_message(
            request,
            messages.INFO,
            format_html(
                "The <em>`%s`</em> fixture has been successfully loaded "
                "with a <em>loaddata</em> operation." % file
            ),
        )
        # Redirects to the admin page for the relevant model
        return redirect("/admin/%s/%s/" % (application, model.lower()))
    elif request.method == "GET":
        application = list(filter(None, request.META.get("HTTP_REFERER").split("/")))[
            -2
        ]
        initial = context = {"model": model, "application": application}
        context["heading_keyword"] = "loaddata"
        context["action_string"] = "load the fixture for"
        context["confirmation_form"] = ConfirmationForm(initial=initial)
        context["warning"] = format_html(
            "Beware that <em>loaddata</em> can damage data!"
        )
        return render(request, "users/confirm_loaddata_form.html", context)


@login_required
def dumpdata_general(request, model):
    application = list(filter(None, request.META.get("HTTP_REFERER").split("/")))[-2]
    # Dumps data from installed models to main fixtures folder

    path = "%s/fixtures/%s.json" % (application, model.lower())
    # A clean dumpdata
    with open(path, "w") as f:
        management.call_command(
            "dumpdata", "%s.%s" % (application, model), stdout=f, indent=2
        )
    messages.add_message(
        request,
        messages.INFO,
        format_html(
            "A <em>dumpdata</em> command has been executed and the "
            "data of the <em>`%s`</em> model of the <em>`%s`</em> application have successfully been saved in a "
            "<em>fixture</em>." % (model, application)
        ),
    )
    env_variables = dict(os.environ.items())
    if "app" in env_variables and env_variables["app"] == "prod":
        message = "fixtures from server " + str(datetime.datetime.now())
        os.system("git add " + path)
        os.system('git commit -m "' + message + '"')
        os.system("git push origin dev")
    # A backup dumpdata (with date in file name)
    if "site-packages" in apps.get_app_config(application).path:
        path = "fixtures/%s.json" % (
            str(model.lower()) + "_" + str(datetime.date.today())
        )
    else:
        path = "%s/fixtures/%s.json" % (
            application,
            str(model.lower()) + "_" + str(datetime.date.today()),
        )
    with open(path, "w") as f:
        management.call_command(
            "dumpdata", "%s.%s" % (application, model), stdout=f, indent=2
        )
    messages.add_message(
        request,
        messages.INFO,
        format_html(
            "The <em>`%s`</em> model of the <em>`%s`</em> application "
            "has been successfully backed up with a <em>dumpdata</em> fixture with todays date."
            % (model, application)
        ),
    )
    # Redirects to the admin page for the relevant model
    return redirect("/admin/%s/%s/" % (application, model.lower()))
