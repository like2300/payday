import json
import logging
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from core.models import Transaction, Fundraiser
from django.utils import timezone

logger = logging.getLogger(__name__)

@csrf_exempt
@require_POST
def openpay_webhook(request):
    """
    Webhook endpoint for OpenPay payment confirmations.
    """
    try:
        data = json.loads(request.body)
        logger.info(f"OpenPay Webhook received: {data}")
        
        # OpenPay sends external_id inside the metadata object
        metadata = data.get('metadata', {})
        external_id = metadata.get('external_id') or data.get('external_id')
        
        # OpenPay status can be 'status' or 'payment_status' or inside data object
        openpay_status = data.get('status') or data.get('payment_status')
        if not openpay_status and 'data' in data:
            openpay_status = data['data'].get('status')
            
        openpay_transaction_id = data.get('transaction_id') or data.get('payment_token')
        if not openpay_transaction_id and 'data' in data:
            openpay_transaction_id = data['data'].get('payment_token') or data['data'].get('transaction_id')
        
        if not external_id:
            logger.error(f"Missing external_id in webhook data: {data}")
            return JsonResponse({'error': 'Missing external_id'}, status=400)
            
        # Handle VoteRecord
        if isinstance(external_id, str) and external_id.startswith('vote_'):
            try:
                from votes.models import VoteRecord
                record_id = external_id.replace('vote_', '')
                vote_record = VoteRecord.objects.get(id=record_id)
            except (VoteRecord.DoesNotExist, ValueError):
                logger.error(f"VoteRecord {external_id} not found for webhook.")
                return JsonResponse({'error': 'VoteRecord not found'}, status=404)
            
            is_success = openpay_status in ['COMPLETED', 'paid', 'success', 'SUCCESS']
            if is_success:
                if vote_record.status != 'completed':
                    vote_record.status = 'completed'
                    if openpay_transaction_id:
                        vote_record.openpay_transaction_id = openpay_transaction_id
                    vote_record.save()
                    
                    # Increment choice vote count
                    choice = vote_record.choice
                    choice.vote_count += 1
                    choice.save()
                    logger.info(f"VoteRecord {record_id} completed. Choice {choice.id} updated.")
            elif openpay_status in ['FAILED', 'failed', 'error']:
                vote_record.status = 'failed'
                vote_record.save()
                logger.warning(f"VoteRecord {record_id} failed.")
                
            return HttpResponse(status=200)

        # Handle Transaction (Fundraiser)
        try:
            transaction = Transaction.objects.get(id=external_id)
        except (Transaction.DoesNotExist, ValueError):
            logger.error(f"Transaction {external_id} not found for webhook.")
            return JsonResponse({'error': 'Transaction not found'}, status=404)
            
        # Update transaction status
        # Note: OpenPay status might be 'paid', 'COMPLETED', 'success' etc.
        is_success = openpay_status in ['COMPLETED', 'paid', 'success', 'SUCCESS']
        
        if is_success:
            if transaction.status != 'completed':
                transaction.status = 'completed'
                transaction.completed_at = timezone.now()
                if openpay_transaction_id:
                    transaction.openpay_transaction_id = openpay_transaction_id
                transaction.save()
                
                # Update fundraiser collected amount
                fundraiser = transaction.fundraiser
                # Force refresh from DB to avoid race conditions
                fundraiser.refresh_from_db()
                fundraiser.collected_amount += transaction.amount
                
                # Automatically deactivate if target reached
                if fundraiser.target_amount and fundraiser.collected_amount >= fundraiser.target_amount:
                    fundraiser.is_active = False
                    logger.info(f"Fundraiser {fundraiser.id} reached target. Deactivating.")
                
                fundraiser.save()
                logger.info(f"Transaction {external_id} completed. Fundraiser {fundraiser.id} updated.")
        
        elif openpay_status in ['FAILED', 'failed', 'error']:
            transaction.status = 'failed'
            transaction.error_message = data.get('error_message') or data.get('message', 'Payment failed')
            transaction.save()
            logger.warning(f"Transaction {external_id} failed.")
            
        return HttpResponse(status=200)
        
    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
