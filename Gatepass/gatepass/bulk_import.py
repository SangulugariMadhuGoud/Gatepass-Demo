"""
Bulk import functionality for Students and Gatepasses
Handles Excel/CSV file imports with proper error handling and database management
"""
import pandas as pd
import time
from django.db import transaction, DatabaseError, connections
from .models import User, Student, GatePass


class BulkImportError(Exception):
    """Custom exception for bulk import errors"""
    pass


def execute_with_retry(func, max_retries=10, initial_delay=1.0):
    """
    Execute function with exponential backoff retry on database lock
    
    Args:
        func: Function to execute
        max_retries: Maximum number of retries
        initial_delay: Initial delay in seconds
    
    Returns:
        Result of function execution
    
    Raises:
        DatabaseError: If all retries are exhausted
    """
    delay = initial_delay
    last_error = None
    
    for attempt in range(max_retries):
        try:
            return func()
        except DatabaseError as e:
            error_msg = str(e).lower()
            if 'database is locked' in error_msg or 'disk i/o error' in error_msg:
                last_error = e
                if attempt < max_retries - 1:
                    print(f"Database locked (attempt {attempt + 1}/{max_retries}), retrying in {delay}s...")
                    time.sleep(delay)
                    delay = min(delay * 2, 10)  # Cap exponential backoff at 10 seconds
                    continue
            raise
    
    if last_error:
        raise last_error


class StudentBulkImporter:
    """Handle bulk import of students from Excel/CSV file"""
    
    def __init__(self, file_path):
        """
        Initialize the importer
        
        Args:
            file_path: Path to Excel or CSV file
        """
        self.file_path = file_path
        self.errors = []
        self.successes = []
        self.df = None
        
    def load_file(self):
        """Load Excel or CSV file"""
        try:
            if self.file_path.endswith('.csv'):
                self.df = pd.read_csv(self.file_path)
            else:
                self.df = pd.read_excel(self.file_path)
            # Normalize column names: strip whitespace and match case-insensitively
            self.df.columns = [str(c).strip() for c in self.df.columns]
            return True
        except Exception as e:
            self.errors.append(f"Error loading file: {str(e)}")
            return False

    def validate_data(self):
        """Validate required columns exist (case-insensitive, flexible spacing)"""
        required_columns = [
            'Student Name', 'Hall Ticket No', 'Room No',
            'Gender', 'Email', 'Mobile', 'Parent Name', 'Parent Mobile'
        ]
        # Build normalized lookup: standard name -> actual column name in file (case-insensitive)
        self._col_map = {}
        df_cols_upper = {str(c).strip().upper().replace(' ', ''): c for c in self.df.columns}
        required_norm = {c.upper().replace(' ', ''): c for c in required_columns}
        for norm, display_name in required_norm.items():
            self._col_map[display_name] = df_cols_upper.get(norm)  # None if column missing
        missing = [display_name for display_name, actual in self._col_map.items() if actual is None]
        # Email is optional for bulk import (can be empty)
        if 'Email' in missing:
            missing.remove('Email')
        if missing:
            self.errors.append(f"Missing required columns: {', '.join(missing)}")
            return False
        return True
    
    def import_students(self):
        """Import students from dataframe with batch processing"""
        if not self.load_file():
            return False
        
        if not self.validate_data():
            return False
        
        batch_size = 5  # Process 5 rows at a time to avoid database locks
        total_rows = len(self.df)
        
        # Process data in batches
        for batch_start in range(0, total_rows, batch_size):
            batch_end = min(batch_start + batch_size, total_rows)
            batch_df = self.df.iloc[batch_start:batch_end]
            
            def process_batch():
                """Process a single batch of rows"""
                with transaction.atomic():
                    for idx, row in batch_df.iterrows():
                        try:
                            def get_col(name):
                                """Get value from row using column map (actual header name in file)."""
                                actual = getattr(self, '_col_map', {}).get(name)
                                if actual is None and name == 'Email':
                                    return ''
                                if actual is None:
                                    return ''
                                val = row.get(actual)
                                return '' if pd.isna(val) else str(val).strip()
                            
                            student_name = get_col('Student Name')
                            hall_ticket_no = get_col('Hall Ticket No')
                            room_no = get_col('Room No')
                            gender = get_col('Gender').upper()
                            email = get_col('Email')
                            mobile_number = get_col('Mobile')
                            parent_name = get_col('Parent Name')
                            parent_mobile = get_col('Parent Mobile')
                            
                            # Approved column (optional)
                            is_approved = True
                            for col in self.df.columns:
                                if str(col).strip().upper() == 'APPROVED':
                                    v = row.get(col)
                                    if pd.notna(v):
                                        approved_val = str(v).strip().lower()
                                        is_approved = approved_val in ['yes', 'true', '1', 'y']
                                    break
                            
                            # Validate required fields (email is optional)
                            if not all([student_name, hall_ticket_no, room_no, parent_name,
                                       parent_mobile, mobile_number, gender]):
                                self.errors.append(f"Row {idx + 2}: Missing required fields (Student Name, Hall Ticket No, Room No, Gender, Mobile, Parent Name, Parent Mobile)")
                                continue
                            
                            # Validate mobile numbers - handle Excel float format (e.g., 9391811184.0)
                            mobile_str = str(mobile_number).split('.')[0].strip()
                            parent_mobile_str = str(parent_mobile).split('.')[0].strip()
                            
                            if not (mobile_str.isdigit() and len(mobile_str) == 10):
                                self.errors.append(
                                    f"Row {idx + 2}: Invalid student mobile (must be 10 digits), got '{mobile_number}'"
                                )
                                continue
                            
                            if not (parent_mobile_str.isdigit() and len(parent_mobile_str) == 10):
                                self.errors.append(
                                    f"Row {idx + 2}: Invalid parent mobile (must be 10 digits), got '{parent_mobile}'"
                                )
                                continue
                            
                            mobile_number = mobile_str
                            parent_mobile = parent_mobile_str
                            
                            # Validate gender
                            gender_lower = gender.lower()
                            if gender_lower in ['male', 'm']:
                                gender = 'M'
                            elif gender_lower in ['female', 'f']:
                                gender = 'F'
                            else:
                                self.errors.append(
                                    f"Row {idx + 2}: Invalid gender '{gender}' (must be Male/Female or M/F)"
                                )
                                continue
                            
                            # Email: optional; validate format only if provided
                            if email and ('@' not in email or '.' not in email):
                                self.errors.append(f"Row {idx + 2}: Invalid email format")
                                continue
                            email = email or None
                            
                            # Generate username from name and hall ticket
                            username = f"{student_name.replace(' ', '')}@{hall_ticket_no[-4:]}"
                            
                            if Student.objects.filter(hall_ticket_no=hall_ticket_no).exists():
                                self.errors.append(f"Row {idx + 2}: Student with hall ticket {hall_ticket_no} already exists")
                                continue
                            
                            if User.objects.filter(username=username).exists():
                                self.errors.append(f"Row {idx + 2}: Username {username} already exists")
                                continue
                            
                            # Create user account (email can be None)
                            user = User.objects.create_user(
                                username=username,
                                email=email,
                                password=f"{student_name}@2024",
                                role='student',
                                mobile_number=mobile_number,
                                gender=gender,
                                is_approved=is_approved
                            )
                            
                            # Create student profile
                            Student.objects.create(
                                user=user,
                                hall_ticket_no=hall_ticket_no,
                                student_name=student_name,
                                room_no=room_no,
                                parent_name=parent_name,
                                parent_mobile=parent_mobile
                            )
                            
                            # Record success
                            self.successes.append({
                                'row': idx + 2,
                                'username': username,
                                'student_name': student_name,
                                'hall_ticket_no': hall_ticket_no,
                                'approved': 'Yes' if is_approved else 'No'
                            })
                            
                        except Exception as e:
                            self.errors.append(f"Row {idx + 2}: {str(e)}")
                            # Continue processing other rows instead of stopping
                            continue
            
            # Execute batch with retry logic
            try:
                execute_with_retry(process_batch, max_retries=10, initial_delay=1.0)
            except Exception as e:
                self.errors.append(f"Database error at rows {batch_start + 2}-{batch_end + 1}: {str(e)}")
                return False
            finally:
                # Close the database connection after each batch
                connections.close_all()
        
        return len(self.errors) == 0


