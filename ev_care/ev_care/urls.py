"""
URL configuration for ev_care project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from user_app.views import *
from service_app.views import *
from charging_center.views import *
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/',UserRegistration.as_view(),name='signup'),
    path('signin/',SigninView.as_view(),name='signin'),
    path('logout/',LogoutView.as_view(),name='logout'),
    path('forgot-password/', PasswordForgotView.as_view(), name='forgot-password'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),

    path('addv/',VehicleAddView.as_view(),name="addv"),
    path('updatev/<int:pk>',VehicleUpdateView.as_view(),name='updatev'),
    path('listv/',VehicleListView.as_view(),name='listv'),
    path('deletev/<int:pk>',VehicleDeleteView.as_view(),name='deletev'),
    path('',BaseView.as_view(),name='home'),

    path('services/',ServicecenterView.as_view(),name='serviceup'),
    path('serviceList/',ServiceListView.as_view(),name='servicelist'),
    path('Serviceupdate/<int:pk>/',ServicecenterUpdate.as_view(),name='serviceupdate'),
    path('Servicedelete/<int:pk>/',ServicecenterDelete.as_view(),name='serviceupdate'),

    path('product/<int:service_centre_id>',CreateProduct.as_view(),name='product'),
    path('productlist/<int:service_centre_id>',ListProductView.as_view(),name='productlist'),
    path('productupdate/<int:pk>/', UpdateProduct.as_view(), name='product-edit'),
    path('productdelete/<int:pk>/', DeleteProduct.as_view(), name='product-delete'),

    path('userservicelist/',UserServiceListView.as_view(),name="userservicelist"),
    path('userproductlist/<int:service_centre_id>/',UserListProductView.as_view(),name='userproductlist'),
    path('userservice/<int:service_centre_id>/',ServiceCreateView.as_view(),name='userserviceCreate'),

    path('my-services/',ServiceRquestList.as_view(),name='servicerequest'),
    path('userserviceupdate/<int:pk>/',ServiceUpdate.as_view(),name="serviceupdate"),
    path('userservicedelete/<int:pk>/',ServiceDelete.as_view(),name='servicedelete'),
    path('servicelist_center/<int:service_centre_id>',ServiceRquestInCenter.as_view(),name='ServiceRquestInCenter'),

    path("servicecenter/service/inline-update/<int:pk>/",ServiceCenterInlineUpdate.as_view(),name="servicecenter_inline_update"),

    path("service/payment/<int:service_id>/",ServicePaymentView.as_view(),name="service_payment"),
    path('buy-product/<int:product_id>/', BuyProductView.as_view(), name='buy_product'),
    path('razorpay-checkout/<int:order_id>/', razorpay_checkout, name='razorpay_checkout'),
    path('razorpay-verify/<int:order_id>/', razorpay_verify, name='razorpay_verify'),
    path('order-success/<int:order_id>/', order_success, name='order_success'),
    path('my-orders/', BuyedProductList.as_view(), name='my_orders'),

    path('service-orders/<int:service_centre_id>/',BuyedProductseviceList.as_view(),name='servicelist_orders'),
    path('service-orders/<int:service_centre_id>/',BuyedProductList.as_view(),name='service_orders'),
    path('send-order-otp/<int:order_id>/',send_order_otp,name='send_order_otp'),
    path('confirm-order-otp/<int:order_id>/',confirm_order_otp,name='confirm_order_otp'),

    path('chargingStation/',ChargingStationView.as_view(),name='add-station'),
    path('liststation/',ChargingListView.as_view(),name='slot-list'),
    path("stations/<int:station_id>/",SloteCreationView.as_view(),name="slot-create"),
    path("stationlist/<int:station_id>/",SlotListView.as_view(),name="slot-list"),
    path("stations/<int:station_id>/slots/<int:pk>/update/",SlotUpdateView.as_view(),name="slot-update"),
    path("stations/<int:station_id>/slots/<int:pk>/delete/",SlotDeleteView.as_view(),name="slot-delete"),

    path('user_station_list/',ListStations.as_view(),name='u_station_li'),
    path('station/<int:pk>/slots/',StationSlotsView.as_view(), name='station_slots'),
    path('slot/book/<int:slot_id>/', book_slot, name='book_slot'),
    path('slot/cancel/<int:slot_id>/',cancel_slot, name='cancel_slot'),
    path('payment/<int:slot_id>/',payment, name='payment'),



]
urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
