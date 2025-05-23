
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
from .models import Invoice
from django.core.paginator import Paginator

# ✅ Custom login view class
class CustomLoginView(LoginView):
    template_name = 'invoice_manager/login.html'

# ✅ Prefix mapping
CATEGORY_PREFIXES = {
    'VAT': 'VILTS-',
    'SVAT': 'VILSS-',
    'NON-VAT': 'VILCS-',
    'DELIVERY': 'WH/OUT-',
    'SAMPLE': 'WH/CST-',
    'WARRANTY': 'WRT-',
}

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

@login_required
def category_all_view(request, category, template):
    prefix = CATEGORY_PREFIXES.get(category, 'INV-')
    query = request.GET.get('q', '')

    invoices = Invoice.objects.filter(category=category).order_by('-uploaded_at')
    if query:
        invoices = invoices.filter(code__icontains=query)

    paginator = Paginator(invoices, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, template, {
        'page_obj': page_obj,
        'query': query,
        'prefix': prefix,
        'category': category,
    })

@csrf_exempt
@login_required
def handle_upload_view(request, category, template):
    prefix = CATEGORY_PREFIXES.get(category, 'INV-')
    query = request.GET.get('q', '')
    invoices = Invoice.objects.filter(category=category).order_by('-uploaded_at')

    if query:
        invoices = invoices.filter(code__icontains=query)

    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        suffix = request.POST.get('code_suffix') or request.POST.get('custom_number', '')
        suffix = suffix.strip()

        if file.content_type in ['application/pdf', 'image/jpeg', 'image/jpg'] and suffix:
            full_code = f"{prefix}{suffix}"
            file_hash = get_file_hash(file)

            if Invoice.objects.filter(code=full_code).exists():
                today = timezone.now()
                month_start = today.replace(day=1)
                total_this_month = invoices.filter(uploaded_at__gte=month_start).count()
                current_month = today.strftime('%B %Y')

                return render(request, template, {
                    'invoices': invoices,
                    'query': query,
                    'total_this_month': total_this_month,
                    'current_month': current_month,
                    'category': category,
                    'prefix': prefix,
                    'error_message': f"❌ Invoice with code {full_code} already exists. Please re upload & use a different number."
                })

            if not Invoice.objects.filter(file_hash=file_hash, category=category).exists():
                file.name = f"{full_code}.{file.name.split('.')[-1]}"
                invoice = Invoice(
                    file=file,
                    uploaded_at=timezone.now(),
                    uploaded_by=request.user,
                    category=category,
                    code=full_code,
                    file_hash=file_hash
                )
                invoice.save()
            return redirect(request.path)

    today = timezone.now()
    month_start = today.replace(day=1)
    total_this_month = invoices.filter(uploaded_at__gte=month_start).count()
    current_month = today.strftime('%B %Y')

    context = {
        'invoices': invoices[:10],
        'query': query,
        'total_this_month': total_this_month,
        'current_month': current_month,
        'category': category,
        'prefix': prefix,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('invoice_manager/invoice_list.html', context, request)
        return JsonResponse({'html': html})

    return render(request, template, context)

# ✅ Individual category views
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
def delivery_page(request):
    return handle_upload_view(request, category='DELIVERY', template='invoice_manager/delivery_page.html')

@login_required
def sample_page(request):
    return handle_upload_view(request, category='SAMPLE', template='invoice_manager/sample_page.html')

@login_required
def warranty_page(request):
    return handle_upload_view(request, category='WARRANTY', template='invoice_manager/warranty_page.html')

@login_required
def homepage_view(request):
    return render(request, 'invoice_manager/homepage.html')



@login_required
def vat_all_view(request):
    return category_all_view(request, category='VAT', template='invoice_manager/vat_all.html')

@login_required
def svat_all_view(request):
    return category_all_view(request, category='SVAT', template='invoice_manager/svat_all.html')

@login_required
def non_vat_all_view(request):
    return category_all_view(request, category='NON-VAT', template='invoice_manager/non_vat_all.html')

@login_required
def delivery_all_view(request):
    return category_all_view(request, category='DELIVERY', template='invoice_manager/delivery_all.html')

@login_required
def sample_all_view(request):
    return category_all_view(request, category='SAMPLE', template='invoice_manager/sample_all.html')

@login_required
def warranty_all_view(request):
    return category_all_view(request, category='WARRANTY', template='invoice_manager/warranty_all.html')
