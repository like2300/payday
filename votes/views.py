from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from django.db.models import Count, Q
from django.contrib.contenttypes.models import ContentType
from .models import VoteSession, Choice, VoteRecord
from core.models import Like
from payments.services import OpenPayService
from django.conf import settings
from decimal import Decimal

from django.core.paginator import Paginator

from django.utils import timezone

def vote_list(request):
    search_query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    page_number = request.GET.get('page', 1)
    
    # Filter active and not expired sessions
    now = timezone.now()

    # Lazy deactivation for expired sessions
    VoteSession.objects.filter(
        is_active=True,
        end_date__lte=now
    ).update(is_active=False)

    # Get ContentType for VoteSession
    session_ct = ContentType.objects.get_for_model(VoteSession)
    
    sessions = VoteSession.objects.filter(
        is_active=True
    ).annotate(
        likes_count=Count('core_like', filter=Q(core_like__content_type=session_ct))
    ).order_by('-is_verified', '-likes_count', '-created_at')
    
    if search_query:
        sessions = sessions.filter(title__icontains=search_query)
        
    if category:
        sessions = sessions.filter(category=category)
        
    paginator = Paginator(sessions, 6) # 6 sessions per page
    page_obj = paginator.get_page(page_number)
    
    context = {
        'sessions': page_obj,
        'categories': VoteSession.CATEGORY_CHOICES,
        'search_query': search_query,
        'selected_category': category
    }

    if request.headers.get('HX-Request'):
        return render(request, 'votes/partials/vote_cards.html', context)

    return render(request, 'votes/list.html', context)

from django.http import Http404

def vote_detail(request, slug):
    session = get_object_or_404(VoteSession, slug=slug)
    
    # If not active, only creator can see it
    if not session.is_active and session.creator != request.user:
        raise Http404("Cette session de vote n'est plus active.")
    
    # Get ContentType for Choice
    choice_ct = ContentType.objects.get_for_model(Choice)
    
    choices = session.choices.all().annotate(
        likes_count=Count('core_like', filter=Q(core_like__content_type=choice_ct))
    ).order_by('-likes_count', '-vote_count')
    
    ip_address = get_client_ip(request)
    
    # Calculate total votes for the session
    total_votes = sum(choice.vote_count for choice in choices)

    # Attach percentage to each choice
    for choice in choices:
        if total_votes > 0:
            choice.percentage = (choice.vote_count * 100) / total_votes
        else:
            choice.percentage = 0
    
    # Check if this IP has already voted for a free vote in this session
    has_voted = False
    if session.vote_price == 0:
        has_voted = VoteRecord.objects.filter(
            choice__session=session,
            ip_address=ip_address,
            status='completed'
        ).exists()

    return render(request, 'votes/detail.html', {
        'session': session,
        'choices': choices,
        'has_voted': has_voted,
        'total_votes': total_votes,
    })

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def initiate_vote(request, choice_id):
    choice = get_object_or_404(Choice, id=choice_id, session__is_active=True)
    session = choice.session
    
    if session.is_expired:
        messages.error(request, "Désolé, cette session de vote est terminée.")
        return redirect('vote_detail', slug=session.slug)

    ip_address = get_client_ip(request)
    
    if request.method == 'POST':
        if session.vote_price > 0:
            voter_name = request.POST.get('voter_name', 'Anonyme')
            voter_phone = request.POST.get('voter_phone', '')
            
            # Create a pending vote record
            vote_record = VoteRecord.objects.create(
                choice=choice,
                voter_name=voter_name,
                voter_phone=voter_phone,
                ip_address=ip_address,
                amount_paid=session.vote_price,
                status='pending'
            )
            
            # Paid vote logic
            site_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')
            result = OpenPayService.create_payment(
                amount=session.vote_price,
                description=f"Vote pour {choice.name} - {session.title}",
                customer_name=voter_name,
                customer_phone=voter_phone,
                external_id=f"vote_{vote_record.id}", # use record ID
                success_url=f"{site_url}{reverse('vote_detail', kwargs={'slug': session.slug})}?status=success",
                callback_url=f"{site_url}/openpay/callback",
            )
            
            if result['success']:
                # Optionally save the openpay transaction ID if returned early
                if result.get('openpay_transaction_id'):
                    vote_record.openpay_transaction_id = result['openpay_transaction_id']
                    vote_record.save()
                return redirect(result['payment_link'])
            else:
                vote_record.status = 'failed'
                vote_record.save()
                messages.error(request, f"Erreur OpenPay: {result.get('error')}")
                return redirect('vote_detail', slug=session.slug)
        else:
            # Free vote logic with IP check
            # We check if ANY choice in the same session has been voted for by this IP
            has_voted = VoteRecord.objects.filter(
                choice__session=session, 
                ip_address=ip_address,
                status='completed'
            ).exists()
            
            if has_voted:
                messages.error(request, "Désolé, vous avez déjà voté pour cette session (limite d'un vote gratuit par personne).")
                return redirect('vote_detail', slug=session.slug)
            
            VoteRecord.objects.create(
                choice=choice,
                ip_address=ip_address,
                amount_paid=0,
                status='completed'
            )
            choice.vote_count += 1
            choice.save()
            messages.success(request, f"Merci ! Votre vote pour {choice.name} a été enregistré.")
            return redirect('vote_detail', slug=session.slug)
            
    return redirect('vote_detail', slug=session.slug)
