# Configuration Google Auth (Haram Style)

## 1. Prérequis (.env)
```env
GOOGLE_CLIENT_ID=votre_client_id
GOOGLE_CLIENT_SECRET=votre_secret
```

## 2. Django Settings
Ajoutez à `INSTALLED_APPS` :
```python
INSTALLED_APPS = [
    ...
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]
```

Configurez `SOCIALACCOUNT_PROVIDERS` :
```python
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": config('GOOGLE_CLIENT_ID', default=''),
            "secret": config('GOOGLE_CLIENT_SECRET', default=''),
            "key": "",
        },
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
    }
}
```

## 3. URLs
```python
urlpatterns = [
    ...
    path('accounts/', include('allauth.urls')),
]
```

## 4. Redirections
```python
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
ACCOUNT_EMAIL_VERIFICATION = 'none' # Pour prototype
```
