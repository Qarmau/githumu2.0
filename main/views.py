# Django Built-in Modules
from django.contrib import messages
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.files.storage import default_storage
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Q, Min, IntegerField
from django.db.models.functions import Cast
from django.http import HttpResponse, HttpResponseForbidden, FileResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

# Third-Party Libraries
import pandas as pd
import csv
import io
from io import BytesIO
from datetime import datetime

# ReportLab (PDF Generation)
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, PageBreak

# Project-Specific Imports
from .models import *
from .forms import (
    ContactForm,
    CustomUserCreationForm,
    HolidayAssignmentForm,
    UserProfileForm,
    TeacherProfileForm,
    AdministratorProfileForm,
    GradeSelectForm,
    StreamSelectForm,
    PastPaperForm,
    RevisionMaterialForm,
    StreamForm,
    GradeForm,
    StreamForm, 
    StudentForm

)

def download_assignment(request, assignment_id):
    assignment = get_object_or_404(HolidayAssignment, id=assignment_id)
    assignment.download_count += 1
    assignment.save()
    return FileResponse(assignment.file, as_attachment=True)

# Home page view
def home(request):
    current_time = timezone.now()
    events = Event.objects.filter(date__gte=current_time).order_by('date')[:3]
    news = News.objects.order_by('-date')[:5]
    calendar_events = CalendarEvent.objects.filter(date__gte=current_time).order_by('date')[:10]

    context = {
        'events': events,
        'news': news,
        'calendar_events': calendar_events,
    }
    return render(request, 'home.html', context)

def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'event_detail.html', {'event': event})

# About page view
def about(request):
    about_info = About.objects.first()

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            send_mail(
                f'Message from {name}',
                message,
                email,
                [about_info.email],
                fail_silently=False,
            )
            messages.success(request, 'Your message has been sent successfully!')
        else:
            messages.error(request, 'There was an error with your submission. Please check the form and try again.')
    else:
        form = ContactForm()
    return render(request, 'about.html', {'about': about_info, 'form': form})

# Administration page view
def administration(request):
    administrators = Administrator.objects.all().order_by('order')
    return render(request, 'administration.html', {'administrators': administrators})

# Teaching staff page view
def teaching_staff(request):
    staff = TeachingStaff.objects.all().order_by('order')
    return render(request, 'teaching_staff.html', {'staff': staff})

# Achievements page view
def achievements(request):
    university_admissions = Achievement.objects.all().order_by('year')
    awards = CoCurricularAward.objects.all().order_by('-year')
    return render(request, 'achievements.html', {
        'university_admissions': university_admissions,
        'awards': awards,
    })

# Academics page view
def academics(request):
    assignments = HolidayAssignment.objects.all().order_by('-date_uploaded')

    # Extract unique years
    unique_academics = []
    unique_years = set()
    for assignment in assignments:
        if assignment.year not in unique_years:
            unique_academics.append(assignment)
            unique_years.add(assignment.year)

    return render(request, 'academics.html', {'academics': unique_academics})

def likizo(request):
    assignments = HolidayAssignment.objects.all().order_by('-date_uploaded')

    # Extract unique years
    unique_academics = []
    unique_years = set()
    for assignment in assignments:
        if assignment.year not in unique_years:
            unique_academics.append(assignment)
            unique_years.add(assignment.year)

    return render(request, 'likizo.html', {'academics': unique_academics})

def keys(request):
    return render(request,'keys.html')

# Holiday assignment detail view
def holiday(request, holiday_id):
    holiday = get_object_or_404(HolidayAssignment, id=holiday_id)
    all_assignments = HolidayAssignment.objects.filter(year=holiday.year).order_by('-date_uploaded')
    unique_assignments = {assignment.title: assignment for assignment in all_assignments}
    filtered_assignments = list(unique_assignments.values())
    return render(request, 'holiday.html', {'holiday': holiday, 'assignments': filtered_assignments})

# Grades view
def grades(request, grade_id):
    selected_assignment = get_object_or_404(HolidayAssignment, id=grade_id)
    assignments = HolidayAssignment.objects.filter(title=selected_assignment.title).order_by('-date_uploaded')
    all_grades = HolidayAssignment.objects.filter(title=selected_assignment.title).values('grade').annotate(first_assignment_id=Min('id'))
    return render(request, 'grades.html', {'grades': selected_assignment, 'assignments': assignments, 'all_grades': all_grades})

# Years view
def years(request, years_id):
    year_assignment = get_object_or_404(HolidayAssignment, id=years_id)
    return render(request, 'years.html', {'years': year_assignment})

