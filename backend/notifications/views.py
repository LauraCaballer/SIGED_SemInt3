import os
import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

# Expecting POST with JSON containing client_id and optional custom message
@csrf_exempt
@require_POST
def send_reminder(request):
    try:
        data = json.loads(request.body)
        client_id = data.get('client_id')
        # In a real app, retrieve client email and name from DB
        # For now, expect client_email and client_name provided
        client_email = data.get('client_email')
        client_name = data.get('client_name')
        if not client_email:
            return JsonResponse({'error': 'client_email required'}, status=400)
        api_key = os.getenv('BREVO_API_KEY')
        sender_email = os.getenv('BREVO_SENDER_EMAIL')
        sender_name = os.getenv('BREVO_SENDER_NAME')
        if not api_key or not sender_email:
            return JsonResponse({'error': 'Brevo configuration missing'}, status=500)
        # Build email payload according to Brevo API
        payload = {
            'sender': {'email': sender_email, 'name': sender_name or ''},
            'to': [{'email': client_email, 'name': client_name or ''}],
            'subject': 'Recordatorio de pago pendiente',
            'htmlContent': f"<p>Estimado/a {client_name or ''},</p><p>Le recordamos que tiene una deuda pendiente. Por favor, revise su cuenta y realice el pago correspondiente.</p><p>Gracias.</p>"
        }
        response = requests.post(
            'https://api.brevo.com/v3/smtp/email',
            json=payload,
            headers={'api-key': api_key, 'Content-Type': 'application/json'}
        )
        if response.status_code >= 200 and response.status_code < 300:
            return JsonResponse({'message': 'Email sent successfully'})
        else:
            return JsonResponse({'error': 'Failed to send email', 'detail': response.text}, status=500)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
