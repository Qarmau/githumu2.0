from .models import *
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
import csv
from django.utils import timezone

 
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date')
    search_fields = ('title', 'description')


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'date')
    search_fields = ('title', 'content')

@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date')
    search_fields = ('title',)

@admin.register(About)
class AboutAdmin(admin.ModelAdmin):
    pass

@admin.register(Administrator)
class AdministratorAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'order')
    list_editable = ('order',)

@admin.register(TeachingStaff)
class TeachingStaffAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'role', 'subjects', 'order')
    list_editable = ('order',)

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('year', 'university_admission_rate')

@admin.register(CoCurricularAward)
class CoCurricularAwardAdmin(admin.ModelAdmin):
    list_display = ('title', 'year')

@admin.register(HolidayAssignment)
class HolidayAssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'year', 'grade', 'subject','download_count', 'author', 'date_uploaded')
    list_filter = ('year', 'grade', 'subject')
    search_fields = ('title', 'author__username')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export-assignments/', self.export_assignments, name='main_holidayassignment_export'),
        ]
        return custom_urls + urls

    def export_assignments(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="assignments_export_{timezone.now().strftime("%Y-%m-%d")}.csv"'

        writer = csv.writer(response)
        writer.writerow(['Title', 'Year', 'Grade', 'Subject', 'Author', 'Date Uploaded', 'Downloads'])

        assignments = HolidayAssignment.objects.all().order_by('-date_uploaded')
        for assignment in assignments:
            writer.writerow([
                assignment.title,
                assignment.year,
                assignment.grade,
                assignment.subject,
                assignment.author.username,
                assignment.date_uploaded.strftime("%Y-%m-%d %H:%M:%S"),
                assignment.download_count
            ])

        return response

@admin.register(BackgroundImage)
class BackgroundImageAdmin(admin.ModelAdmin):
    list_display = ('image', 'order')
    list_editable = ('order',)

@admin.action(description='Activate selected users')
def activate_users(modeladmin, request, queryset):
    queryset.update(is_active=True)

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email','is_active','user_type', 'date_joined', 'is_staff')
    actions = [activate_users]
    list_filter = ('user_type', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('User Type', {'fields': ('user_type',)}),
    )

#admin.site.register(CustomUser, CustomUserAdmin)


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(RevisionMaterial)
admin.site.register(PastPaper)
admin.site.register(AcademicYear)
admin.site.register(Term)
admin.site.register(Grade)
admin.site.register(Subject)


#gallery
@admin.register(Gallery)
class BackgroundImageAdmin(admin.ModelAdmin):
    list_display = ('image', 'caption')




@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('admission_number','name','stream','kcpe')


@admin.register(Stream)
class StreamAdmin(admin.ModelAdmin):
    list_display = ('name','grade')