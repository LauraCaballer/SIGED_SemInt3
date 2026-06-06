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
        deuda_monto = data.get('deuda_monto')
        deuda_tipo = data.get('deuda_tipo')
        deuda_venta_id = data.get('deuda_venta_id')
        
        if not client_email:
            return JsonResponse({'error': 'client_email required'}, status=400)
            
        api_key = os.getenv('BREVO_API_KEY')
        sender_email = os.getenv('BREVO_SENDER_EMAIL', 'formcreatorufps@gmail.com')
        sender_name = os.getenv('BREVO_SENDER_NAME', 'SIGED')
        
        if not api_key:
            from django.conf import settings
            api_key = getattr(settings, 'BREVO_API_KEY', None)
            sender_email = getattr(settings, 'BREVO_SENDER_EMAIL', 'formcreatorufps@gmail.com')
            sender_name = getattr(settings, 'BREVO_SENDER_NAME', 'SIGED')
            
        if not api_key:
            return JsonResponse({'error': 'Brevo configuration missing'}, status=500)
            
        # Build email payload according to Brevo API
        html_content = f"""
        <div style="font-family: Arial, sans-serif; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eaeaea; border-radius: 8px;">
            <h2 style="color: #2563eb; text-align: center;">Recordatorio de Pago Pendiente</h2>
            <p>Estimado/a <strong>{client_name or 'Cliente'}</strong>,</p>
            <p>Le escribimos para recordarle cordialmente que tiene una deuda pendiente registrada en nuestro sistema.</p>
            
            <div style="background-color: #f9fafb; padding: 15px; border-radius: 6px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #4b5563;">Detalles de la Deuda</h3>
                <ul style="list-style-type: none; padding-left: 0;">
                    <li style="margin-bottom: 8px;"><strong>Tipo de Deuda:</strong> {deuda_tipo or 'N/A'}</li>
                    <li style="margin-bottom: 8px;"><strong>ID de Venta:</strong> #{deuda_venta_id or 'N/A'}</li>
                    <li style="margin-bottom: 8px;"><strong>Monto Pendiente:</strong> <span style="color: #dc2626; font-weight: bold; font-size: 1.1em;">${deuda_monto or '0'}</span></li>
                </ul>
            </div>
            
            <p>Le agradecemos que realice el pago lo antes posible para mantener su cuenta al día.</p>
            <p>Si ya realizó el pago, por favor ignore este mensaje.</p>
            
            <hr style="border: none; border-top: 1px solid #eaeaea; margin: 20px 0;" />
            <p style="font-size: 12px; color: #6b7280; text-align: center;">Este es un mensaje automático generado por SIGED, por favor no responda a este correo.</p>
        </div>
        """
        
        payload = {
            'sender': {'email': sender_email, 'name': sender_name},
            'to': [{'email': client_email, 'name': client_name or ''}],
            'subject': f'SIGED - Recordatorio de pago pendiente (#{deuda_venta_id})',
            'htmlContent': html_content
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
