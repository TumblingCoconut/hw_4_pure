from __future__ import annotations

from datetime import datetime
from decimal import Decimal, InvalidOperation
from zoneinfo import ZoneInfo

from django.http import HttpRequest, HttpResponse
from django.template import loader

from django.views.decorators.http import require_GET, require_POST

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from app.models import Course
from app.models import Lecture
from app.models import *

from django.views.decorators.csrf import csrf_exempt

from django.http import JsonResponse, HttpResponse


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
    ''''''
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

@require_GET
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
            is_staff= not(is_student == "student")
        )

        if is_student == "student":
            StudentProfile.objects.create(user=new_user)
        else:
            InstructorProfile.objects.create(user=new_user)

        login(request, new_user)

        return HttpResponse("User has been created!", status=200)
    
    return HttpResponse("Method Not Allowed", status=405)

def is_instructor(user):
    return (user.is_authenticated 
            and hasattr(user, "instructorprofile") 
            and not hasattr(user, "studentprofile"))

def is_student(user):
    return (user.is_authenticated 
            and hasattr(user, "studentprofile") 
            and not hasattr(user, "instructorprofile"))


@require_GET
def newCoursePage(request):
    if request.method == "GET":
        template = loader.get_template("app/new_course.html")
        return HttpResponse(template.render({}, request))
    else: 
        return HttpResponse("Method not allowed", status=405)


@csrf_exempt
@require_POST
def createCourse(request):
    user = request.user
    if not is_instructor(user):
        return HttpResponse("Unauthorized", status=401)

    name = request.POST.get("course-name")
    start_time = request.POST.get("start-time")
    end_time = request.POST.get("end-time")
    if not (name and start_time and end_time):
        return HttpResponse("Missing name or course time", status=400)

    possible_days = ["day-mon", "day-tue", "day-wed", "day-thu", "day-fri"]
    selected_days = [day for day in possible_days if request.POST.get(day)]

    if not selected_days:
        return HttpResponse("Select day(s) of week", status=400)
    
    Course.objects.create(
        name=name,
        start_time=start_time,
        end_time=end_time,
        day_mon="day-mon" in request.POST,
        day_tue="day-tue" in request.POST,
        day_wed="day-wed" in request.POST,
        day_thu="day-thu" in request.POST,
        day_fri="day-fri" in request.POST,
        instructor_id=InstructorProfile.objects.get(user_id=user.id).id
    )   

    return HttpResponse("Course created successfully", status=200)

@require_GET
def newLecturePage(request):
    if request.method == "GET":
        template = loader.get_template("app/new_lecture.html")
        return HttpResponse(template.render({}, request))
    else: 
        return HttpResponse("Method not allowed", status=405)


@csrf_exempt
@require_POST
def createLecture(request):
    user = request.user
    if not is_instructor(user):
        return HttpResponse("Unauthorized", status=401)

    course = request.POST.get("choice")
    date = request.POST.get("date")


    Lecture.objects.create(
        date=date,
        course_id=Course.objects.get(name=course).id

    )
    return HttpResponse("Lecture created", status=200)

def newQRUploadPage(request):
    if request.method == "GET":
                template = loader.get_template("app/new_qr_upload.html")
                return HttpResponse(template.render({}, request))
    else: 
        return HttpResponse("Method not allowed", status=405)


@csrf_exempt
@require_POST
def createQRCodeUpload(request):
    user = request.user
    if not is_student(user):
        return HttpResponse("Unauthorized", status=401)

    image = request.FILES.get("imageUpload")
    if image is None:
        return HttpResponse("Missing image upload", status=400)

    QRCodeUpload.objects.create(
        student_id=user.student_profile.id,
        image=image,
        uploaded_at= datetime.now(tz=CDT)
    )

    return HttpResponse("Upload created", status=200)

@require_GET
def dumpUploads(request):
    user = request.user
    if not is_instructor(user):
        return HttpResponse("Unauthorized", status=401)

    uploads = QRCodeUpload.objects.select_related("student")

    data = [
        {
            "username": u.student.username,
            "upload_time": u.uploaded_at
        }
        for u in uploads
    ]
    return JsonResponse(data, safe=False)
    