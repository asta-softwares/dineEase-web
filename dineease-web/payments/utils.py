import requests

def send_push_notification(notification_token, title, message, data=None):
    """
    Sends a push notification via Expo Push Notification API.

    :param notification_token: Expo notification token
    :param title: Notification title
    :param message: Notification message
    :param data: Additional data to send with the notification (optional)
    """
    if not notification_token:
        return {"error": "Notification token is missing."}

    payload = {
        "to": notification_token,
        "title": title,
        "body": message,
        "data": data or {}
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    response = requests.post("https://exp.host/--/api/v2/push/send", json=payload, headers=headers)

    if response.status_code != 200:
        print(f"Expo notification failed: {response.text}")
        return {"error": response.text}

    return {"success": True, "response": response.json()}