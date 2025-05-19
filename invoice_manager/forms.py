from django import forms
from .models import Invoice

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['file']

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file and not file.name.endswith('.pdf'):
            raise forms.ValidationError("Only PDF files are allowed.")
        return file
