from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import User, Student, GatePass, ParentVerification
from .password_validation import validate_password_strength
from django.utils import timezone
from datetime import datetime, date


class StudentRegistrationForm(forms.ModelForm):
    """Student registration form"""

    password1 = forms.CharField(
        label='Password',
        help_text='Password must contain at least 5 alphabet characters, 5 numbers, and one special character.',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password',
            'autocomplete': 'new-password',
        })
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Re-enter password',
            'autocomplete': 'new-password',
        })
    )
    # Email and student mobile are optional for students (see README)
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'name@example.com',
            'autocomplete': 'email',
        })
    )
    mobile_number = forms.CharField(
        required=False,
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '10-digit mobile',
            'autocomplete': 'tel',
        })
    )
    gender = forms.ChoiceField(
        required=True,
        choices=[('M', 'Male'), ('F', 'Female')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    # Photo is optional at registration time; can be updated later
    photo = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'id': 'photo-upload',
            'capture': 'camera'
        }),
        help_text='Capture or upload your photo for verification (optional at registration)'
    )

    class Meta:
        model = Student
        fields = [
            'hall_ticket_no', 'student_name', 'room_no',
            'parent_name', 'parent_mobile', 'photo'
        ]
        widgets = {
            'hall_ticket_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 22D01A6607'}),
            'student_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full name'}),
            'room_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Room number'}),
            'parent_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Parent/Guardian name'}),
            'parent_mobile': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '10-digit parent mobile'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")

        return cleaned_data

    def clean_hall_ticket_no(self):
        hall_ticket_no = self.cleaned_data.get('hall_ticket_no')
        if Student.objects.filter(hall_ticket_no=hall_ticket_no).exists():
            raise ValidationError("Student with this hall ticket number already exists")
        return hall_ticket_no
    
    def clean_parent_mobile(self):
        parent_mobile = self.cleaned_data.get('parent_mobile')
        if Student.objects.filter(parent_mobile=parent_mobile).exists():
            raise ValidationError("Parent mobile number already exists")
        return parent_mobile
    
    def clean_mobile_number(self):
        mobile_number = self.cleaned_data.get('mobile_number')
        if mobile_number and User.objects.filter(mobile_number=mobile_number).exists():
            raise ValidationError("Mobile number already exists")
        return mobile_number

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if password1:
            validate_password_strength(password1)
        return password1


