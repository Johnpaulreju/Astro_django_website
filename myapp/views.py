from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import TestBooking, ContactMessage , UserProfile # Ensure this matches your model name
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout , update_session_auth_hash
from .forms import RegisterForm , LoginForm 
from django.utils.timezone import now
from django.http import JsonResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site



def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            new_password = request.POST["password"]
            confirm_password = request.POST["confirm_password"]

            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Password reset successfully. You can now login.")
                return redirect("login")
            else:
                messages.error(request, "Passwords do not match.")

        return render(request, "reset_password.html")
    else:
        messages.error(request, "Invalid or expired reset link.")
        return redirect("forgot_password")
def forgot_password(request):
    if request.method == "POST":
        email = request.POST["email"]
        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            domain = get_current_site(request).domain
            reset_link = f"http://{domain}/reset-password/{uid}/{token}/"

            email_subject = "Password Reset Request"
            email_body = render_to_string("reset_email.html", {"reset_link": reset_link, "user": user})

            send_mail(email_subject, email_body, "admin@yourwebsite.com", [email])

            messages.success(request, "A password reset link has been sent to your email.")
        except User.DoesNotExist:
            messages.error(request, "Email not found.")
    return render(request, "forget_password.html")


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Hash password before saving
            user.save()

            # ✅ Create UserProfile and store additional details
            UserProfile.objects.create(
                user=user,
                phone=form.cleaned_data.get('phone'),
                address=form.cleaned_data.get('address')
            )

            # ✅ Store message in session instead of messages framework
            request.session['registration_success'] = "Registration successful! Please log in."
            return redirect('login')  # ✅ Redirect to login after successful registration

    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})


def login_view(request):
    form = LoginForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            remember_me = request.POST.get("remember_me") == "true"


            # ✅ Convert email to username before authentication
            try:
                user = User.objects.get(email=email)
                user = authenticate(request, username=user.username, password=password)
            except User.DoesNotExist:
                user = None

            if user is not None:
                login(request, user)
                messages.success(request, "Login successful!")
                if remember_me:
                    request.session.set_expiry(60 * 60 * 24 * 30)  # 30 days
                else:
                    request.session.set_expiry(0)

                # ✅ Fetch the user's UUID
                user_profile = UserProfile.objects.get(user=user)
                user_uuid = user_profile.unique_id  # 🔥 Get the auto-generated user_id
                isAdmin = user_profile.is_admin
                if isAdmin:
                    return redirect(f"/Dashboard/{user_uuid}/")
                else:
                    return redirect(f"/dashboard/{user_uuid}/")
            else:
                messages.error(request, "Invalid credentials. Please try again.")

        else:
            print(form.errors)  # Show form validation errors

    return render(request, "login.html", {"form": form})

def dashboard_view(request, unique_id):
    try:
        # ✅ Query using `unique_id` instead of `user_id`
        user_profile = UserProfile.objects.get(unique_id=unique_id)
    except UserProfile.DoesNotExist:
        return render(request, "404.html", {"message": "User not found"})

    return render(request, "dashboard.html", {"user_profile": user_profile, "unique_id": unique_id})

def admin_dashbaord_view(request, unique_id):
    try:
        # ✅ Query using `unique_id` instead of `user_id`
        user_profile = UserProfile.objects.get(unique_id=unique_id)
    except UserProfile.DoesNotExist:
        return render(request, "404.html", {"message": "User not found"})

    return render(request, "admindashbaord.html", {"user_profile": user_profile, "unique_id": unique_id})

# def admin_appointment_view(request, unique_id):
#     try:
#         # ✅ Query using `unique_id` instead of `user_id`
#         user_profile = UserProfile.objects.get(unique_id=unique_id)
#     except UserProfile.DoesNotExist:
#         return render(request, "404.html", {"message": "User not found"})

#     return render(request, "checkup.html", {"user_profile": user_profile, "unique_id": unique_id})

