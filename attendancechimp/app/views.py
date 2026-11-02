from __future__ import annotations

from datetime import datetime
from decimal import Decimal, InvalidOperation
from zoneinfo import ZoneInfo

from django.http import HttpRequest, HttpResponse
from django.template import loader

from django.views.decorators.http import require_GET, require_POST

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

from django.views.decorators.csrf import csrf_exempt


CDT = ZoneInfo("America/Chicago")


def time_view(request: HttpRequest) -> HttpResponse:
    """Return current Chicago time as HH:MM (24-hour), plain text."""
    now = datetime.now(tz=CDT)
    return HttpResponse(now.strftime("%H:%M"), content_type="text/plain")


def _decimal_to_str(x: Decimal) -> str:
    """Format Decimal without scientific notation and without trailing zeros."""
    s = format(x, "f")
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s


def sum_view(request: HttpRequest) -> HttpResponse:
    """Return n1 + n2 from query params as plain text."""
    n1_str = request.GET.get("n1", "0")
    n2_str = request.GET.get("n2", "0")

    try:
        val = Decimal(n1_str) + Decimal(n2_str)
    except (InvalidOperation, ValueError):
        return HttpResponse("Bad Request: n1 and n2 must be numbers", status=400, content_type="text/plain")

    return HttpResponse(_decimal_to_str(val), content_type="text/plain")

def index(request):
    bio = 'This is the AttendanceChimp App'
    user_name = request.user if request.user.is_authenticated else "Not logged in"
    time = datetime.now().strftime('%H:%M')

    context = {
        'bio': bio,
        'name': user_name,
        'time': time
    }

    template = loader.get_template('app/index.html')
    rendered_html = template.render(context, request)
    return HttpResponse(rendered_html)

def new(request):
    if request.method == "GET":
        template = loader.get_template('app/new.html')
        return HttpResponse(template.render({}, request))
    else: 
        return HttpResponse("Method not allowed", status=405)

@csrf_exempt
def create_new(request):
    if request.method == "POST":
        user_name = request.POST.get("user_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        is_student = request.POST.get("is_student")
        
        print(User.objects.all())

        if not user_name or not password:
                return HttpResponse("Username and password are required.", status=400)

        user_exists = User.objects.filter(email=email).exists()

        if user_exists:
            return HttpResponse("That email is already taken.", status=400)
        
        new_user = User.objects.create_user(
            username=user_name, 
            email=email, 
            password=password, 
            is_staff=not bool(is_student)
        )

        login(request, new_user)

        return HttpResponse("User has been created!", status=200)
    
    return HttpResponse("Method Not Allowed", status=405)



