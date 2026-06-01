from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.models import Fundraiser, Transaction, Profile
from votes.models import VoteSession, VoteRecord, Choice
from .models import WithdrawalRequest, PlatformRule
from .forms import FundraiserForm, VoteSessionForm, ChoiceForm, UserForm, ProfileForm
from django.db.models import Sum
from django.forms import inlineformset_factory

@login_required
def profile_edit(request):
    # Get or create profile for existing users
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    # Auto-fetch Google profile picture if it's a new profile and user has social account
    if created or not profile.avatar:
        try:
            from allauth.socialaccount.models import SocialAccount
            social_acc = SocialAccount.objects.filter(user=request.user, provider='google').first()
            if social_acc and 'picture' in social_acc.extra_data:
                # Store the URL or ideally download it. For now, we'll store a note or use it as fallback in template.
                # To keep it simple, we'll just ensure we have the data available.
                pass
        except ImportError:
            pass
            
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profil mis à jour avec succès !")
            return redirect('dashboard')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=profile)
    
    return render(request, 'surveys/profile_edit.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'title': 'Modifier le Profil'
    })

@login_required
def fundraiser_create(request):
    if request.method == 'POST':
        form = FundraiserForm(request.POST, request.FILES)
        if form.is_valid():
            fundraiser = form.save(commit=False)
            fundraiser.creator = request.user
            fundraiser.save()
            messages.success(request, "Votre collecte a été créée avec succès !")
            return redirect('dashboard')
    else:
        form = FundraiserForm()
    
    rules = PlatformRule.objects.filter(is_active=True)
    return render(request, 'surveys/fundraiser_create.html', {
        'form': form, 
        'title': 'Créer une Collecte',
        'rules': rules
    })

@login_required
def vote_create(request):
    ChoiceFormSet = inlineformset_factory(VoteSession, Choice, form=ChoiceForm, extra=3, can_delete=False)
    
    if request.method == 'POST':
        form = VoteSessionForm(request.POST, request.FILES)
        formset = ChoiceFormSet(request.POST, request.FILES)
        
        if form.is_valid() and formset.is_valid():
            session = form.save(commit=False)
            session.creator = request.user
            session.save()
            
            formset.instance = session
            formset.save()
            
            messages.success(request, "Votre session de vote a été créée avec succès !")
            return redirect('dashboard')
    else:
        form = VoteSessionForm()
        formset = ChoiceFormSet()
        
    rules = PlatformRule.objects.filter(is_active=True)
    return render(request, 'surveys/vote_create.html', {
        'form': form, 
        'formset': formset,
        'title': 'Créer un Vote',
        'rules': rules
    })

@login_required
def fundraiser_edit(request, pk):
    fundraiser = get_object_or_404(Fundraiser, pk=pk, creator=request.user)
    if request.method == 'POST':
        form = FundraiserForm(request.POST, request.FILES, instance=fundraiser)
        if form.is_valid():
            form.save()
            messages.success(request, "Collecte mise à jour !")
            return redirect('dashboard')
    else:
        form = FundraiserForm(instance=fundraiser)
    return render(request, 'surveys/fundraiser_create.html', {'form': form, 'title': 'Modifier la Collecte'})

@login_required
def fundraiser_delete(request, pk):
    fundraiser = get_object_or_404(Fundraiser, pk=pk, creator=request.user)
    if request.method == 'POST':
        fundraiser.delete()
        messages.success(request, "Collecte supprimée.")
    return redirect('dashboard')

@login_required
def vote_edit(request, pk):
    session = get_object_or_404(VoteSession, pk=pk, creator=request.user)
    ChoiceFormSet = inlineformset_factory(VoteSession, Choice, form=ChoiceForm, extra=1, can_delete=True)
    
    if request.method == 'POST':
        form = VoteSessionForm(request.POST, request.FILES, instance=session)
        formset = ChoiceFormSet(request.POST, request.FILES, instance=session)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, "Vote mis à jour !")
            return redirect('dashboard')
    else:
        form = VoteSessionForm(instance=session)
        formset = ChoiceFormSet(instance=session)
        
    return render(request, 'surveys/vote_create.html', {
        'form': form,
        'formset': formset,
        'title': 'Modifier le Vote'
    })

