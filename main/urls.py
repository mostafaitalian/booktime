import rest_framework
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.generic import DetailView, TemplateView
from rest_framework import routers
from rest_framework.authtoken import views as authtoken_views
from rest_framework.authtoken.views import obtain_auth_token

from . import admin, endpoints, views
from .forms import LoginForm
from .models import Product
from .views import ContactUs, Product_list, SignUpView

app_name = 'main'

router = routers.DefaultRouter()
router.register(r'orderlines', endpoints.PaidOrderLineViewSet)
router.register(r'orders', endpoints.PaidOrderViewSet)
urlpatterns = [
    

    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('about-us/', TemplateView.as_view(template_name='aboutus.html'), name='about-us' ),
    path('contact-us/', ContactUs.as_view(), name='contact_us'),
    path('products/<slug:tag>/', Product_list.as_view(), name='products'),
    path('product/<slug:slug>/', DetailView.as_view(model=Product), name="product"),
    path('login/', auth_views.LoginView.as_view(template_name='main/loginv2.html', form_class=LoginForm), name="login"),
    path('signup/', SignUpView.as_view(), name="signup"),
    path('address-list/', views.AddressListView.as_view(), name='address_list'),
    path('address/create/', views.AddressCreateView.as_view(), name='address_create'),
    path('address/<int:pk>/update/', views.AddressUpdateView.as_view(), name="address_update"),
    path('address/<int:pk>/delete/', views.AddressDeleteView.as_view(), name='address_delete'),
    path('add_to_basket/', views.add_to_basket, name="add_to_basket"),
    path('manage_basket/', views.manage_basket, name='manage_basket'),
    path('address/select', views.AddressSelectionView.as_view(), name='address_select'),
    path('order/done/', TemplateView.as_view(template_name='main/order_done.html'), name='checkout_done'),
    path('order/dashboard/', views.OrderView.as_view(), name="order_dashboard"),
    path("customer-service/<int:order_id>/", views.room, name="cs-chatroom"),
    path("customer-service/", TemplateView.as_view(template_name="customer-service.html"), name="cs_main"),
    path('api/', include(router.urls)),
    path("mobile-api/auth/", authtoken_views.obtain_auth_token, name="mobile_token"),
    path("mobile-api/my-orders/", endpoints.my_orders, name="mobile_my_orders"),
]