# News detail view
def news_detail(request, news_id):
    news = get_object_or_404(News, id=news_id)
    return render(request, 'news_detail.html', {'news': news})

# Assignments view
def assignments(request, assignment_id):
    assignment = get_object_or_404(HolidayAssignment, id=assignment_id)
    related_assignments = HolidayAssignment.objects.filter(
        year=assignment.year,
        grade=assignment.grade,
        title=assignment.title
    ).order_by('subject')
    return render(request, 'assignments.html', {
        'assignment': assignment,
        'related_assignments': related_assignments,
    })

# Search view
def search(request):
    query = request.GET.get('q')
    results = []
    if query:
        results = HolidayAssignment.objects.filter(
            Q(title__icontains=query) |
            Q(grade__icontains=query) |
            Q(subject__icontains=query) |
            Q(year__icontains=query) |
            Q(file__icontains=query)
        )

        # Get the list of searches from the session
        searches = request.session.get('searches', [])

        # Add the new search query to the list
        if query not in searches:
            searches.append(query)
            # Keep only the last 5 searches
            if len(searches) > 5:
                searches.pop(0)

        # Save the updated list back to the session
        request.session['searches'] = searches

    return render(request, 'search_results.html', {'results': results, 'query': query, 'searches': request.session.get('searches', [])})


# Admin dashboard view
@login_required
def admin_dashboard(request):
    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, instance=request.user)
        if request.user.user_type == 'teacher':
            profile_form = TeacherProfileForm(request.POST, request.FILES, instance=request.user.teachingstaff)
        else:
            profile_form = AdministratorProfileForm(request.POST, request.FILES, instance=request.user.administrator)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('admin_dashboard')
    else:
        user_form = UserProfileForm(instance=request.user)
        if request.user.user_type == 'teacher':
            profile_form = TeacherProfileForm(instance=request.user.teachingstaff)
        else:
            profile_form = AdministratorProfileForm(instance=request.user.administrator)
    return render(request, 'admin_dashboard.html', {'user_form': user_form, 'profile_form': profile_form})

# User registration view
def register(request):
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        user_type = request.POST.get('user_type')

        if user_type == 'administrator':
            profile_form = AdministratorProfileForm(request.POST, request.FILES)
        else:
            profile_form = TeacherProfileForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)

            # Determine if the user is a superuser and adjust `is_active`
            user.is_staff = (user_type == 'administrator')
            if user.is_superuser:
                user.is_active = True  # Superusers are active by default
            else:
                user.is_active = False  # Set other users as inactive by default

            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            # Send email to the superuser for approval if the user is not a superuser
            if not user.is_superuser:
                send_approval_notification(user)
                messages.success(request, 'Your registration is pending approval by the administrator. You will be notified when your account is activated.')
                return redirect('login')
            else:
                messages.success(request, 'Your account has been created successfully and is active.')
                return redirect('login')
    else:
        user_form = CustomUserCreationForm()

    # Initialize forms for the GET request or in case of a POST request failure
    administrator_profile_form = AdministratorProfileForm()
    teacher_profile_form = TeacherProfileForm()

    # For POST requests that fail validation, we need to return the appropriate form
    if request.method == 'POST':
        if user_type == 'administrator':
            profile_form = AdministratorProfileForm(request.POST, request.FILES)
        else:
            profile_form = TeacherProfileForm(request.POST, request.FILES)

        return render(request, 'registration.html', {
            'user_form': user_form,
            'administrator_profile_form': profile_form if user_type == 'administrator' else administrator_profile_form,
            'teacher_profile_form': profile_form if user_type != 'administrator' else teacher_profile_form
        })

    return render(request, 'registration.html', {
        'user_form': user_form,
        'administrator_profile_form': administrator_profile_form,
        'teacher_profile_form': teacher_profile_form
    })




def send_approval_notification(user):
    subject = f"Approval Request: New User Registration - {user.username}"
    message = (
        f"Dear Administrator,\n\n"
        f"A new user has recently registered on the website. "
        f"Please review the registration details to approve the account at https://githumuhigh.pythonanywhere.com/admin/\n\n"
        f"Username: {user.username}\n\n"
        f"Thank you for your prompt attention to this matter.\n\n"
        f"Best regards,\n"
        f"GHS Team"
    )
    from_email = "kamauj613@gmail.com"
    to_email = "kamaumbaya8@gmail.com"
    send_mail(subject, message, from_email, [to_email], fail_silently=False)


# User login view
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('holiday_assignment_list')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

