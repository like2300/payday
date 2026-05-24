from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from .models import VoteSession, Candidate, VoteRecord
from payments.services import OpenPayService
from django.conf import settings
from decimal import Decimal

def vote_list(request):
    search_query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    
    sessions = VoteSession.objects.filter(is_active=True)
    
    if search_query:
        sessions = sessions.filter(title__icontains=search_query)
        
    if category:
        sessions = sessions.filter(category=category)
        
    return render(request, 'votes/list.html', {
        'sessions': sessions,
        'categories': VoteSession.CATEGORY_CHOICES,
        'search_query': search_query,
        'selected_category': category
    })

def vote_detail(request, slug):
    session = get_object_or_404(VoteSession, slug=slug, is_active=True)
    candidates = session.candidates.all().order_by('-vote_count')
    return render(request, 'votes/detail.html', {
        'session': session,
        'candidates': candidates,
    })

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def initiate_vote(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id, session__is_active=True)
    session = candidate.session
    ip_address = get_client_ip(request)
    
    if request.method == 'POST':
        if session.vote_price > 0:
            voter_name = request.POST.get('voter_name', 'Anonyme')
            voter_phone = request.POST.get('voter_phone', '')
            
            # Paid vote logic
            site_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')
            result = OpenPayService.create_payment(
                amount=session.vote_price,
                description=f"Vote pour {candidate.name} - {session.title}",
                customer_name=voter_name,
                customer_phone=voter_phone,
                external_id=f"vote_{candidate.id}_{ip_address}", # use IP in external_id for tracking
                success_url=f"{site_url}{reverse('vote_detail', kwargs={'slug': session.slug})}?status=success",
                callback_url=f"{site_url}/openpay/callback",
            )
            
            if result['success']:
                return redirect(result['payment_link'])
            else:
                messages.error(request, f"Erreur OpenPay: {result.get('error')}")
                return redirect('vote_detail', slug=session.slug)
        else:
            # Free vote logic with IP check
            has_voted = VoteRecord.objects.filter(
                candidate__session=session, 
                ip_address=ip_address,
                amount_paid=0
            ).exists()
            
            if has_voted:
                messages.error(request, "Désolé, vous avez déjà voté pour cette session.")
                return redirect('vote_detail', slug=session.slug)
            
            VoteRecord.objects.create(
                candidate=candidate,
                ip_address=ip_address,
                amount_paid=0
            )
            candidate.vote_count += 1
            candidate.save()
            messages.success(request, f"Merci ! Votre vote pour {candidate.name} a été enregistré.")
            return redirect('vote_detail', slug=session.slug)
            
    return redirect('vote_detail', slug=session.slug)
