from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from fundraisers.views import fundraiser_detail, payment_success, fundraiser_list
from payments.views import openpay_webhook
from payments.api_views import initiate_payment
from reports.views import export_transactions_excel

from django.views.generic import TemplateView
from django.http import HttpResponse

def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        f"Sitemap: {settings.SITE_URL}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")
from core.models import Fundraiser # Adjust if needed
from django.utils import timezone

def sitemap_xml(request):
    fundraisers = Fundraiser.objects.all()
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        '  <url>',
        f'    <loc>{settings.SITE_URL}/</loc>',
        '    <changefreq>daily</changefreq>',
        '    <priority>1.0</priority>',
        '  </url>',
    ]
    for f in fundraisers:
        lines.append('  <url>')
        lines.append(f'    <loc>{settings.SITE_URL}/f/{f.slug}/</loc>')
        lines.append(f'    <lastmod>{f.updated_at.strftime("%Y-%m-%d")}</lastmod>')
        lines.append('    <changefreq>weekly</changefreq>')
        lines.append('    <priority>0.8</priority>')
        lines.append('  </url>')
    lines.append('</urlset>')
    return HttpResponse("\n".join(lines), content_type="application/xml")

urlpatterns = [
    path('admin/', admin.site.urls),

    # SEO & PWA
    path('robots.txt', robots_txt),
    path('sitemap.xml', sitemap_xml),
    path('manifest.json', TemplateView.as_view(template_name="manifest.json", content_type='application/json'), name='manifest.json'),
    path('sw.js', TemplateView.as_view(template_name="sw.js", content_type='application/javascript'), name='sw.js'),
    
    # Fundraising Pages
    path('', fundraiser_list, name='fundraiser_list'),
    path('f/<slug:slug>/', fundraiser_detail, name='fundraiser_detail'),
    path('payment-success/', payment_success, name='payment_success'),
    path('payment-success/<slug:slug>/', payment_success, name='payment_success_with_slug'),
    
    # Payments API & Webhooks
    path('api/payment/initiate/', initiate_payment, name='api_initiate_payment'),
    path('openpay/callback', openpay_webhook, name='openpay_callback'),
    
    # Reports
    path('admin/export/transactions/', export_transactions_excel, name='admin_export_transactions'),
    path('admin/export/transactions/<int:fundraiser_id>/', export_transactions_excel, name='admin_export_fundraiser_transactions'),
]

handler404 = 'config.views.error_404'
handler500 = 'config.views.error_500'
handler403 = 'config.views.error_403'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
