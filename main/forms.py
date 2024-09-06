from django import forms
from django.core.validators import EmailValidator
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, HolidayAssignment, TeachingStaff, Administrator

from .models import PastPaper, RevisionMaterial
 
class PastPaperForm(forms.ModelForm):
    class Meta:
        model = PastPaper
        fields = ['title', 'file', 'year', 'term', 'grade', 'subject']
        labels={'title':'Name of Exam','grade':'Form'}

class RevisionMaterialForm(forms.ModelForm):
    class Meta:
        model = RevisionMaterial
        fields = ['title', 'file', 'year', 'term', 'grade', 'subject']
        labels={'title':'Name of Revision material','grade':'Form'}

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(validators=[EmailValidator()])
    message = forms.CharField(widget=forms.Textarea(attrs={'cols': 80, 'rows': 10}), required=True)

    def clean_message(self):
        message = self.cleaned_data['message']
        if len(message) < 10:
            raise forms.ValidationError("Message must be at least 10 characters long.")
        return message

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'user_type']

class HolidayAssignmentForm(forms.ModelForm):
    class Meta:
        model = HolidayAssignment
        fields = ['year', 'title', 'grade', 'subject', 'file']
        labels = {
            'year': 'Academic Year',
            'title': 'Name of Holiday',
            'grade': 'Form',
            'subject': 'Subject',
            'file': 'Assignment File',
            #'description': 'Description'
        }
        help_texts = {
            'year': 'Select the academic year for the assignment.',
            'title': 'Select the name of the holiday.',
            'grade': 'Select the Form this assignment is for.',
            'subject': 'Specify the subject of the assignment.',
            'file': 'Upload the assignment file (e.g., PDF, DOCX).',

        }


class CustomUserCreationForm(UserCreationForm):
    user_type = forms.ChoiceField(choices=CustomUser.USER_TYPES, required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'user_type']

class AdministratorProfileForm(forms.ModelForm):
    class Meta:
        model = Administrator
        fields = [ 'title', 'name','role','order', 'photo', 'subjects']
        labels = {
            'title': 'Title',
            'name': 'Full Name',
            'role': 'Position',
            'order': 'Staff number',
            'photo': 'Profile Photo',
            'subjects': 'Subjects'
        }
        help_texts = {
            'title': 'Enter your title(e.g, Mr).',
            'name': 'Enter your full name.',
            'role': 'Specify your position in the institution.',


            'subjects': 'List the subjects you teach.'
        }

class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = TeachingStaff
        fields = [ 'title', 'name','role','order', 'photo', 'subjects']
        labels = {
            'title': 'Title',
            'name': 'Full Name',
            'role': 'Position',
            'order': 'Staff number',
            'photo': 'Profile Photo',
            'subjects': 'Subjects'
        }
        help_texts = {
            'title': 'Enter your title(e.g, Mr).',
            'name': 'Enter your full name.',
            'role': '(OPTIONAL)',


            'subjects': 'List the subjects you teach.'
        }




# class list
from .models import Grade, Stream, Student

class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['name']

class StreamForm(forms.ModelForm):
    class Meta:
        model = Stream
        fields = ['name', 'grade']

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['admission_number', 'name', 'stream','kcpe']


from django import forms
from .models import Grade, Stream

from django import forms
from .models import Grade

class GradeSelectForm(forms.Form):
    grade = forms.ModelChoiceField(queryset=Grade.objects.all(), empty_label=None, label='Select Grade')

class StreamSelectForm(forms.ModelForm):
    class Meta:
        model = Stream
        fields = ['id', 'name']  # Adjust fields as necessary
