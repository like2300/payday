from django import forms
from django.contrib.auth.models import User
from core.models import Fundraiser, Profile
from votes.models import VoteSession, Choice

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'input-premium'}),
            'last_name': forms.TextInput(attrs={'class': 'input-premium'}),
            'email': forms.EmailInput(attrs={'class': 'input-premium'}),
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'bio', 'phone']
        widgets = {
            'avatar': forms.FileInput(attrs={
                'class': 'hidden', 
                'id': 'avatar-input',
                'accept': 'image/*',
                'onchange': 'previewFile()'
            }),
            'bio': forms.Textarea(attrs={'class': 'input-premium', 'rows': 3, 'placeholder': 'Parlez-nous de vous...'}),
            'phone': forms.TextInput(attrs={
                'class': 'input-premium', 
                'placeholder': '06 666 00 00',
                'inputmode': 'numeric',
                'pattern': '[0-9]*',
                'onkeypress': 'return event.charCode >= 48 && event.charCode <= 57'
            }),
        }

class FundraiserForm(forms.ModelForm):
    class Meta:
        model = Fundraiser
        fields = [
            'title', 'description', 'category', 'beneficiary_name', 
            'beneficiary_phone', 'beneficiary_image', 'background_media', 
            'media_type', 'target_amount', 'min_donation_amount'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'input-premium'}),
            'description': forms.Textarea(attrs={'class': 'input-premium', 'rows': 4}),
            'category': forms.Select(attrs={'class': 'input-premium'}),
            'beneficiary_name': forms.TextInput(attrs={'class': 'input-premium'}),
            'beneficiary_phone': forms.TextInput(attrs={
                'class': 'input-premium',
                'inputmode': 'numeric',
                'pattern': '[0-9]*',
                'onkeypress': 'return event.charCode >= 48 && event.charCode <= 57'
            }),
            'beneficiary_image': forms.FileInput(attrs={'class': 'input-premium'}),
            'background_media': forms.FileInput(attrs={'class': 'input-premium'}),
            'media_type': forms.Select(attrs={'class': 'input-premium'}),
            'target_amount': forms.NumberInput(attrs={
                'class': 'input-premium',
                'onkeypress': 'return event.charCode >= 48 && event.charCode <= 57'
            }),
            'min_donation_amount': forms.NumberInput(attrs={
                'class': 'input-premium',
                'onkeypress': 'return event.charCode >= 48 && event.charCode <= 57'
            }),
        }

class VoteSessionForm(forms.ModelForm):
    class Meta:
        model = VoteSession
        fields = [
            'title', 'description', 'category', 'background_image', 
            'vote_price', 'end_date'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'input-premium'}),
            'description': forms.Textarea(attrs={'class': 'input-premium', 'rows': 4}),
            'category': forms.Select(attrs={'class': 'input-premium'}),
            'background_image': forms.FileInput(attrs={'class': 'input-premium'}),
            'vote_price': forms.NumberInput(attrs={
                'class': 'input-premium',
                'onkeypress': 'return event.charCode >= 48 && event.charCode <= 57'
            }),
            'end_date': forms.DateTimeInput(attrs={'class': 'input-premium', 'type': 'datetime-local'}),
        }

class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['name', 'image', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'input-premium',
                'placeholder': 'Nom du candidat ou de l\'option'
            }),
            'description': forms.Textarea(attrs={
                'class': 'input-premium',
                'rows': 2, 
                'placeholder': 'Brève description...'
            }),
            'image': forms.FileInput(attrs={
                'class': 'hidden',
                'accept': 'image/*'
            })
        }