def admin_appointment_view(request, unique_id):
    try:
        user_profile = UserProfile.objects.get(unique_id=unique_id)
    except UserProfile.DoesNotExist:
        return render(request, "404.html", {"message": "User not found"})

    # Get filter parameters from request
    search_name = request.GET.get("name", "").strip()
    start_date = request.GET.get("start_date", "")
    end_date = request.GET.get("end_date", "")
    test_types = request.GET.getlist("tests")

    # Start filtering
    queryset = TestBooking.objects.all()

    if search_name:
        queryset = queryset.filter(name__icontains=search_name)

    if start_date and end_date:
        queryset = queryset.filter(date__range=[start_date, end_date])
    else:
        queryset = queryset.filter(date=now().date())

    if test_types:
        queryset = queryset.filter(test_type__in=test_types)

    print(f"Filtered Appointments: {queryset}")  # Debugging line

    return render(request, "checkup.html", {
        "user_profile": user_profile,
        "unique_id": unique_id,
        "todays_appointments": queryset
    })



def get_appointment(request, appointment_id):
    appointment = get_object_or_404(TestBooking, id=appointment_id)
    data = {
        "name": appointment.name,
        "date": appointment.date.strftime("%Y-%m-%d"),
        "hour": appointment.hour,
        "test_type": appointment.test_type,
        "total_price": appointment.total_price,
        "stage": appointment.stage,
        "labreport": appointment.labreport.url if appointment.labreport else None
    }
    return JsonResponse(data)

@csrf_exempt
def upload_lab_report(request, appointment_id):
    if request.method == "POST":
        try:
            appointment = TestBooking.objects.get(id=appointment_id)
            stage = request.POST.get("stage")

            # Update the stage
            if stage:
                appointment.stage = stage

            # Handle file upload (optional)
            if 'labreport' in request.FILES:
                appointment.labreport = request.FILES['labreport']

            appointment.save()

            return JsonResponse({"success": True, "message": "Appointment updated successfully."})

        except TestBooking.DoesNotExist:
            return JsonResponse({"success": False, "message": "Appointment not found."}, status=404)

    return JsonResponse({"success": False, "message": "Invalid request."}, status=400)

def test_appointment_view(request, unique_id):
    try:
        # ✅ Get user profile using `unique_id`
        user_profile = UserProfile.objects.get(unique_id=unique_id)
        username = user_profile.user.username  # Extract the username

        # ✅ Define available tests
        tests = [
            {"name": "LDH", "price": 250},
            {"name": "BLOOD R/E (HB, TC, DC, ESR - Each Test)", "price": 150},
            {"name": "CBC", "price": 180},
            {"name": "PLATELETS COUNT", "price": 200},
            {"name": "VDRL (Rapid Test)", "price": 200},
            {"name": "HBs Ag (Rapid Test)", "price": 300},
            {"name": "HIV-1&2 (Rapid Test)", "price": 350},
            {"name": "WIDAL (Tube Test)", "price": 400},
            {"name": "Blood Group & RH", "price": 100},
            {"name": "Serum Calcium", "price": 100},
            {"name": "Renal Function Tests (RFT)", "price": 270},
            {"name": "ECG", "price": 150},
            {"name": "Serum Creatinine", "price": 100},
            {"name": "Liver Function Tests (LFT)", "price": 380},
            {"name": "X-Ray (Chest)", "price": 170},
            {"name": "Dental X-Ray", "price": 100},
            {"name": "Vitamin D3", "price": 950},
            {"name": "Blood C/S", "price": 500},
        ]

        # ✅ Fetch today's and upcoming test appointments
        today = now().date()
        today_appointments = TestBooking.objects.filter(
            date=today, booked_by=username
        ).order_by('hour')

        upcoming_appointments = TestBooking.objects.filter(
            date__gt=today, booked_by=username
        ).order_by('date')

        # ✅ Calculate test count for each appointment
        for appointment in today_appointments:
            appointment.test_count = len(appointment.test_type.split(',')) if appointment.test_type else 0

        for appointment in upcoming_appointments:
            appointment.test_count = len(appointment.test_type.split(',')) if appointment.test_type else 0

        if request.method == 'POST':
            # ✅ Retrieve form data
            name = request.POST.get('name')
            date = request.POST.get('date')
            hour = request.POST.get('hour')
            selected_tests = request.POST.getlist('tests[]')

            # ✅ Validate form data
            if not name or not date or not hour or not selected_tests:
                return render(request, 'appointment.html', {
                    'error': 'All fields are required.', 
                    'tests': tests,
                    'today_appointments': today_appointments,
                    'upcoming_appointments': upcoming_appointments,
                    'user_profile': user_profile,
                    'unique_id': unique_id
                })

            # ✅ Calculate total price
            total_price = sum(int(price) for price in selected_tests)
            today = now().date()

            # ✅ Convert selected tests into a string
            test_names = ", ".join([test['name'] for test in tests if str(test['price']) in selected_tests])

            # ✅ Save the appointment in the database
            TestBooking.objects.create(
                name=name,
                date=date,
                test_type=test_names,  
                hour=hour,
                total_price=total_price,
                booked_by=user_profile.user.username,
                booked_on=today,
                stage='upcoming'
            )

            return redirect(f'/appointment/{unique_id}/')

    except UserProfile.DoesNotExist:
        return render(request, "404.html", {"message": "User not found"})

    # ✅ Debugging: Check if appointments exist
    # print(f"Today Appointments: {today_appointments}")
    # print(f"Upcoming Appointments: {upcoming_appointments}")

    return render(request, 'userappointment.html', {
        'tests': tests,
        'today_appointments': today_appointments,
        'upcoming_appointments': upcoming_appointments,
        'user_profile': user_profile,
        'unique_id': unique_id
    })