class WardenRegistrationForm(forms.ModelForm):
    """Warden registration form"""

    password1 = forms.CharField(
        label='Password',
        help_text='Password must contain at least 5 alphabet characters, 5 numbers, and one special character.',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password',
            'autocomplete': 'new-password',
        })
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Re-enter password',
            'autocomplete': 'new-password',
        })
    )
    gender = forms.ChoiceField(
        required=True,
        choices=[('M', 'Male'), ('F', 'Female')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'mobile_number', 'gender', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose a username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '10-digit mobile'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")

        return cleaned_data

    def clean_mobile_number(self):
        mobile_number = self.cleaned_data.get('mobile_number')
        if mobile_number and User.objects.filter(mobile_number=mobile_number).exists():
            raise ValidationError("Mobile number already exists")
        return mobile_number

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if password1:
            validate_password_strength(password1)
        return password1


class SecurityRegistrationForm(forms.ModelForm):
    """Security registration form"""
    shift = forms.ChoiceField(
        label='Shift',
        choices=[('', 'Select Shift'), ('Morning','Morning'),('Night','Night')],
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    password1 = forms.CharField(
        label='Password',
        help_text='Password must contain at least 5 alphabet characters, 5 numbers, and one special character.',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password',
            'autocomplete': 'new-password',
        })
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Re-enter password',
            'autocomplete': 'new-password',
        })
    )
    gender = forms.ChoiceField(
        required=True,
        choices=[('M', 'Male'), ('F', 'Female')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    class Meta:
        model = User
        fields = ['username', 'email', 'mobile_number', 'first_name', 'last_name', 'shift']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose a username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '10-digit mobile'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
        }
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return cleaned_data
    def clean_mobile_number(self):
        mobile_number = self.cleaned_data.get('mobile_number')
        if mobile_number and User.objects.filter(mobile_number=mobile_number).exists():
            raise ValidationError("Mobile number already exists")
        return mobile_number

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if password1:
            validate_password_strength(password1)
        return password1


class GatePassRequestForm(forms.ModelForm):
    """Gate pass request form"""
    
    outing_hour = forms.ChoiceField(choices=[(h, f'{h:02d}') for h in range(1, 13)], widget=forms.Select(attrs={'class': 'form-select'}))
    outing_minute = forms.ChoiceField(choices=[(m, f'{m:02d}') for m in range(0, 60, 5)], widget=forms.Select(attrs={'class': 'form-select'}))
    outing_ampm = forms.ChoiceField(choices=[('AM', 'AM'), ('PM', 'PM')], widget=forms.Select(attrs={'class': 'form-select'}))
    
    expected_return_hour = forms.ChoiceField(choices=[(h, f'{h:02d}') for h in range(1, 13)], widget=forms.Select(attrs={'class': 'form-select'}))
    expected_return_minute = forms.ChoiceField(choices=[(m, f'{m:02d}') for m in range(0, 60, 5)], widget=forms.Select(attrs={'class': 'form-select'}))
    expected_return_ampm = forms.ChoiceField(choices=[('AM', 'AM'), ('PM', 'PM')], widget=forms.Select(attrs={'class': 'form-select'}))

    photo = forms.ImageField(
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'id': 'photo-upload',
            'capture': 'camera'
        }),
        help_text='Capture or upload your photo for gatepass verification'
    )
    
    class Meta:
        model = GatePass
        fields = ['outing_date', 'expected_return_date', 'purpose', 'photo']
        widgets = {
            'outing_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expected_return_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'purpose': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        outing_date = cleaned_data.get('outing_date')
        expected_return_date = cleaned_data.get('expected_return_date')
        outing_time = cleaned_data.get('outing_time')
        expected_return_time = cleaned_data.get('expected_return_time')
        
        if outing_date and expected_return_date:
            if outing_date > expected_return_date:
                raise ValidationError("Expected return date cannot be before outing date")
            
            if outing_date == expected_return_date and outing_time and expected_return_time:
                if outing_time >= expected_return_time:
                    raise ValidationError("Expected return time must be after outing time")
        
        # Check if outing date is not in the past
        if outing_date and outing_date < date.today():
            raise ValidationError("Outing date cannot be in the past")
        
        return cleaned_data


class WardenApprovalForm(forms.Form):
    """Warden approval form"""
    
    APPROVAL_CHOICES = [
        ('approve', 'Approve'),
        ('reject', 'Reject'),
    ]
    
    action = forms.ChoiceField(
        choices=APPROVAL_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    parent_verification = forms.BooleanField(
        required=False,
        label='Parent verification completed',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    rejection_reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Reason for rejection...'}),
        label='Rejection Reason'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        rejection_reason = cleaned_data.get('rejection_reason')
        
        if action == 'reject' and not rejection_reason:
            raise ValidationError("Rejection reason is required when rejecting a request")
        
        return cleaned_data


class ParentVerificationForm(forms.ModelForm):
    """Parent verification form"""
    
    class Meta:
        model = ParentVerification
        fields = ['verification_code']
        widgets = {
            'verification_code': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 6})
        }
    
    def clean_verification_code(self):
        verification_code = self.cleaned_data.get('verification_code')
        if len(verification_code) != 6 or not verification_code.isdigit():
            raise ValidationError("Verification code must be 6 digits")
        return verification_code


class SecurityReturnForm(forms.ModelForm):
    """Security return verification form - time is captured automatically"""

    class Meta:
        model = GatePass
        fields = ['return_notes']
        widgets = {
            'return_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Any additional notes about the return...'}),
        }



class WardenDateFilterForm(forms.Form):
    """Warden date filter form"""
    
    from_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='From Date'
    )
    to_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='To Date'
    )
    status_filter = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'All Status'),
            ('pending', 'Pending'),
            ('warden_approved', 'Warden Approved'),
            ('security_approved', 'Students Out'),
            ('returned', 'Returned'),
            ('warden_rejected', 'Rejected'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Status Filter'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        from_date = cleaned_data.get('from_date')
        to_date = cleaned_data.get('to_date')
        
        if from_date and to_date and from_date > to_date:
            raise ValidationError("From date cannot be after to date")
        
        return cleaned_data


class ForgotPasswordForm(forms.Form):
    """Forgot Password form"""
    username = forms.CharField(
        label='Username',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username',
        })
    )
    new_password1 = forms.CharField(
        label='New Password',
        help_text='Password must contain at least 5 alphabet characters, 5 numbers, and one special character.',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password',
            'autocomplete': 'new-password',
        })
    )
    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Re-enter new password',
            'autocomplete': 'new-password',
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')

        if new_password1 and new_password2 and new_password1 != new_password2:
            raise ValidationError("Passwords don't match")

        return cleaned_data

    def clean_new_password1(self):
        new_password1 = self.cleaned_data.get('new_password1')
        if new_password1:
            validate_password_strength(new_password1)
        return new_password1