class GatePassBulkImporter:
    """Handle bulk import of gatepasses from Excel/CSV file"""
    
    def __init__(self, file_path):
        """
        Initialize the importer
        
        Args:
            file_path: Path to Excel or CSV file
        """
        self.file_path = file_path
        self.errors = []
        self.successes = []
        self.df = None
        
    def load_file(self):
        """Load Excel or CSV file"""
        try:
            if self.file_path.endswith('.csv'):
                self.df = pd.read_csv(self.file_path)
            else:
                self.df = pd.read_excel(self.file_path)
            return True
        except Exception as e:
            self.errors.append(f"Error loading file: {str(e)}")
            return False
    
    def validate_data(self):
        """Validate required columns exist - support both Excel and code column names"""
        # Accept both Excel format (with spaces) and code format (snake_case)
        required_columns = [
            'hall_ticket_no', 'outing_date', 'outing_time',
            'expected_return_date', 'expected_return_time', 'purpose', 'status'
        ]
        
        # Also accept Excel format with spaces/title case
        excel_columns = [
            'Hall Ticket No', 'Outing Date', 'Outing Time',
            'Expected Return Date', 'Expected Return Time', 'Purpose', 'Status'
        ]
        
        # Check if using code format or Excel format
        has_code_format = all(col in self.df.columns for col in required_columns)
        has_excel_format = all(col in self.df.columns for col in excel_columns)
        
        if not (has_code_format or has_excel_format):
            missing_code = [col for col in required_columns if col not in self.df.columns]
            missing_excel = [col for col in excel_columns if col not in self.df.columns]
            self.errors.append(
                f"Missing required columns. Expected either:\n"
                f"  Code format: {required_columns}\n"
                f"  Excel format: {excel_columns}"
            )
            return False
        
        # Store format type for use in import
        self.use_excel_format = has_excel_format and not has_code_format
        return True
    
    def import_gatepasses(self):
        """Import gatepasses from dataframe with batch processing"""
        if not self.load_file():
            return False
        
        if not self.validate_data():
            return False
        
        batch_size = 5  # Process 5 rows at a time to avoid database locks
        total_rows = len(self.df)
        
        # Valid status values
        valid_statuses = ['pending', 'warden_approved', 'warden_rejected', 
                         'security_approved', 'returned', 'completed']
        
        # Map Excel column names to code names if using Excel format
        column_map = {}
        if hasattr(self, 'use_excel_format') and self.use_excel_format:
            column_map = {
                'Hall Ticket No': 'hall_ticket_no',
                'Outing Date': 'outing_date',
                'Outing Time': 'outing_time',
                'Expected Return Date': 'expected_return_date',
                'Expected Return Time': 'expected_return_time',
                'Purpose': 'purpose',
                'Status': 'status'
            }
            # Rename columns to standard names
            self.df = self.df.rename(columns=column_map)
        
        # Process data in batches
        for batch_start in range(0, total_rows, batch_size):
            batch_end = min(batch_start + batch_size, total_rows)
            batch_df = self.df.iloc[batch_start:batch_end]
            
            def process_batch():
                """Process a single batch of rows"""
                with transaction.atomic():
                    for idx, row in batch_df.iterrows():
                        try:
                            # Extract and clean data from row
                            hall_ticket_no = str(row['hall_ticket_no']).strip()
                            purpose = str(row['purpose']).strip()
                            # Convert status to valid format (handle Excel format like "Security Approved")
                            status_raw = str(row['status']).strip()
                            # Map common status values
                            status_map = {
                                'pending': 'pending',
                                'warden approved': 'warden_approved',
                                'warden_approved': 'warden_approved',
                                'warden rejected': 'warden_rejected',
                                'warden_rejected': 'warden_rejected',
                                'security approved': 'security_approved',
                                'security_approved': 'security_approved',
                                'returned': 'returned',
                                'completed': 'completed'
                            }
                            status = status_map.get(status_raw.lower(), status_raw.lower())
                            
                            # Parse dates and times
                            try:
                                outing_date = pd.to_datetime(row['outing_date']).date()
                                outing_time = pd.to_datetime(row['outing_time']).time()
                                expected_return_date = pd.to_datetime(row['expected_return_date']).date()
                                expected_return_time = pd.to_datetime(row['expected_return_time']).time()
                            except Exception as e:
                                self.errors.append(f"Row {idx + 2}: Invalid date/time format - {str(e)}")
                                continue
                            
                            # Parse optional fields
                            actual_return_date = None
                            actual_return_time = None
                            if pd.notna(row.get('actual_return_date')):
                                try:
                                    actual_return_date = pd.to_datetime(row['actual_return_date']).date()
                                except:
                                    pass
                            
                            if pd.notna(row.get('actual_return_time')):
                                try:
                                    actual_return_time = pd.to_datetime(row['actual_return_time']).time()
                                except:
                                    pass
                            
                            parent_verification = bool(row.get('parent_verification', False))
                            
                            # Validate required fields
                            if not all([hall_ticket_no, purpose, status]):
                                self.errors.append(f"Row {idx + 2}: Missing required fields")
                                continue
                            
                            # Find student by hall ticket
                            try:
                                student = Student.objects.get(hall_ticket_no=hall_ticket_no)
                            except Student.DoesNotExist:
                                self.errors.append(f"Row {idx + 2}: Student with hall ticket '{hall_ticket_no}' not found")
                                continue
                            
                            # Validate status
                            if status not in valid_statuses:
                                self.errors.append(
                                    f"Row {idx + 2}: Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}"
                                )
                                continue
                            
                            # Create gatepass record
                            gatepass = GatePass.objects.create(
                                student=student,
                                outing_date=outing_date,
                                outing_time=outing_time,
                                expected_return_date=expected_return_date,
                                expected_return_time=expected_return_time,
                                purpose=purpose,
                                status=status,
                                parent_verification=parent_verification,
                                actual_return_date=actual_return_date,
                                actual_return_time=actual_return_time
                            )
                            
                            # Record success
                            self.successes.append({
                                'row': idx + 2,
                                'student': student.student_name,
                                'hall_ticket': hall_ticket_no,
                                'outing_date': str(outing_date),
                                'status': status
                            })
                            
                        except Exception as e:
                            self.errors.append(f"Row {idx + 2}: {str(e)}")
                            # Continue processing other rows instead of stopping
                            continue
            
            # Execute batch with retry logic
            try:
                execute_with_retry(process_batch, max_retries=10, initial_delay=1.0)
            except Exception as e:
                self.errors.append(f"Database error at rows {batch_start + 2}-{batch_end + 1}: {str(e)}")
                return False
            finally:
                # Close the database connection after each batch
                connections.close_all()
        
        return len(self.errors) == 0