# Holiday assignment list view
@login_required
def holiday_assignment_list(request):

    return render(request, 'holiday_assignments.html')

# Create holiday assignment view
@login_required
def holiday_assignment_create(request):
    if request.method == 'POST':
        form = HolidayAssignmentForm(request.POST, request.FILES)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.author = request.user
            assignment.save()
            response_data = {'success': True}
        else:
            response_data = {'success': False, 'errors': form.errors}
        return JsonResponse(response_data)
    else:
        form = HolidayAssignmentForm()
    return render(request, 'holiday_assignment_form.html', {'form': form})


# Delete holiday assignment view
@login_required
def holiday_assignment_delete(request, pk):
    assignment = get_object_or_404(HolidayAssignment, pk=pk)
    if request.method == 'POST':
        assignment.delete()
        return redirect('holiday_assignment_list')
    return render(request, 'holiday_assignment_delete.html', {'assignment': assignment})

# Download holiday assignment file view
@login_required
def holiday_assignment_download(request, pk):
    assignment = get_object_or_404(HolidayAssignment, pk=pk)
    response = HttpResponse(assignment.file, content_type='application/force-download')
    response['Content-Disposition'] = f'attachment; filename="{assignment.title}.{assignment.file.name.split(".")[-1]}"'
    return response

# Assignment detail view
@login_required
def assignment_detail(request, pk):
    assignment = get_object_or_404(HolidayAssignment, pk=pk)
    if request.user.user_type == 'teacher' and assignment.author != request.user:
        return HttpResponseForbidden("You are not allowed to view this assignment.")
    return render(request, 'holiday_assignment_detail.html', {'assignment': assignment})

# Logout function
@login_required
def logout_user(request):
    logout(request)
    return redirect('login')


def password_reset(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            user = form.user
            user.password_reset_token = default_token_generator.make_token(user)
            user.password_reset_token_expiration = timezone.now() + timedelta(hours=24)
            user.password_reset_token_expiration = timezone.now() + timedelta(minutes=15)
            user.save()

            # Send password reset email
            subject = 'Password Reset Request'
            message = render_to_string('password_reset_email.html', {
                'user': user,
                'token': user.password_reset_token,
                'expiration_time': user.password_reset_token_expiration,
            })
            from_email = 'your_school@example.com'
            recipient_list = [user.email]
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)

            return redirect('password_reset_done')
    else:
        form = PasswordResetForm()

    return render(request, 'password_reset.html', {'form': form})

def password_reset_done(request):
    return render(request, 'password_reset_done.html')

def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = CustomUserCreationForm(request.POST, instance=user)
            if form.is_valid():
                user = form.save(commit=False)
                user.set_password(form.cleaned_data['password1'])
                user.password_reset_token = ''
                user.password_reset_token_expiration = None
                user.is_active = True
                user.save()
                login(request, user)
                return redirect('home')
        else:
            form = CustomUserCreationForm(instance=user)
        return render(request, 'password_reset_confirm.html', {'form': form})
    else:
        return render(request, 'password_reset_confirm.html', {'form': None, 'error': 'The password reset link is invalid or has expired.'})

def download_assignment(request, assignment_id):
    assignment = get_object_or_404(HolidayAssignment, id=assignment_id)
    assignment.download_count += 1
    assignment.save()
    return FileResponse(assignment.file, as_attachment=True)




# gallery view
def gallery(request):
    gallery = Gallery.objects.all().order_by('-date_uploaded')
    categories = Gallery.CATEGORY_CHOICES
    return render(request, 'gallery.html', {'gallery': gallery, 'categories': categories})


#academic views
def past_papers(request):
    years = AcademicYear.objects.all()
    terms = Term.objects.all()
    grades = Grade.objects.all()
    subjects = Subject.objects.all()

    year = request.GET.get('year')
    term = request.GET.get('term')
    grade = request.GET.get('grade')
    subject = request.GET.get('subject')

    papers = PastPaper.objects.all()

    if year:
        papers = papers.filter(year__year=year)
    if term:
        papers = papers.filter(term__id=term)
    if grade:
        papers = papers.filter(grade__id=grade)
    if subject:
        papers = papers.filter(subject__id=subject)

    paginator = Paginator(papers, 12)  # Show 12 papers per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'years': years,
        'terms': terms,
        'grades': grades,
        'subjects': subjects,
    }

    return render(request, 'past_papers.html', context)

