from django.urls import path,include
from .views import CustomLoginView, delete_invoice, all_invoices, homepage_view
from . import views


urlpatterns = [
    path('', homepage_view, name='homepage'),
    path('login/', CustomLoginView.as_view(), name='login'),

    # Category pages
    path('vat/', views.vat_page, name='vat_page'),
    path('svat/', views.svat_page, name='svat_page'),
    path('non-vat/', views.non_vat_page, name='non_vat_page'),

    # Shared actions
    path('delete/<int:invoice_id>/', delete_invoice, name='delete_invoice'),
    path('all/', all_invoices, name='all_invoices'),

    # ✅ Safe PWA route (use prefix to avoid conflict)
    path('pwa/', include('pwa.urls')),
]

