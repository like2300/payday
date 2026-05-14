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

def fundraiser_detail(request, slug):
    """
    Public view for a specific fundraiser collection page.
    """
    fundraiser = get_object_or_404(Fundraiser, slug=slug, is_active=True)
    transactions = fundraiser.transactions.filter(status='completed').order_by('-completed_at')
    
    context = {
        'fundraiser': fundraiser,
        'transactions': transactions,
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