def revision_materials(request):
    years = AcademicYear.objects.all()
    terms = Term.objects.all()
    grades = Grade.objects.all()
    subjects = Subject.objects.all()

    year = request.GET.get('year')
    term = request.GET.get('term')
    grade = request.GET.get('grade')
    subject = request.GET.get('subject')

    materials = RevisionMaterial.objects.all()

    if year:
        materials = materials.filter(year__year=year)
    if term:
        materials = materials.filter(term__id=term)
    if grade:
        materials = materials.filter(grade__id=grade)
    if subject:
        materials = materials.filter(subject__id=subject)

    paginator = Paginator(materials, 12)  # Show 12 materials per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'years': years,
        'terms': terms,
        'grades': grades,
        'subjects': subjects,
    }

    return render(request, 'revision_materials.html', context)

#uploading exams and revision
@login_required
def upload_past_paper(request):
    if request.method == 'POST':
        form = PastPaperForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('holiday_assignment_list')
    else:
        form = PastPaperForm()
    return render(request, 'upload_past_paper.html', {'form': form})

@login_required
def upload_revision_material(request):
    if request.method == 'POST':
        form = RevisionMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('holiday_assignment_list')
    else:
        form = RevisionMaterialForm()
    return render(request, 'upload_revision_material.html', {'form': form})



#class list
@login_required
def create_grade(request):
    if request.method == 'POST':
        form = GradeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('grade_list')
    else:
        form = GradeForm()
    return render(request, 'create_grade.html', {'form': form})

@login_required
def create_stream(request, grade_id):
    grade = get_object_or_404(Grade, id=grade_id)
    if request.method == 'POST':
        form = StreamForm(request.POST)
        if form.is_valid():
            stream = form.save(commit=False)
            stream.grade = grade
            stream.save()
            return redirect('stream_list', grade_id=grade_id)  # Redirect with grade_id
    else:
        form = StreamForm()
    return render(request, 'create_stream.html', {'form': form, 'grade': grade})

@login_required
def select_grade(request):
    if request.method == 'POST':
        grade_form = GradeSelectForm(request.POST)
        if grade_form.is_valid():
            grade_id = grade_form.cleaned_data['grade'].id
            return redirect('select_stream', grade_id=grade_id)
        else:
            return render(request, 'select_grade.html', {'grade_form': grade_form, 'error': 'Invalid grade selection.'})
    else:
        grade_form = GradeSelectForm()

    return render(request, 'select_grade.html', {'grade_form': grade_form})

@login_required
def select_stream(request, grade_id):
    grade = get_object_or_404(Grade, id=grade_id)
    streams = Stream.objects.filter(grade=grade)

    if request.method == 'POST':
        stream_id = request.POST.get('stream_id')
        return redirect('upload_students', grade_id=grade_id, stream_id=stream_id)

    stream_form = StreamSelectForm()
    return render(request, 'select_stream.html', {'stream_form': stream_form, 'streams': streams, 'grade': grade})

@login_required
def upload_students(request, grade_id, stream_id):
    grade = get_object_or_404(Grade, id=grade_id)
    stream = get_object_or_404(Stream, id=stream_id)
    

    if request.method == 'POST':
        uploaded_file = request.FILES['file']
        df = pd.read_excel(uploaded_file)

        # Ensure required columns are present
        if 'admission_number' not in df.columns or 'name' not in df.columns or 'kcpe' not in df.columns:
            return render(request, 'upload_students.html', {'error': 'Required columns are missing from the uploaded file.'})

        # Process the DataFrame
        for index, row in df.iterrows():
            admission_number = row['admission_number']
            name = row['name']
            kcpe=row['kcpe']

            # Create or update the Student object
            Student.objects.update_or_create(
                admission_number=admission_number,
                defaults={'name': name, 'stream': stream,'kcpe':kcpe}
            )

        # Redirect to the student list page for the stream
        return redirect('student_list', stream_id=stream_id)

    return render(request, 'upload_students.html', {'grade': grade, 'stream': stream})

@login_required
def mini_dashboard(request):
    return render(request,'mini_dashboard.html')

@login_required
def grade_list(request):
    grades = Grade.objects.all()
    return render(request, 'grade_list.html', {'grades': grades})

@login_required
def stream_list(request, grade_id):
    grade = get_object_or_404(Grade, id=grade_id)
    streams = grade.streams.all()
    return render(request, 'stream_list.html', {'grade': grade, 'streams': streams})

@login_required
def student_list(request, stream_id):
    stream = get_object_or_404(Stream, id=stream_id)
    students = Student.objects.filter(stream=stream).annotate(
        admission_number_int=Cast('admission_number', IntegerField())
    ).order_by('admission_number_int')
    
    grade = stream.grade  # Fetch the associated grade
    return render(request, 'student_list.html', {'stream': stream, 'students': students, 'grade': grade})

