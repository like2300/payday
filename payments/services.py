import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class OpenPayService:
    """Service class for OpenPay API integration using Payment Links"""
    
    BASE_URL = settings.OPENPAY_BASE_URL
    API_KEY = settings.OPENPAY_API_KEY
    
    @classmethod
    def get_headers(cls):
        return {
            'XO-API-KEY': cls.API_KEY,
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
    
    @classmethod
    def create_payment(cls, amount, description, customer_name=None, customer_phone=None, external_id=None, success_url=None, callback_url=None):
        """
        Creates a payment link via /v1/payment-link
        """
        url = f"{cls.BASE_URL}/payment-link"
        
        # Ensure amount is an integer
        try:
            amount_val = int(float(amount))
        except (ValueError, TypeError):
            amount_val = 0

        payload = {
            "amount": amount_val,
            "description": description[:100], # Keep it concise
            "metadata": {}
        }
        
        # Add external_id to metadata if provided
        if external_id:
            payload["metadata"]["external_id"] = str(external_id)
        
        # Only include customer if we have at least a name or phone
        customer_data = {}
        if customer_name and customer_name.strip():
            customer_data["name"] = customer_name.strip()
        if customer_phone and customer_phone.strip():
            customer_data["phone"] = customer_phone.strip()
            
        if customer_data:
            payload["customer"] = customer_data
            
        if success_url:
            payload["success_url"] = success_url
            
        if callback_url:
            payload["webhook_url"] = callback_url

        try:
            logger.info(f"Sending request to OpenPay: {url} with payload: {payload}")
            response = requests.post(
                url, 
                json=payload, 
                headers=cls.get_headers(),
                timeout=15
            )
            
            if response.status_code != 201:
                logger.error(f"OpenPay API Error {response.status_code}: {response.text}")
                
            response.raise_for_status()
            data = response.json()
            
            # The API response structure according to doc:
            # { "success": true, "data": { "payment_url": "...", "payment_token": "...", ... } }
            if data.get('success'):
                payment_data = data.get('data', {})
                return {
                    'success': True,
                    'payment_link': payment_data.get('payment_url'),
                    'openpay_transaction_id': payment_data.get('payment_token'), # Or another unique ID if available
                    'status': payment_data.get('status'),
                }
            return {'success': False, 'error': 'API returned success=false'}
            
        except Exception as e:
            logger.error(f"OpenPay Payment Link Creation Error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    @classmethod
    def get_transaction_status(cls, token):
        """
        Checks status via /v1/transaction/{token} or similar if available for payment links
        """
        url = f"{cls.BASE_URL}/transaction/{token}"
        try:
            response = requests.get(url, headers=cls.get_headers(), timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"OpenPay Status Check Error: {str(e)}")
            return None
