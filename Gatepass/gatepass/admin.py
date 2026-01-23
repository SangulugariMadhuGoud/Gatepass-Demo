from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db import transaction
from django.contrib import messages
from django.urls import path
from django.shortcuts import render
from django.utils.html import format_html
from .models import User, Student, Warden, Security, GatePass, ParentVerification, Notification
import tempfile
import os

# Lazy import bulk_import to avoid startup errors
StudentBulkImporter = None
GatePassBulkImporter = None

def get_bulk_importers():
    """Lazy load bulk importers"""
    global StudentBulkImporter, GatePassBulkImporter
    if StudentBulkImporter is None or GatePassBulkImporter is None:
        try:
            from .bulk_import import StudentBulkImporter as SBI, GatePassBulkImporter as GBI
            StudentBulkImporter = SBI
            GatePassBulkImporter = GBI
        except ImportError as e:
            print(f"Warning: Could not import bulk importers: {e}")
            return False
    return True


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Custom User Admin"""
    
    list_display = ('username', 'email', 'role', 'gender', 'is_approved', 'is_active', 'date_joined')
    list_filter = ('role', 'gender', 'is_approved', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'mobile_number', 'gender')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Gatepass Info', {'fields': ('role', 'is_approved')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'is_approved'),
        }),
    )


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Student Admin"""
    
    list_display = ('student_name', 'hall_ticket_no', 'room_no', 'parent_name', 'parent_mobile', 'user')
    list_filter = ('user__gender', 'user__is_approved')
    search_fields = ('student_name', 'hall_ticket_no', 'parent_name', 'parent_mobile')
    readonly_fields = ('username_format',)
    change_list_template = 'admin/gatepass/student_changelist.html'
    
    def get_urls(self):
        """Add bulk import URL"""
        urls = super().get_urls()
        custom_urls = [
            path('bulk-import/', self.admin_site.admin_view(self.bulk_import_view), name='gatepass_student_bulk_import'),
        ]
        return custom_urls + urls
    
    def changelist_view(self, request, extra_context=None):
        """Add bulk import button to changelist"""
        extra_context = extra_context or {}
        extra_context['has_bulk_import'] = True
        return super().changelist_view(request, extra_context)
    
    def bulk_import_view(self, request):
        """Handle bulk import of students"""
        try:
            # Load bulk importers
            if not get_bulk_importers():
                messages.error(request, 'Bulk import functionality is not available.')
                return render(request, 'admin/gatepass/bulk_import.html', {'title': 'Bulk Import Students'})
            
            if request.method == 'GET':
                return render(request, 'admin/gatepass/bulk_import.html', {
                    'title': 'Bulk Import Students',
                    'instruction': 'Upload an Excel file with student data.'
                })
            
            if request.method == 'POST':
                if 'file' not in request.FILES:
                    messages.error(request, 'No file uploaded. Please select an Excel or CSV file.')
                    return render(request, 'admin/gatepass/bulk_import.html', {'title': 'Bulk Import Students'})
                
                uploaded_file = request.FILES['file']
                
                # Validate file extension
                valid_extensions = ['.xlsx', '.xls', '.csv']
                file_ext = os.path.splitext(uploaded_file.name)[1].lower()
                if file_ext not in valid_extensions:
                    messages.error(request, f'Invalid file format. Accepted formats: {", ".join(valid_extensions)}')
                    return render(request, 'admin/gatepass/bulk_import.html', {'title': 'Bulk Import Students'})
                
                # Save uploaded file temporarily
                tmp_path = None
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
                        for chunk in uploaded_file.chunks():
                            tmp_file.write(chunk)
                        tmp_path = tmp_file.name
                    
                    # Import students
                    importer = StudentBulkImporter(tmp_path)
                    success = importer.import_students()
                    
                    # Display results
                    if success:
                        messages.success(
                            request,
                            f'✓ {len(importer.successes)} student(s) imported successfully!'
                        )
                        # Redirect to changelist
                        from django.http import HttpResponseRedirect
                        return HttpResponseRedirect('../')
                    else:
                        # Show results with errors
                        context = {
                            'title': 'Bulk Import Results - Students',
                            'successes': importer.successes,
                            'errors': importer.errors,
                            'total_rows': len(importer.successes) + len(importer.errors),
                            'success_count': len(importer.successes),
                            'error_count': len(importer.errors),
                            'back_url': '../'
                        }
                        return render(request, 'admin/gatepass/bulk_import_results.html', context)
                    
                except Exception as import_error:
                    messages.error(request, f'Import failed: {str(import_error)}')
                    return render(request, 'admin/gatepass/bulk_import.html', {'title': 'Bulk Import Students'})
                
                finally:
                    # Clean up temporary file
                    if tmp_path and os.path.exists(tmp_path):
                        try:
                            os.remove(tmp_path)
                        except:
                            pass
        
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return render(request, 'admin/gatepass/bulk_import.html', {'title': 'Bulk Import Students'})


@admin.register(Warden)
class WardenAdmin(admin.ModelAdmin):
    """Warden Admin"""
    
    list_display = ('name', 'department', 'user')
    search_fields = ('name', 'department')


@admin.register(Security)
class SecurityAdmin(admin.ModelAdmin):
    """Security Admin"""
    
    list_display = ('name', 'shift', 'user')
    search_fields = ('name', 'shift')


