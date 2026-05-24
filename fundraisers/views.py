from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from core.models import Fundraiser

def fundraiser_list(request):
    """
    Home page listing all active fundraisers with search and filtering.
    """
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    sort = request.GET.get('sort', '-created_at')
    
    fundraisers = Fundraiser.objects.filter(is_active=True)
    
    if query:
        fundraisers = fundraisers.filter(
            Q(title__icontains=query) | 
            Q(beneficiary_name__icontains=query) |
            Q(description__icontains=query)
        )
        
    if category:
        fundraisers = fundraisers.filter(category=category)
        
    if sort in ['collected_amount', '-collected_amount', 'created_at', '-created_at']:
        fundraisers = fundraisers.order_by(sort)
        
    context = {
        'fundraisers': fundraisers,
        'search_query': query,
        'selected_category': category,
        'current_sort': sort,
        'categories': Fundraiser.CATEGORY_CHOICES
    }
    return render(request, 'fundraisers/list.html', context)

from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.paginator import Paginator

def fundraiser_detail(request, slug):
    """
    Public view for a specific fundraiser collection page.
    """
    fundraiser = get_object_or_404(Fundraiser, slug=slug, is_active=True)
    
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

    context = {
        'fundraiser': fundraiser,
        'hide_sidebar': True,
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
