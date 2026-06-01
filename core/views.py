from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Like, Fundraiser
from votes.models import VoteSession

User = get_user_model()

def user_profile(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)
    is_owner = request.user == profile_user
    
    # Lazy deactivation
    from django.utils import timezone
    now = timezone.now()
    from django.db.models import F
    Fundraiser.objects.filter(creator=profile_user, is_active=True, target_amount__gt=0, collected_amount__gte=F('target_amount')).update(is_active=False)
    VoteSession.objects.filter(creator=profile_user, is_active=True, end_date__lte=now).update(is_active=False)
    
    # Base querysets
    fundraiser_qs = Fundraiser.objects.filter(creator=profile_user)
    vote_qs = VoteSession.objects.filter(creator=profile_user)
    
    if not is_owner:
        # Others only see active and ongoing items
        fundraisers = fundraiser_qs.filter(is_active=True)
        votes = vote_qs.filter(is_active=True)
    else:
        # Owner sees everything
        fundraisers = fundraiser_qs
        votes = vote_qs
    
    context = {
        'profile_user': profile_user,
        'fundraisers': fundraisers,
        'votes': votes,
        'is_owner': is_owner,
    }
    return render(request, 'core/public_profile.html', context)

@login_required
def toggle_like(request):
    if request.method == 'POST':
        content_type_id = request.POST.get('content_type_id')
        object_id = request.POST.get('object_id')
        
        content_type = get_object_or_404(ContentType, id=content_type_id)
        
        like, created = Like.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=object_id
        )
        
        if not created:
            like.delete()
            action = 'unliked'
        else:
            action = 'liked'
            
        likes_count = Like.objects.filter(content_type=content_type, object_id=object_id).count()
        
        return JsonResponse({
            'success': True,
            'action': action,
            'likes_count': likes_count
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def global_search(request):
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    results = []
    from django.utils import timezone
    now = timezone.now()
    from django.db.models import F
    
    # Lazy deactivation
    Fundraiser.objects.filter(is_active=True, target_amount__gt=0, collected_amount__gte=F('target_amount')).update(is_active=False)
    VoteSession.objects.filter(is_active=True, end_date__lte=now).update(is_active=False)

    # Search Fundraisers - Only active
    fundraisers = Fundraiser.objects.filter(
        Q(title__icontains=query) | Q(beneficiary_name__icontains=query),
        is_active=True
    )[:5]
    
    for f in fundraisers:
        results.append({
            'type': 'fundraiser',
            'title': f.title,
            'url': f.get_absolute_url(),
            'image': f.background_media.url if f.background_media else None,
            'subtitle': f'Collecte • {f.beneficiary_name}'
        })
        
    # Search Votes - Only active and not expired
    votes = VoteSession.objects.filter(
        Q(title__icontains=query),
        is_active=True
    ).filter(
        Q(end_date__isnull=True) | Q(end_date__gt=now)
    )[:5]
    
    for v in votes:
        results.append({
            'type': 'vote',
            'title': v.title,
            'url': v.get_absolute_url(),
            'image': v.background_image.url if v.background_image else None,
            'subtitle': f'Vote • {v.category}'
        })
        
    return JsonResponse({'results': results})