@login_required
def vote_delete(request, pk):
    session = get_object_or_404(VoteSession, pk=pk, creator=request.user)
    if request.method == 'POST':
        session.delete()
        messages.success(request, "Vote supprimé.")
    return redirect('dashboard')

@login_required
def dashboard(request):
    """
    User dashboard showing their created fundraisers, votes, and earnings.
    """
    # Ensure profile exists for analytics/UI
    Profile.objects.get_or_create(user=request.user)
    
    from django.db import models
    from django.db.models import Sum, Q, Value
    from django.db.models.functions import Coalesce
    
    user_fundraisers = Fundraiser.objects.filter(creator=request.user)
    # Annotate each vote session with its total revenue
    user_votes = VoteSession.objects.filter(creator=request.user).annotate(
        total_revenue=Coalesce(Sum('choices__votes__amount_paid', filter=Q(choices__votes__status='completed')), Value(0, output_field=models.DecimalField()))
    )
    
    # Calculate total earnings from fundraisers
    fundraiser_total = user_fundraisers.aggregate(total=Sum('collected_amount'))['total'] or 0
    
    # Calculate total earnings from votes
    vote_total = VoteRecord.objects.filter(
        choice__session__creator=request.user,
        status='completed'
    ).aggregate(total=Sum('amount_paid'))['total'] or 0
    
    total_balance = fundraiser_total + vote_total
    
    # Withdrawal requests
    withdrawal_requests = WithdrawalRequest.objects.filter(user=request.user)
    
    context = {
        'fundraisers': user_fundraisers,
        'votes': user_votes,
        'total_balance': total_balance,
        'withdrawal_requests': withdrawal_requests,
        'fundraiser_total': fundraiser_total,
        'vote_total': vote_total,
    }
    return render(request, 'surveys/dashboard.html', context)

@login_required
def request_withdrawal(request, source_type, source_id):
    """
    Request a withdrawal for a specific fundraiser or vote session.
    """
    if source_type == 'fundraiser':
        source = get_object_or_404(Fundraiser, id=source_id, creator=request.user)
        amount = source.collected_amount
        # Check if already has a pending withdrawal for this
        if WithdrawalRequest.objects.filter(fundraiser=source, status='pending').exists():
            messages.warning(request, "Une demande de retrait est déjà en cours pour cette collecte.")
            return redirect('dashboard')
        
        WithdrawalRequest.objects.create(
            user=request.user,
            fundraiser=source,
            amount=amount,
            status='pending'
        )
    elif source_type == 'vote':
        source = get_object_or_404(VoteSession, id=source_id, creator=request.user)
        amount = VoteRecord.objects.filter(choice__session=source, status='completed').aggregate(total=Sum('amount_paid'))['total'] or 0
        
        if WithdrawalRequest.objects.filter(vote_session=source, status='pending').exists():
            messages.warning(request, "Une demande de retrait est déjà en cours pour ce vote.")
            return redirect('dashboard')
            
        WithdrawalRequest.objects.create(
            user=request.user,
            vote_session=source,
            amount=amount,
            status='pending'
        )
        
    messages.success(request, "Votre demande de retrait a été enregistrée. Elle sera examinée prochainement.")
    return redirect('dashboard')

@login_required
def download_withdrawal_slip(request, withdrawal_id):
    """
    Generates a withdrawal slip for the user to present at the office.
    """
    withdrawal = get_object_or_404(WithdrawalRequest, id=withdrawal_id, user=request.user)
    
    if withdrawal.status != 'approved':
        messages.error(request, "Votre demande de retrait n'est pas encore approuvée ou a déjà été traitée.")
        return redirect('dashboard')
        
    return render(request, 'surveys/withdrawal_slip.html', {'withdrawal': withdrawal})
