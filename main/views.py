from django.shortcuts import render
from django.views.generic import FormView
from .forms import  ContactForm, BasketLineForm, AddressSelectionForm, AddressCreateForm
from django.views.generic import ListView, DetailView
from .models import Product, ProductTag, Address, Basket, BasketLine
from django.shortcuts import get_object_or_404
from .forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse,reverse_lazy
from . import models
from django.http import HttpResponseRedirect
import logging
from django import forms as django_forms
from django.db import models as django_models
import django_filters
from django_filters.views import FilterView 
# Create your views here.
logger = logging.getLogger(__name__) 

class ContactUs(FormView):
    form_class = ContactForm
    template_name = 'contact-us.html'
    success_url = '/'
    
    def form_valid(self, form):
        form.send_mail()
        return super().form_valid(form)

class Product_list(ListView):

    model = Product
    context_object_name = 'product_list'
    template_name='main/product_list.html'
    paginate_by = 4
    def get_queryset(self):
        tag = self.kwargs.get('tag')
        if tag != 'all':
            self.tag = get_object_or_404(ProductTag, slug=tag)
            if self.tag:
                products = Product.objects.active().filter(tags=self.tag)
        else:
            products = Product.objects.active() 
        return products.order_by('name')       
class SignUpView(FormView):
    template_name = 'main/signup.html'
    form_class = UserCreationForm

    def get_success_url(self):
        response = self.request.GET.get('next', '/')
        return response
    def form_valid(self, form):
        form.save()
        email = form.cleaned_data['email']
        raw_password = form.cleaned_data['password1']
        user = authenticate(email=email, password=raw_password)
        if user:
            login(self.request, user)
            form.send_mail()
            messages.info(self.request, 'you successfully become a user')
        return super().form_valid(form)
class AddressListView(LoginRequiredMixin, ListView):
    model = Address
    template_name='main/addres_list.html'
    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)
class AddressCreateView(LoginRequiredMixin, CreateView):
    model = Address
    form_class = AddressCreateForm
    success_url = reverse_lazy('main:address_list')
    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        obj.save()
        return super().form_valid(form)
class AddressUpdateView(LoginRequiredMixin, UpdateView):
    model = Address
    fields = ['country', 'address1', 'address2', 'zip_code']

    success_url = reverse_lazy('main:address_list')
    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)
class AddressDeleteView(LoginRequiredMixin, DeleteView):
    model = Address
    success_url = reverse_lazy('main:address_list')
    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


def add_to_basket(request):
    if request.method == 'GET':
        product  = get_object_or_404(Product, pk=request.GET.get('product_id'))
        logger.info('get product')
        print(product.name)
        basket = request.basket
        logger.info('get basket ')
        if not request.basket:
            if request.user.is_authenticated:
                user = request.user

            else:
                user = None
            basket = models.Basket.objects.create(user=user)
            request.session['basket_id'] = basket.id
        basketline, created = models.BasketLine.objects.get_or_create(basket=basket, product=product)
        if not created:
            basketline.quantity += 1
            basketline.save()
            logger.info('basketline quantity')
        return HttpResponseRedirect(reverse('main:product', kwargs={'slug':product.slug}))    

def manage_basket(request):
    if not request.basket:
        return render(request, 'main/basket.html', {'formset': None})
    if request.method == 'POST':
        formset = BasketLineForm(request.POST, instance=request.basket)
        if formset.is_valid():
            formset.save()
    else:
        formset = BasketLineForm(instance=request.basket)
    if request.basket.is_empty():
        return render(request, 'main/basket.html', {'formset': None})
    return render(request, 'main/basket.html', {'formset': formset})                    
class AddressSelectionView(FormView):
    template_name = 'main/address_select.html'
    form_class = AddressSelectionForm
    success_url = reverse_lazy('main:checkout_done')
    def get_form_kwargs(self):
        kwargs =  super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    def form_valid(self, form):
        del self.request.session['basket_id']
        basket = self.request.basket
        basket.create_order(form.cleaned_data['billing_address'], form.cleaned_data['shipping_address'])
        return super().form_valid(form)
class DateInput(django_forms.DateInput):
    input_type = 'date'
class OrderFilter(django_filters.FilterSet):
    class Meta:
        model = models.Order
        fields = {
            'user__email': ['icontains'],
            'status': ['exact'],
            'date_added': ['lt', 'gt'],
            'date_updated': ['lt', 'gt'],
        }
        filter_overrides = {
            django_models.DateTimeField: {
                'filter_class': django_filters.DateFilter,
                'extra': lambda f:{'widget': DateInput}}}
class OrderView(UserPassesTestMixin, FilterView):
    filterset_class = OrderFilter
    login_url = reverse_lazy("main:login")
    def test_func(self):
        return self.request.user.is_staff is True   
def room(request, order_id):
    return render(request, "chat_room.html", {"room_name_json": str(order_id)})