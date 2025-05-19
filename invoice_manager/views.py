from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.conf import settings
from django.template.loader import render_to_string
import os
import hashlib

from django.contrib.auth.views import LoginView
from .forms import InvoiceForm
from .models import Invoice

from django.db.models.functions import TruncMonth
from django.db.models import Count
from datetime import datetime, timedelta
from django.core.paginator import Paginator

# ✅ Custom login view class
class CustomLoginView(LoginView):
    template_name = 'invoice_manager/login.html'

# ✅ Auto ID format mapping
CATEGORY_CODES = {
    'VAT': ('VILTS-', 41816),
    'SVAT': ('VILSS-', 22381),
    'NON-VAT': ('NON-', 1000),
}

def get_next_invoice_code(category):
    prefix, start = CATEGORY_CODES.get(category, ('INV-', 1))
    last_invoice = (
        Invoice.objects.filter(category=category, code__startswith=prefix)
        .order_by('-uploaded_at')
        .first()
    )
    if last_invoice and last_invoice.code:
        try:
            last_number = int(last_invoice.code.replace(prefix, ''))
            return f"{prefix}{last_number + 1}"
        except:
            pass
    return f"{prefix}{start}"

def get_file_hash(file):
    hasher = hashlib.md5()
    for chunk in file.chunks():
        hasher.update(chunk)
    return hasher.hexdigest()

@login_required
def delete_invoice(request, invoice_id):
    if not request.user.is_superuser:
        return redirect('homepage')

    invoice = get_object_or_404(Invoice, id=invoice_id)
    file_path = os.path.join(settings.MEDIA_ROOT, invoice.file.name)
    if os.path.exists(file_path):
        os.remove(file_path)

    invoice.delete()
    return redirect(request.META.get('HTTP_REFERER', 'homepage'))

@login_required
def all_invoices(request):
    query = request.GET.get('q', '')
    invoices = Invoice.objects.all().order_by('-uploaded_at')
    if query:
        invoices = invoices.filter(code__icontains=query)

    paginator = Paginator(invoices, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'invoice_manager/all_invoices.html', {
        'query': query,
        'page_obj': page_obj
    })

@csrf_exempt
@login_required
def handle_upload_view(request, category, template):
    query = request.GET.get('q', '')
    invoices = Invoice.objects.filter(category=category).order_by('-uploaded_at')

    if query:
        invoices = invoices.filter(code__icontains=query)

    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        if file.content_type in ['application/pdf', 'image/jpeg', 'image/jpg']:
            file_hash = get_file_hash(file)

            # Check for duplicates
            if not Invoice.objects.filter(file_hash=file_hash, category=category).exists():
                invoice_code = get_next_invoice_code(category)
                file.name = f"{invoice_code}.{file.name.split('.')[-1]}"
                invoice = Invoice(
                    file=file,
                    uploaded_at=timezone.now(),
                    uploaded_by=request.user,
                    category=category,
                    code=invoice_code,
                    file_hash=file_hash
                )
                invoice.save()
            return redirect(request.path)

    # Monthly summary
    today = timezone.now()
    month_start = today.replace(day=1)
    total_this_month = invoices.filter(uploaded_at__gte=month_start).count()
    current_month = today.strftime('%B %Y')

    context = {
        'invoices': invoices,
        'query': query,
        'total_this_month': total_this_month,
        'current_month': current_month,
        'category': category,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('invoice_manager/invoice_list.html', context, request)
        return JsonResponse({'html': html})

    return render(request, template, context)

# Individual views
@login_required
def vat_page(request):
    return handle_upload_view(request, category='VAT', template='invoice_manager/vat_page.html')

@login_required
def svat_page(request):
    return handle_upload_view(request, category='SVAT', template='invoice_manager/svat_page.html')

@login_required
def non_vat_page(request):
    return handle_upload_view(request, category='NON-VAT', template='invoice_manager/non_vat_page.html')

@login_required
def homepage_view(request):
    return render(request, 'invoice_manager/homepage.html')
