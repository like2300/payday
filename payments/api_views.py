from decimal import Decimal

from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response

from core.models import Fundraiser, Transaction
from payments.services import OpenPayService


@api_view(["POST"])
def initiate_payment(request):
    """
    API endpoint to initiate a payment via OpenPay.
    """
    fundraiser_id = request.data.get("fundraiser_id")
    amount = request.data.get("amount")
    phone = request.data.get("phone", "")  # Optional now
    provider = request.data.get("provider")
    donor_name = request.data.get("donor_name")

    if not all([fundraiser_id, amount, provider]):
        return Response({"success": False, "error": "Données manquantes"}, status=400)

    fundraiser = get_object_or_404(Fundraiser, id=fundraiser_id, is_active=True)

    if fundraiser.is_closed:
        return Response(
            {
                "success": False,
                "error": "Cette collecte est clôturée car l'objectif a été atteint. Merci pour votre générosité !",
            },
            status=400,
        )

    # Validation du montant
    try:
        amount_decimal = Decimal(str(amount))
    except (ValueError, TypeError):
        return Response({"success": False, "error": "Montant invalide"}, status=400)

    if amount_decimal < Decimal("100"):
        return Response(
            {
                "success": False,
                "error": "Le montant minimum autorisé par OpenPay est de 100 XAF.",
            },
            status=400,
        )

    if amount_decimal < fundraiser.min_donation_amount:
        return Response(
            {
                "success": False,
                "error": f"Le montant minimum pour cette collecte est de {fundraiser.min_donation_amount} XAF.",
            },
            status=400,
        )

    # Create internal transaction
    transaction = Transaction.objects.create(
        fundraiser=fundraiser,
        amount=Decimal(amount),
        donor_phone=phone,
        provider=provider,
        donor_name=donor_name,
        status="pending",
    )

    # Call OpenPay
    site_url = getattr(settings, "SITE_URL", "http://127.0.0.1:8000")
    result = OpenPayService.create_payment(
        amount=amount,
        description=f"Participation: {fundraiser.title}",
        customer_name=donor_name,
        customer_phone=phone,
        external_id=transaction.id,
        success_url=f"{site_url}/payment-success/{fundraiser.slug}/",
        callback_url=f"{site_url}/openpay/callback",
    )

    if result["success"]:
        transaction.openpay_transaction_id = result["openpay_transaction_id"]
        transaction.openpay_link = result["payment_link"]
        transaction.save()
        return Response({"success": True, "payment_link": result["payment_link"]})
    else:
        transaction.status = "failed"
        transaction.error_message = result.get("error")
        transaction.save()
        return Response({"success": False, "error": result.get("error")}, status=500)
