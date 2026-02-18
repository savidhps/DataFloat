"""
Input validation service for LuckyVista.
Implements strict schema-based validation with security checks.
"""
import re
from typing import Dict, Any, Tuple, Optional


class ValidationError(Exception):
    """Custom exception for validation errors."""
    
    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(self.message)


class ValidationService:
    """Service for validating user inputs against schemas."""
    
    # Validation schemas
    REGISTRATION_SCHEMA = {
        "name": {
            "type": "string",
            "required": True,
            "min_length": 2,
            "max_length": 100,
            "pattern": r"^[a-zA-Z\s\-']+$"
        },
        "email": {
            "type": "string",
            "required": True,
            "format": "email",
            "max_length": 255
        },
        "phone": {
            "type": "string",
            "required": True,
            "pattern": r"^\+?[1-9]\d{1,14}$"
        },
        "tenant": {
            "type": "string",
            "required": True,
            "min_length": 2,
            "max_length": 100,
            "pattern": r"^[a-zA-Z0-9\-_]+$"
        },
        "password": {
            "type": "string",
            "required": True,
            "min_length": 8,
            "max_length": 128
        }
    }
    
    SIGNIN_SCHEMA = {
        "email": {
            "type": "string",
            "required": True,
            "format": "email"
        },
        "password": {
            "type": "string",
            "required": True
        }
    }
    
    FEEDBACK_SCHEMA = {
        "overall_rating": {
            "type": "integer",
            "required": True,
            "min": 1,
            "max": 5
        },
        "experience_rating": {
            "type": "integer",
            "required": True,
            "min": 1,
            "max": 5
        },
        "comments": {
            "type": "string",
            "required": True,
            "min_length": 10,
            "max_length": 5000
        },
        "feature_satisfaction": {
            "type": "integer",
            "required": False,
            "min": 1,
            "max": 5
        },
        "ui_rating": {
            "type": "integer",
            "required": False,
            "min": 1,
            "max": 5
        },
        "recommendation_likelihood": {
            "type": "integer",
            "required": False,
            "min": 1,
            "max": 10
        },
        "additional_suggestions": {
            "type": "string",
            "required": False,
            "max_length": 2000
        }
    }
    
    # Email regex pattern (RFC 5322 simplified)
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    # Security patterns to detect
    INJECTION_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # Script tags
        r'javascript:',  # JavaScript protocol
        r'on\w+\s*=',  # Event handlers
        r'<iframe',  # Iframes
        r'<object',  # Objects
        r'<embed',  # Embeds
        r'(\bUNION\b|\bSELECT\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b|\bDROP\b).*(\bFROM\b|\bWHERE\b|\bINTO\b)',  # SQL injection
        r'--',  # SQL comments
        r'/\*.*\*/',  # SQL block comments
    ]
    
    def validate_registration(self, data: Dict[str, Any]) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validate registration data.
        
        Args:
            data: Registration data dictionary
        
        Returns:
            Tuple of (is_valid, error_message, field_name)
        """
        return self._validate_against_schema(data, self.REGISTRATION_SCHEMA)
    
    def validate_signin(self, data: Dict[str, Any]) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validate sign-in data.
        
        Args:
            data: Sign-in data dictionary
        
        Returns:
            Tuple of (is_valid, error_message, field_name)
        """
        return self._validate_against_schema(data, self.SIGNIN_SCHEMA)
    
    def validate_feedback(self, data: Dict[str, Any]) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validate feedback data.
        
        Args:
            data: Feedback data dictionary
        
        Returns:
            Tuple of (is_valid, error_message, field_name)
        """
        return self._validate_against_schema(data, self.FEEDBACK_SCHEMA)
    
    def _validate_against_schema(self, data: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validate data against a schema.
        
        Args:
            data: Data to validate
            schema: Schema definition
        
        Returns:
            Tuple of (is_valid, error_message, field_name)
        """
        # Check for unexpected fields (strict schema validation)
        allowed_fields = set(schema.keys())
        provided_fields = set(data.keys())
        unexpected_fields = provided_fields - allowed_fields
        
        if unexpected_fields:
            return False, f"Unexpected fields: {', '.join(unexpected_fields)}", None
        
        # Validate each field
        for field_name, field_schema in schema.items():
            value = data.get(field_name)
            
            # Check required fields
            if field_schema.get('required', False):
                if value is None or (isinstance(value, str) and value.strip() == ''):
                    return False, f"{field_name} is required", field_name
            
            # Skip validation for optional fields that are not provided
            if value is None and not field_schema.get('required', False):
                continue
            
            # Type validation
            field_type = field_schema.get('type')
            if field_type == 'string' and not isinstance(value, str):
                return False, f"{field_name} must be a string", field_name
            elif field_type == 'integer' and not isinstance(value, int):
                return False, f"{field_name} must be an integer", field_name
            
            # String validations
            if field_type == 'string' and isinstance(value, str):
                # Length validation
                min_length = field_schema.get('min_length')
                if min_length and len(value) < min_length:
                    return False, f"{field_name} must be at least {min_length} characters", field_name
                
                max_length = field_schema.get('max_length')
                if max_length and len(value) > max_length:
                    return False, f"{field_name} must not exceed {max_length} characters", field_name
                
                # Pattern validation
                pattern = field_schema.get('pattern')
                if pattern and not re.match(pattern, value):
                    return False, f"{field_name} format is invalid", field_name
                
                # Email format validation
                if field_schema.get('format') == 'email':
                    is_valid, error = self.validate_email(value)
                    if not is_valid:
                        return False, error, field_name
                
                # Injection pattern detection
                if self.detect_injection_patterns(value):
                    return False, f"{field_name} contains potentially malicious content", field_name
            
            # Integer validations
            if field_type == 'integer' and isinstance(value, int):
                min_val = field_schema.get('min')
                if min_val is not None and value < min_val:
                    return False, f"{field_name} must be at least {min_val}", field_name
                
                max_val = field_schema.get('max')
                if max_val is not None and value > max_val:
                    return False, f"{field_name} must not exceed {max_val}", field_name
        
        return True, None, None
    
    def validate_email(self, email: str) -> Tuple[bool, Optional[str]]:
        """
        Validate email format according to RFC 5322.
        
        Args:
            email: Email address to validate
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not email or not isinstance(email, str):
            return False, "Email is required"
        
        if not re.match(self.EMAIL_PATTERN, email):
            return False, "Invalid email format"
        
        return True, None
    
    def validate_password_strength(self, password: str) -> Tuple[bool, Optional[str]]:
        """
        Validate password strength requirements.
        
        Args:
            password: Password to validate
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not password or not isinstance(password, str):
            return False, "Password is required"
        
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if len(password) > 128:
            return False, "Password must not exceed 128 characters"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one digit"
        
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
            return False, "Password must contain at least one special character"
        
        return True, None
    
    def detect_injection_patterns(self, input_str: str) -> bool:
        """
        Detect potential injection patterns in input.
        
        Args:
            input_str: String to check
        
        Returns:
            True if injection pattern detected, False otherwise
        """
        if not isinstance(input_str, str):
            return False
        
        input_lower = input_str.lower()
        
        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, input_lower, re.IGNORECASE):
                return True
        
        return False
    
    def contains_injection_patterns(self, input_str: str) -> bool:
        """
        Alias for detect_injection_patterns for backward compatibility.
        
        Args:
            input_str: String to check
        
        Returns:
            True if injection pattern detected, False otherwise
        """
        return self.detect_injection_patterns(input_str)
    
    def sanitize_html(self, input_str: str) -> str:
        """
        Sanitize HTML by removing potentially dangerous tags.
        
        Args:
            input_str: String to sanitize
        
        Returns:
            Sanitized string
        """
        if not isinstance(input_str, str):
            return input_str
        
        # Remove script tags
        sanitized = re.sub(r'<script[^>]*>.*?</script>', '', input_str, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove event handlers
        sanitized = re.sub(r'on\w+\s*=\s*["\']?[^"\']*["\']?', '', sanitized, flags=re.IGNORECASE)
        
        # Remove javascript: protocol
        sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
        
        # Remove iframe, object, embed tags
        sanitized = re.sub(r'<(iframe|object|embed)[^>]*>.*?</\1>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
        
        return sanitized