@admin.register(GatePass)
class GatePassAdmin(admin.ModelAdmin):
    """GatePass Admin"""
    
    list_display = ('student', 'outing_date', 'outing_time', 'status', 'created_at')
    list_filter = ('status', 'outing_date', 'student__user__gender')
    search_fields = ('student__student_name', 'student__hall_ticket_no')
    readonly_fields = ('created_at', 'updated_at')
    actions = ['delete_selected_safe']
    list_per_page = 50  # Limit items per page to avoid field limit issues
    list_max_show_all = 100  # Maximum number of items to show when "Show all" is clicked
    show_full_result_count = False  # Don't count all items (performance)
    change_list_template = 'admin/gatepass/gatepass_changelist.html'
    
    fieldsets = (
        ('Student Information', {
            'fields': ('student',)
        }),
        ('Outing Details', {
            'fields': ('outing_date', 'outing_time', 'expected_return_date', 'expected_return_time', 'purpose')
        }),
        ('Approval Status', {
            'fields': ('status', 'warden_approval', 'security_approval', 'warden_rejection_reason', 'parent_verification')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_urls(self):
        """Add bulk import URL"""
        urls = super().get_urls()
        custom_urls = [
            path('bulk-import/', self.admin_site.admin_view(self.bulk_import_view), name='gatepass_gatepass_bulk_import'),
        ]
        return custom_urls + urls
    
    def changelist_view(self, request, extra_context=None):
        """Add bulk import button to changelist"""
        extra_context = extra_context or {}
        extra_context['has_bulk_import'] = True
        return super().changelist_view(request, extra_context)
    
    def bulk_import_view(self, request):
        """Handle bulk import of gatepasses"""
        try:
            # Load bulk importers
            if not get_bulk_importers():
                messages.error(request, 'Bulk import functionality is not available.')
                return render(request, 'admin/gatepass/bulk_import.html', {'title': 'Bulk Import Gatepasses'})
            
            if request.method == 'GET':
                return render(request, 'admin/gatepass/bulk_import.html', {
                    'title': 'Bulk Import Gatepasses',
                    'instruction': 'Upload an Excel file with gatepass data.'
                })
            
            if request.method == 'POST':
                if 'file' not in request.FILES:
                    messages.error(request, 'No file uploaded. Please select an Excel or CSV file.')
                    return render(request, 'admin/gatepass/bulk_import.html', {'title': 'Bulk Import Gatepasses'})
                
                uploaded_file = request.FILES['file']
                
                # Validate file extension
                valid_extensions = ['.xlsx', '.xls', '.csv']
                file_ext = os.path.splitext(uploaded_file.name)[1].lower()
                if file_ext not in valid_extensions:
                    messages.error(request, f'Invalid file format. Accepted formats: {", ".join(valid_extensions)}')
                    return render(request, 'admin/gatepass/bulk_import.html', {'title': 'Bulk Import Gatepasses'})
                
                # Save uploaded file temporarily
                tmp_path = None
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
                        for chunk in uploaded_file.chunks():
                            tmp_file.write(chunk)
                        tmp_path = tmp_file.name
                    
                    # Import gatepasses
                    importer = GatePassBulkImporter(tmp_path)
                    success = importer.import_gatepasses()
                    
                    # Display results
                    if success:
                        messages.success(
                            request,
                            f'✓ {len(importer.successes)} gatepass(es) imported successfully!'
                        )
                        # Redirect to changelist
                        from django.http import HttpResponseRedirect
                        return HttpResponseRedirect('../')
                    else:
                        # Show results with errors
                        context = {
                            'title': 'Bulk Import Results - Gatepasses',
                            'successes': importer.successes,
                            'errors': importer.errors,
                            'total_rows': len(importer.successes) + len(importer.errors),
                            'success_count': len(importer.successes),
                            'error_count': len(importer.errors),
                            'back_url': '../'
                        }
                        return render(request, 'admin/gatepass/bulk_import_results.html', context)
                    
                except Exception as import_error:
                    messages.error(request, f'Import failed: {str(import_error)}')
                    return render(request, 'admin/gatepass/bulk_import.html', {'title': 'Bulk Import Gatepasses'})
                
                finally:
                    # Clean up temporary file
                    if tmp_path and os.path.exists(tmp_path):
                        try:
                            os.remove(tmp_path)
                        except:
                            pass
        
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return render(request, 'admin/gatepass/bulk_import.html', {'title': 'Bulk Import Gatepasses'})
    
    def delete_selected_safe(self, request, queryset):
        """Custom delete action that handles large querysets without hitting field limits"""
        count = queryset.count()
        if count == 0:
            self.message_user(request, 'No records selected.', messages.WARNING)
            return
        
        try:
            with transaction.atomic():
                # Delete related notifications first
                Notification.objects.filter(gatepass__in=queryset).delete()
                # Delete related parent verifications
                ParentVerification.objects.filter(gatepass__in=queryset).delete()
                # Finally delete gatepasses
                deleted_count, _ = queryset.delete()
                
            self.message_user(
                request,
                f'Successfully deleted {deleted_count} gatepass record(s) and related data.',
                messages.SUCCESS
            )
        except Exception as e:
            self.message_user(
                request,
                f'Error deleting records: {str(e)}',
                messages.ERROR
            )
    
    delete_selected_safe.short_description = "Delete selected gatepasses (handles large selections)"


@admin.register(ParentVerification)
class ParentVerificationAdmin(admin.ModelAdmin):
    """Parent Verification Admin"""
    
    list_display = ('gatepass', 'parent_mobile', 'is_verified', 'verified_at', 'created_at')
    list_filter = ('is_verified', 'created_at')
    search_fields = ('gatepass__student__student_name', 'parent_mobile')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Notification Admin"""
    
    list_display = ('user', 'gatepass', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'message')
    readonly_fields = ('created_at',)