#from .utils import generate_xlsx, generate_pdf

@login_required
def download_students(request, stream_id):
    stream = get_object_or_404(Stream, id=stream_id)
    grade = get_object_or_404(Grade, id=stream.grade.id)
    students = stream.students.all()  # Adjust based on your actual queryset

    if request.method == 'POST':
        format_type = request.POST.get('format')
        if format_type == 'xlsx':
            return generate_xlsx(students, stream, grade)
        elif format_type == 'pdf':
            return generate_pdf(students, stream, grade)
        else:
            return HttpResponse('Invalid format type', status=400)
    else:
        return HttpResponse('Invalid request method', status=405)


def generate_xlsx(students, stream, grade):
    output = io.BytesIO()

    # Create a Pandas Excel writer using XlsxWriter as the engine
    writer = pd.ExcelWriter(output, engine='xlsxwriter')

    # Convert the queryset to a DataFrame
    df = pd.DataFrame(list(students.values('admission_number', 'name','kcpe')))

    # Convert admission_number to numeric (integer), using 'coerce' to handle any non-numeric values
    #df['admission_number'] = pd.to_numeric(df['admission_number'], errors='coerce')

    # Sort by admission_number
    df = df.sort_values(by='admission_number')

    # Write DataFrame to Excel
    df.to_excel(writer, sheet_name='Students', index=False, header=False, startrow=3)

    # Access the XlsxWriter workbook and worksheet objects
    workbook = writer.book
    worksheet = writer.sheets['Students']

    # Add school name and class list info
    worksheet.merge_range('A1:C1', 'Githumu High School', workbook.add_format({'bold': True, 'font_size': 16, 'align': 'center', 'border': 1, 'bg_color': '#4CAF50', 'font_color': 'white'}))
    worksheet.merge_range('A2:C2', f'{grade.name} - {stream.name} Class List', workbook.add_format({'bold': True, 'font_size': 14, 'align': 'center', 'border': 1}))

    # Add column headers
    headers = ['Admission Number', 'Name','KCPE']
    for col_num, header in enumerate(headers):
        worksheet.write(3, col_num, header, workbook.add_format({'bold': True, 'bg_color': '#4CAF50', 'font_color': 'white', 'border': 1, 'align': 'center'}))

    # Format the cells in the table
    cell_format = workbook.add_format({'border': 1, 'align': 'center'})
    for row_num in range(4, len(df) + 4):
        worksheet.set_row(row_num, 20, cell_format)
    worksheet.set_column('A:A', 20)
    worksheet.set_column('B:B', 30)

    # Save the Excel file
    writer.close()
    output.seek(0)

    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{grade.name}{stream.name}_students.xlsx"'

    return response

def generate_pdf(students, stream, grade):
    # Sort students by admission number (converting to integer)
    students = students.annotate(
        admission_number_int=Cast('admission_number', IntegerField())
    ).order_by('admission_number_int')

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # School Details
    styles = getSampleStyleSheet()
    elements.append(Paragraph('Githumu High School', styles['Title']))
    elements.append(Paragraph('P.O BOX 468-01000, THIKA', styles['Normal']))
    elements.append(Paragraph('Phone: +254 701 234 5679 | Email: info@githumuhigh.edu', styles['Normal']))
    elements.append(Paragraph(f'Students in {grade.name} {stream.name} Class', styles['Title']))

    # Define the table data
    data = [['Admission Number', 'Name', 'KCPE', '              ', '                ', '                ', '                ']]  # Adjust columns as needed
    for i, student in enumerate(students):
        data.append([student.admission_number, student.name, student.kcpe, '', '', '', ''])

    # Create and style the table
    table = Table(data, repeatRows=1)  # Header repeats on new pages
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.green),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(table)

    # Add page numbers and date
    def add_page_number(canvas, doc):
        page_num = canvas.getPageNumber()
        text = f"Page {page_num}"
        canvas.drawRightString(200, 10, text)

        # Get the current date
        current_date = datetime.now().strftime("%Y-%m-%d")
        date_text = f"Downloaded on: {current_date}"
        canvas.drawRightString(doc.pagesize[0] - 40, 10, date_text)  # Position date at bottom-right corner

    # Build the document
    doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)

    # Generate the filename with grade and stream names
    filename = f"{grade.name}-{stream.name} class list.pdf"

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.write(buffer.getvalue())
    buffer.close()

    return response
