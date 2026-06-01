from django.shortcuts import render, get_object_or_404
from django.db import models
from django.db.models import Q, Count
from django.contrib.contenttypes.models import ContentType
from core.models import Fundraiser, Like

from django.core.paginator import Paginator

def fundraiser_list(request):
    """
    Home page listing all active fundraisers with search and popularity sorting.
    """
    # Lazy deactivation for fundraisers that reached target
    Fundraiser.objects.filter(
        is_active=True,
        target_amount__gt=0,
        collected_amount__gte=models.F('target_amount')
    ).update(is_active=False)

    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    page_number = request.GET.get('page', 1)
    
    # Get ContentType for Fundraiser to filter likes correctly
    fundraiser_ct = ContentType.objects.get_for_model(Fundraiser)
    
    # Annotate with likes count and filter active/uncompleted
    fundraisers = Fundraiser.objects.filter(is_active=True).annotate(
        likes_count=Count('core_like', filter=Q(core_like__content_type=fundraiser_ct))
    ).exclude(
        Q(target_amount__gt=0) & Q(collected_amount__gte=models.F('target_amount'))
    ).order_by('-is_verified', '-likes_count', '-created_at')
    
    if query:
        fundraisers = fundraisers.filter(
            Q(title__icontains=query) | 
            Q(beneficiary_name__icontains=query) |
            Q(description__icontains=query)
        )
        
    if category:
        fundraisers = fundraisers.filter(category=category)
        
    paginator = Paginator(fundraisers, 6) # 6 fundraisers per page
    page_obj = paginator.get_page(page_number)

    context = {
        'fundraisers': page_obj,
        'search_query': query,
        'selected_category': category,
        'categories': Fundraiser.CATEGORY_CHOICES
    }

    if request.headers.get('HX-Request'):
        return render(request, 'fundraisers/partials/fundraiser_cards.html', context)

    return render(request, 'fundraisers/list.html', context)

from django.http import JsonResponse, Http404
from django.template.loader import render_to_string
from django.core.paginator import Paginator

def fundraiser_detail(request, slug):
    """
    Public view for a specific fundraiser collection page.
    """
    fundraiser = get_object_or_404(Fundraiser, slug=slug)
    
    # If not active, only creator can see it
    if not fundraiser.is_active and fundraiser.creator != request.user:
        raise Http404("Cette collecte n'est plus active.")
    
    # Check if closed
    is_closed = fundraiser.is_closed

    # Handle AJAX request for donors
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        query = request.GET.get('q', '')
        page_number = request.GET.get('page', 1)
        
        transactions = fundraiser.transactions.filter(status='completed').order_by('-completed_at')
        
        if query:
            transactions = transactions.filter(
                Q(donor_name__icontains=query) |
                Q(message__icontains=query)
            )
            
        paginator = Paginator(transactions, 10) # 10 donors per page
        page_obj = paginator.get_page(page_number)
        
        donors_html = render_to_string('fundraisers/partials/donor_list.html', {
            'page_obj': page_obj,
            'fundraiser': fundraiser
        })
        
        return JsonResponse({
            'html': donors_html,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages
        })

    # For initial render, get recent donors
    recent_donors = fundraiser.transactions.filter(status='completed').order_by('-completed_at')[:5]

    context = {
        'fundraiser': fundraiser,
        'recent_donors': recent_donors,
        'hide_sidebar': True,
        'is_closed': is_closed,
        'show_donor_list': getattr(fundraiser, 'settings', None).show_donor_list if hasattr(fundraiser, 'settings') else True
    }
    return render(request, 'fundraisers/detail.html', context)

def payment_success(request, slug=None):
    """
    Success page after a payment.
    """
    context = {
        'fundraiser_slug': slug
    }
    return render(request, 'fundraisers/success.html', context)
