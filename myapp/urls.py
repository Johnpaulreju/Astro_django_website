from django.urls import path
from .views import (
    index_view, appointment_view, test_results_view, contact_view, login_view,dashboard_view, test_appointment_view,
    appointment_success_view,test_result_view,get_appointment,upload_lab_report, admin_dashbaord_view,admin_appointment_view,contact_success_view,register,logout_view
)

urlpatterns = [
    path('', index_view, name='home'),  # ✅ Corrected from views.index to index_view
    path('appointment/', appointment_view, name='appointment'),
    path('appointment/success/', appointment_success_view, name='appointment_success'),
    path('test-results/', test_results_view, name='test-results'),
    # path('test-results/after-login/', test_results_view_after_login, name='test-results-after-login'),
    path('contact/', contact_view, name='contact'),
    path('contact/success/', contact_success_view, name='contact_success'),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('appointment/<str:unique_id>/', test_appointment_view, name='userappointment'),
    path('dashboard/<str:unique_id>/', dashboard_view, name='dashboard'),
    path('testresult/<str:unique_id>/', test_result_view, name='testresult'),
    path('Dashboard/<str:unique_id>/', admin_dashbaord_view, name='admin_dashboard'),
    path('userappointment/<str:unique_id>/', admin_appointment_view, name='admin_appointment'),
    # path('admin-appointments/<str:unique_id>/', admin_appointment_view, name='admin_appointments'),
    path('get-appointment/<int:appointment_id>/', get_appointment, name='get_appointment'),
    path('upload_lab_report/<int:appointment_id>/', upload_lab_report, name='upload_lab_report'),
]