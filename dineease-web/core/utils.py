from django.core.mail import send_mail
from django.conf import settings
from django.contrib.gis.geos import Point
import json


def send_confirmation_email(user, code):
    """
    Send a confirmation email with a 6-digit code.
    """
    subject = "Confirm Your Email Address with DineEase"
    message = f"""
    Hello {user.first_name},

    Thank you for registering with DineEase. 
    Please confirm your email address by using the following code:

    Confirmation Code: {code}

    If you did not register, please ignore this email.
    """
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email] # NOTE: [user.email]

    try:
        send_mail(subject, message, from_email, recipient_list)
    except Exception as e:
        print(f"Failed to send confirmation email: {e}")

def parse_coordinates(coordinates):
    """
    Convert coordinates from string or list to a GeoDjango Point object.
    
    Args:
        coordinates (str | list): Coordinates in string (e.g., "lng,lat") or list (e.g., [lng, lat]).
    
    Returns:
        Point: A GeoDjango Point object.
    
    Raises:
        ValueError: If the coordinates format is invalid.
    """
    if not coordinates:
        return None

    try:
        if isinstance(coordinates, list) and len(coordinates) == 2:
            # If coordinates are a list, directly use them
            lng, lat = coordinates
        elif isinstance(coordinates, str):
            # If coordinates is a string with brackets, parse it into a list
            if coordinates.startswith('[') and coordinates.endswith(']'):
                coordinates = json.loads(coordinates)  # Convert JSON string to list
                if len(coordinates) == 2:
                    lng, lat = coordinates
                else:
                    raise ValueError
            else:
                # If it's a regular string, split by comma
                lng, lat = map(float, coordinates.split(','))
        else:
            raise ValueError
        return Point(lng, lat)
    except (ValueError, TypeError, json.JSONDecodeError):
        raise ValueError("Invalid coordinates format. Expected 'lng,lat' or [lng, lat].")


def enforce_https_in_production(url):
    """
    Convert http to https for URLs when in production mode.
    """
    try:
        if settings.DEBUG is False:
            if not url:
                return url

            if url.startswith('http://'):
                return url.replace('http://', 'https://')
    except Exception as e:
        raise e
    return url