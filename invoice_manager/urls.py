from django.urls import path, include
from . import views
from .views import (
    CustomLoginView,
    delete_invoice,
    all_invoices,
    homepage_view,
    vat_page,
    svat_page,
    non_vat_page,
    delivery_page,
    sample_page,
    warranty_page,
)


urlpatterns = [
    # Homepage (access via http://localhost:port/)
    path('', homepage_view, name='homepage'),

    # Auth
    path('login/', CustomLoginView.as_view(), name='login'),

    # Invoice Category Upload Pages
    path('vat/', vat_page, name='vat_page'),
    path('svat/', svat_page, name='svat_page'),
    path('non-vat/', non_vat_page, name='non_vat_page'),
    path('delivery/', delivery_page, name='delivery_page'),
    path('sample/', sample_page, name='sample_page'),
    path('warranty/', warranty_page, name='warranty_page'),

    # Add these after the category pages
  path('vat/all/', views.vat_all_view, name='vat_all'),
  path('svat/all/', views.svat_all_view, name='svat_all'),
  path('non-vat/all/', views.non_vat_all_view, name='non_vat_all'),
  path('delivery/all/', views.delivery_all_view, name='delivery_all'),
  path('sample/all/', views.sample_all_view, name='sample_all'),
  path('warranty/all/', views.warranty_all_view, name='warranty_all'),


    



    # Shared invoice actions
    path('delete/<int:invoice_id>/', delete_invoice, name='delete_invoice'),
    path('all/', all_invoices, name='all_invoices'),

    # PWA support (progressive web app)
    path('pwa/', include('pwa.urls')),
]
