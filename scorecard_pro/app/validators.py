from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

# Validator for hours worked per week (0 to 168)
def validate_hours_worked(value):
    if value < 0 or value > 168:
        raise ValidationError("Hours worked per week must be between 0 and 168.")

# Validator for percentage values (0 to 100)
def validate_percentage(value):
    if value < 0 or value > 100:
        raise ValidationError("Value must be between 0 and 100.")

# Validator for customer rating (0 to 5)
def validate_customer_rating(value):
    if value < 0 or value > 5:
        raise ValidationError("Customer rating must be between 0 and 5.")

# General positive number validator (0 and above)
def validate_positive(value):
    if value < 0:
        raise ValidationError("Value must be 0 or greater.")
