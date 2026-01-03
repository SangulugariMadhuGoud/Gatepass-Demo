import re
import time
import logging
from django.conf import settings
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.core.cache import cache
from django.utils import timezone
from django.urls import resolve
from .models import SecurityLog

logger = logging.getLogger(__name__)

class DatabaseFirewallMiddleware:
    """
    Comprehensive database firewall middleware to protect against hackers.
    Implements rate limiting, input validation, and security monitoring.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # Rate limiting settings
        self.rate_limit_requests = getattr(settings, 'FIREWALL_RATE_LIMIT_REQUESTS', 100)
        self.rate_limit_window = getattr(settings, 'FIREWALL_RATE_LIMIT_WINDOW', 60)  # seconds

        # Suspicious patterns to block
        self.suspicious_patterns = [
            r'union\s+select',  # SQL injection
            r';\s*drop\s+table',  # SQL injection
            r';\s*delete\s+from',  # SQL injection
            r'--',  # SQL comments
            r'/\*.*\*/',  # SQL comments
            r'<script',  # XSS
            r'javascript:',  # XSS
            r'on\w+\s*=',  # XSS event handlers
            r'../../../',  # Path traversal
            r'\.\./\.\./',  # Path traversal
        ]

        # Compile regex patterns
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.suspicious_patterns]

        # Whitelisted IPs (for admin access)
        self.whitelist_ips = getattr(settings, 'FIREWALL_WHITELIST_IPS', [])

        # Blacklisted IPs
        self.blacklist_ips = getattr(settings, 'FIREWALL_BLACKLIST_IPS', [])

    def __call__(self, request):
        # Check IP blacklists/whitelists
        client_ip = self.get_client_ip(request)

        if client_ip in self.blacklist_ips:
            self.log_security_event(request, 'BLACKLISTED_IP', f'Blocked access from blacklisted IP: {client_ip}')
            return HttpResponseForbidden('Access denied.')

        # Rate limiting check
        if not self.check_rate_limit(client_ip):
            self.log_security_event(request, 'RATE_LIMIT_EXCEEDED', f'Rate limit exceeded for IP: {client_ip}')
            return HttpResponseForbidden('Rate limit exceeded. Please try again later.')

        # Input validation and sanitization
        if not self.validate_request(request):
            self.log_security_event(request, 'MALICIOUS_INPUT', f'Malicious input detected from IP: {client_ip}')
            return HttpResponseBadRequest('Invalid request.')

        # Log suspicious activity
        self.monitor_suspicious_activity(request)

        response = self.get_response(request)

        # Add security headers
        response = self.add_security_headers(response)

        return response

    def get_client_ip(self, request):
        """Get the real client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def check_rate_limit(self, client_ip):
        """Check if the client has exceeded rate limits"""
        cache_key = f'rate_limit_{client_ip}'
        current_time = int(time.time())

        # Get current request count
        request_data = cache.get(cache_key, {'count': 0, 'window_start': current_time})

        # Reset window if expired
        if current_time - request_data['window_start'] > self.rate_limit_window:
            request_data = {'count': 0, 'window_start': current_time}

        # Increment count
        request_data['count'] += 1

        # Check limit
        if request_data['count'] > self.rate_limit_requests:
            return False

        # Update cache
        cache.set(cache_key, request_data, self.rate_limit_window)
        return True

    def validate_request(self, request):
        """Validate request data for malicious content"""
        # Check URL path
        if self.contains_suspicious_patterns(request.path):
            return False

        # Check query parameters
        for key, values in request.GET.lists():
            for value in values:
                if self.contains_suspicious_patterns(str(value)):
                    return False

        # Check POST data
        if request.method == 'POST':
            for key, values in request.POST.lists():
                for value in values:
                    if self.contains_suspicious_patterns(str(value)):
                        return False

        return True

    def contains_suspicious_patterns(self, content):
        """Check if content contains suspicious patterns"""
        for pattern in self.compiled_patterns:
            if pattern.search(content):
                return True
        return False

    def monitor_suspicious_activity(self, request):
        """Monitor and log suspicious activities"""
        client_ip = self.get_client_ip(request)

        # Log authentication attempts
        if 'login' in request.path.lower() and request.method == 'POST':
            self.log_security_event(request, 'LOGIN_ATTEMPT', f'Login attempt from IP: {client_ip}')

        # Log admin access attempts
        if 'admin' in request.path.lower():
            self.log_security_event(request, 'ADMIN_ACCESS', f'Admin access attempt from IP: {client_ip}')

        # Log database-related operations
        if any(keyword in request.path.lower() for keyword in ['export', 'excel', 'data']):
            self.log_security_event(request, 'DATA_EXPORT', f'Data export from IP: {client_ip}')

    def log_security_event(self, request, event_type, message):
        """Log security events to database"""
        try:
            client_ip = self.get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None

            SecurityLog.objects.create(
                event_type=event_type,
                message=message,
                ip_address=client_ip,
                user_agent=user_agent[:500],  # Truncate if too long
                user=user,
                path=request.path,
                method=request.method,
                timestamp=timezone.now()
            )
        except Exception as e:
            logger.error(f"Failed to log security event: {e}")

    def add_security_headers(self, response):
        """Add security headers to response"""
        # Prevent clickjacking
        response['X-Frame-Options'] = 'DENY'

        # Prevent MIME type sniffing
        response['X-Content-Type-Options'] = 'nosniff'

        # XSS protection
        response['X-XSS-Protection'] = '1; mode=block'

        # Referrer policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        # Content Security Policy (basic)
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        response['Content-Security-Policy'] = csp

        return response