def test_result_view(request, unique_id):
    try:
        # ✅ Get the user's profile based on `unique_id`
        user_profile = UserProfile.objects.get(unique_id=unique_id)
        username = user_profile.user.username  # Extract the username
    except UserProfile.DoesNotExist:
        return render(request, "404.html", {"message": "User not found"})

    # ✅ Fetch test bookings filtered by `booked_by=username` & `labreport` is not empty
    test_results = TestBooking.objects.filter(booked_by=username).exclude(labreport="")

    return render(request, "usertestresult.html", {
        "user_profile": user_profile,
        "unique_id": unique_id,
        "test_results": test_results
    })



def logout_view(request):
    logout(request)
    return redirect("login") 

def index_view(request):
    return render(request, 'index.html')

def appointment_view(request):
    # List of tests with their prices
    return render(request, 'login.html')

def appointment_success_view(request):
    return render(request, 'appointment_success.html')

def test_results_view(request):
    return render(request, 'test-results.html')

# def test_results_view_after_login(request):
#     return render(request, 'testresult.html')

def contact_view(request):
    if request.method == 'POST':
        # Retrieve form data
        name = request.POST.get('name')
        email = request.POST.get('email')
        message_text = request.POST.get('message')

        # Validate input
        if not name or not email or not message_text:
            messages.error(request, "All fields are required.")
            return render(request, 'contact.html')

        # Save the message in the database
        ContactMessage.objects.create(
            name=name,
            email=email,
            message=message_text
        )

        # Redirect to success page
        return redirect('contact_success')

    return render(request, 'contact.html')

def contact_success_view(request):
    return render(request, 'contact_success.html')



def index(request):
    return render(request, 'index.html')




def profile_view(request, unique_id):
    user_profile = UserProfile.objects.get(unique_id=unique_id)
    user = user_profile.user

    if request.method == "POST":
        if "update_profile" in request.POST:
            user.email = request.POST["email"]
            user_profile.phone_number = request.POST["phone"]
            user.save()
            user_profile.save()
            messages.success(request, "Profile updated successfully!")

        elif "change_password" in request.POST:
            current_password = request.POST["current_password"]
            new_password = request.POST["new_password"]

            if authenticate(username=user.username, password=current_password):
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)  # Keep the user logged in
                messages.success(request, "Password changed successfully!")
            else:
                messages.error(request, "Current password is incorrect.")

        
    return render(request, "profile.html", { "unique_id": unique_id,"user_profile": user_profile})