from django import forms
from django.core.mail import send_mail
import logging
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from django.contrib.auth.forms import UsernameField
from . import models
from django.contrib.auth import authenticate
from django.forms import inlineformset_factory
from . import widgets, models
logger = logging.getLogger(__name__) 
class ContactForm(forms.Form):
    name = forms.CharField(label='your name', max_length=100)
    message = forms.CharField(max_length=400, widget=forms.Textarea)
    def send_mail(self):
        send_mail('Site Message', self.cleaned_data['message'], 'site@domain.com', ['customer@domain.com'], fail_silenty=False)
    
class UserCreationForm(DjangoUserCreationForm):
    class Meta(DjangoUserCreationForm.Meta):
        model = models.User
        fields= ['email']
        field_classes = {'email': UsernameField}
    def send_mail(self):
        logger.info('sending welcome email  to {} upon signup '.format(self.cleaned_data['email']))
        send_mail('welcome {}'.format(self.cleaned_data['email']), 'message', 'eng_mustafa_yossef@hotmai.com', [self.cleaned_data['email'],], fail_silently=False)
class LoginForm(forms.Form):
    email = forms.EmailField(label='email address')
    password = forms.CharField(strip=False, widget=forms.PasswordInput)

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user  = None
        return super().__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']
        if email is not None and password:
            self.user = authenticate(self.request,
            email=email,
            password=password)
        if self.user is None:
            raise forms.ValidationError("Invalid email/password combination.")
        logger.info("Authentication successful for email=%s", email)
        return self.cleaned_data
    def get_user(self):
        return self.user
BasketLineForm = inlineformset_factory(models.Basket, models.BasketLine, fields=('quantity',), extra=0, widgets={'quantity': widgets.PlusMinusNumberInput()})
class AddressSelectionForm(forms.Form):
    billing_address = forms.ModelChoiceField(queryset=None, help_text='bill')
    shipping_address  = forms.ModelChoiceField(queryset=None)

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = models.Address.objects.filter(user=user)
        self.fields['billing_address'].queryset = queryset
        self.fields['shipping_address'].queryset = queryset
class AddressCreateForm(forms.ModelForm):
    class Meta:
        model = models.Address
        exclude = ['user',]        