from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.home, name='home'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
    path('about/', views.about, name='about'),
    path('administration/', views.administration, name='administration'),
    path('teaching-staff/', views.teaching_staff, name='teaching_staff'),
    path('achievements/', views.achievements, name='achievements'),
    path('academics/', views.academics, name='academics'),
    path('academics/<int:holiday_id>/',views.holiday,name='holiday'),
    path('holiday/<int:grade_id>/',views.grades,name='grades'),
    path('grades/<int:assignment_id>/',views.assignments,name='assignments'),
    path('news/<int:news_id>/', views.news_detail, name='news_detail'),
    path('search/', views.search, name='search'),
    path('register/', views.register, name='register'),
    path('accounts/login/', views.login_view, name='login'),
    path('holiday-assignments/', views.holiday_assignment_list, name='holiday_assignment_list'),
    path('holiday-assignments/create/', views.holiday_assignment_create, name='holiday_assignment_create'),
    path('holiday-assignments/<int:pk>/delete/', views.holiday_assignment_delete, name='holiday_assignment_delete'),
    path('holiday-assignments/<int:pk>/download/', views.holiday_assignment_download, name='holiday_assignment_download'),
    path('accounts/logout/', views.logout_user, name='logout'),
    path('keys/',views.keys,name='keys'),
    path('password-reset/', views.password_reset, name='password_reset'),
    path('password-reset/done/', views.password_reset_done, name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('download/<int:assignment_id>/', views.download_assignment, name='download_assignment'),
    path('gallery/',views.gallery,name='gallery'),
    path('past-papers/', views.past_papers, name='past_papers'),
    path('revision-materials/', views.revision_materials, name='revision_materials'),
    path('upload_past_paper/', views.upload_past_paper, name='upload_past_paper'),
    path('upload_revision_material/', views.upload_revision_material, name='upload_revision_material'),
    path('likizo/',views.likizo,name='likizo'),



    #path('students/upload/', views.upload_students, name='upload_students'),
    path('mini_dashboard/',views.mini_dashboard,name='mini_dashboard'),
    path('grades/', views.grade_list, name='grade_list'),
    path('grades/<int:grade_id>/streams/', views.stream_list, name='stream_list'),
    path('grades/<int:grade_id>/streams/new/', views.create_stream, name='create_stream'),
    path('streams/<int:stream_id>/students/', views.student_list, name='student_list'),
    path('streams/<int:stream_id>/download/', views.download_students, name='download_students'),
    path('grades/select/', views.select_grade, name='select_grade'),
    path('grades/<int:grade_id>/streams/select/', views.select_stream, name='select_stream'),
    path('grades/<int:grade_id>/streams/<int:stream_id>/upload/', views.upload_students, name='upload_students'),
    path('students/upload/', views.upload_students, name='upload_students'),


]
