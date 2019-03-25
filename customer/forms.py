from django import forms
from django.core import validators
from restaurant_admin.models import Table
from django.db.models import Max


class FormOrder(forms.Form):
    table = forms.IntegerField(label="Table Number", min_value=1,
                               max_value=Table.objects.all().aggregate(Max('table_number'))['table_number__max'])
    details = forms.CharField(widget=forms.Textarea, required=False)
    takeaway = forms.BooleanField(required=False,
                                  widget=forms.CheckboxInput(
                                      attrs={'onclick':"myFunction()"}))
    botCatcher = forms.CharField(required=False, widget=forms.HiddenInput,
                                 validators=[validators.MaxLengthValidator(0)])
