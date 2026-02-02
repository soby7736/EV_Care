from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate,login,logout
from django.urls import reverse_lazy
from django.views.generic import View,CreateView,UpdateView,DeleteView,ListView,TemplateView,DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse
from user_app.models import *
from user_app.forms import *
from service_app.models import *
from charging_center.models import *
from charging_center.forms import *
from django.utils import timezone
from django.http import HttpResponseForbidden
import razorpay
import random
import time
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required


# Create your views here.

class UserRegistration(CreateView):
    model =CustomUser
    form_class =UserRegistrationform
    template_name = 'signup.html'
    success_url = reverse_lazy('signin')

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.set_password(form.cleaned_data['password'])
        obj.save()
        return redirect("signin")

class SigninView(View):
    
    def get(self, request):
        return render(request, "signin.html")
    
    def post(self, request):

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)  
            print("success")
            return redirect("home")

        return redirect("signin")

# LogoutView  
class LogoutView(View):

    def get(self,request):
        
        logout(request)

        return redirect("home")
    
class BaseView(TemplateView):
    template_name = "home.html"

class PasswordForgotView(View):
    
    def get(self, request):
        return render(request, "forgot.html")

    def post(self, request):
        username = request.POST.get('username')
        email = request.POST.get('email')

        try:
            user = CustomUser.objects.get(username=username, email=email)

            otp = str(random.randint(1000,9999))

            # Store OTP in session
            request.session['reset_otp'] = otp
            request.session['reset_user_id'] = user.id
            request.session['otp_time'] = int(time.time())

            send_mail(
                subject="Password Reset OTP - EV Care",
                message=f"Your OTP is {otp}. Valid for 5 minutes.",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )

            messages.success(request, "OTP sent to your email.")
            return redirect('verify-otp')

        except CustomUser.DoesNotExist:
            messages.error(request, "Invalid username or email")
            return redirect('forgot-password')
        
class VerifyOTPView(View):
    
    def get(self, request):
        return render(request, "verify_otp.html")

    def post(self, request):
        entered_otp = request.POST.get('otp')

        session_otp = request.session.get('reset_otp')
        otp_time = request.session.get('otp_time')

        # OTP validity: 5 minutes
        if not session_otp or not otp_time:
            messages.error(request, "OTP expired. Try again.")
            return redirect('forgot-password')

        if time.time() - otp_time > 300:
            request.session.flush()
            messages.error(request, "OTP expired. Try again.")
            return redirect('forgot-password')

        if entered_otp != session_otp:
            messages.error(request, "Invalid OTP")
            return redirect('verify-otp')

        # OTP verified
        request.session['otp_verified'] = True
        messages.success(request, "OTP verified successfully.")
        return redirect('reset-password')

class ResetPasswordView(View):
    
    def get(self, request):
        if not request.session.get('otp_verified'):
            return redirect('forgot-password')

        return render(request, "reset_password.html")

    def post(self, request):
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect('reset-password')

        user_id = request.session.get('reset_user_id')
        user = CustomUser.objects.get(id=user_id)

        user.set_password(password1)
        user.save()

        # Clear session
        request.session.flush()

        messages.success(request, "Password reset successful.")
        return redirect('signin')

class VehicleAddView(LoginRequiredMixin,CreateView):
    login_url="signin"
    model = Vehicle

    form_class = VechicleRegistrationForm

    template_name = "vechicle_add.html"

    success_url = reverse_lazy("home")

    def form_valid(self,form):
        print(self.request.user)
        vehicle = form.save(commit=False)
        vehicle.user = self.request.user
        vehicle.save()
        return redirect(self.success_url)

class VehicleUpdateView(LoginRequiredMixin,UpdateView):
    login_url="signin"
    model = Vehicle
    form_class = VechicleRegistrationForm
    template_name = "vehicle_edit.html"
    success_url = reverse_lazy("listv")
    def get_queryset(self):
        return Vehicle.objects.filter(user=self.request.user)
    def get_success_url(self):
        return reverse("listv", kwargs={"pk": self.object.pk})
    
class VehicleListView(LoginRequiredMixin, ListView):
    login_url = "signin"
    model = Vehicle
    template_name = "vehicle_list.html"
    context_object_name = "vehicles"

    def get_queryset(self):
        return Vehicle.objects.filter(user=self.request.user)

class VehicleDeleteView(LoginRequiredMixin,DeleteView):
    login_url="signin"
    model = Vehicle
    template_name = "vehicle_delete_confirm.html"
    success_url = reverse_lazy("home")
    
class UserServiceListView(LoginRequiredMixin,ListView):
    login_url="signin"
    model = Service_Centre
    template_name = "userservicelist.html"
    context_object_name='vehicle'
    
class UserListProductView(LoginRequiredMixin,ListView):
    login_url="signin"
    model = Products
    template_name = 'userproductlist.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Products.objects.filter(service_centre_id=self.kwargs['service_centre_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service_centre_id'] = self.kwargs['service_centre_id']
        return context
    
class ServiceCreateView(LoginRequiredMixin,CreateView):
    login_url="signin"
    model = EVService
    form_class = EVservicerq
    template_name = 'service_request.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        obj.service_centre_id = self.kwargs['service_centre_id']
        obj.save()
        self.object = obj
        return super().form_valid(form)
    
class ServiceRquestList(LoginRequiredMixin, ListView):
    login_url = "signin"
    model = EVService
    template_name = 'service_requestlist.html'
    context_object_name = 'service'

    def get_queryset(self):
        # Return only services for the logged-in user
        return EVService.objects.filter(user=self.request.user).order_by('-created_at')
    
class ServiceUpdate(LoginRequiredMixin,UpdateView):
    login_url="signin"
    model = EVService
    form_class = EVservicerq
    template_name = "serviceupdate.html"
    success_url = reverse_lazy("servicerequest")
    def get_queryset(self):
            return EVService.objects.filter(user=self.request.user)
    def dispatch(self, request, *args, **kwargs):
        service = self.get_object()
        if service.status == "assigned":
            messages.error(request, "This service has already been assigned and cannot be updated.")
            return redirect("servicerequest", pk=service.pk)
        return super().dispatch(request, *args, **kwargs)
    def get_success_url(self):
        return reverse("servicerequest", kwargs={"pk": self.object.pk})
    
class ServiceDelete(LoginRequiredMixin,DeleteView):
    login_url="signin"
    model = EVService
    template_name = "servicedelete.html"
    success_url = reverse_lazy("home")
    def get_queryset(self):
        return EVService.objects.filter(user=self.request.user)
    def dispatch(self, request, *args, **kwargs):
        service = self.get_object()
        if service.status == "assigned":
            messages.error(request, "This service has already been assigned and cannot be updated.")
            return redirect("servicerequest", pk=service.pk)
        return super().dispatch(request, *args, **kwargs)

class ServicePaymentView(LoginRequiredMixin, View):
    login_url = 'signin'

    def get(self, request, service_id):
        # Fetch the service
        service = get_object_or_404(EVService, id=service_id, user=request.user)

        # Allow payment only if completed & not already paid
        if service.status != 'completed' or service.payment == 'completed':
            return HttpResponseForbidden("Payment not allowed")

        # Amount in paise for Razorpay
        amount = int(service.price * 100)

        # Create Razorpay order
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        razorpay_order = client.order.create({
            "amount": amount,
            "currency": "INR",
            "payment_capture": 1
        })

        # Create or get ServicePayment record
        payment, created = ServicePayment.objects.get_or_create(
            service=service,
            defaults={
                "user": request.user,
                "payment_method": "online",
                "amount": service.price,  # store in rupees
            }
        )

        payment.razorpay_order_id = razorpay_order["id"]
        payment.save()

        # Pass data to template
        context = {
            "service": service,
            "amount": service.price,
            "key_id": settings.RAZORPAY_KEY_ID,
            "order_id": razorpay_order["id"],
            "user_phone": getattr(request.user, "phone", ""),  # safe fallback
        }

        return render(request, "payment.html", context)

    def post(self, request, service_id):
        # Fetch service and payment
        service = get_object_or_404(EVService, id=service_id, user=request.user)
        payment = get_object_or_404(ServicePayment, service=service)

        # Update payment info from Razorpay
        payment.razorpay_payment_id = request.POST.get("razorpay_payment_id")
        payment.razorpay_signature = request.POST.get("razorpay_signature")
        payment.is_paid = True
        payment.payment_method = "online"
        payment.paid_at = timezone.now()
        payment.save()

        # Mark EVService as paid
        service.payment = 'completed'
        service.save()

        return redirect("home") 

class BuyProductView(LoginRequiredMixin, CreateView):
    login_url = 'signin'
    model = ProductOrder
    fields = ['quantity']
    template_name = 'buy_product.html'

    def dispatch(self, request, *args, **kwargs):
        self.product = get_object_or_404(Products, id=self.kwargs['product_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Save order first
        form.instance.user = self.request.user
        form.instance.product = self.product
        form.instance.service_centre = self.product.service_centre

        response = super().form_valid(form)  #  order saved here

        # Create Razorpay Order
        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        razorpay_order = client.order.create({
            "amount": int(self.object.total_amount * 100),  # paise
            "currency": "INR",
            "payment_capture": 1
        })

        # Save Razorpay order id
        self.object.razorpay_order_id = razorpay_order['id']
        self.object.save()

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.product
        return context

    def get_success_url(self):
        return reverse_lazy(
            'razorpay_checkout',
            kwargs={'order_id': self.object.id}
        )

def razorpay_checkout(request, order_id):
    order = get_object_or_404(ProductOrder, id=order_id)

    context = {
        'order': order,
        'razorpay_key': settings.RAZORPAY_KEY_ID,
        'amount': int(order.total_amount * 100),
    }
    return render(request, 'razorpay_checkout.html', context)

@csrf_exempt
def razorpay_verify(request, order_id):
    order = get_object_or_404(ProductOrder, id=order_id)

    order.razorpay_payment_id = request.GET.get('razorpay_payment_id')
    order.razorpay_signature = request.GET.get('razorpay_signature')

    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    try:
        client.utility.verify_payment_signature({
            'razorpay_order_id': order.razorpay_order_id,
            'razorpay_payment_id': order.razorpay_payment_id,
            'razorpay_signature': order.razorpay_signature
        })

        # ✅ Trigger signal
        order.payment_status = 'paid'
        order.save(update_fields=['payment_status', 'razorpay_payment_id', 'razorpay_signature'])

        return redirect('order_success', order_id=order.id)

    except:
        order.payment_status = 'failed'
        order.save(update_fields=['payment_status'])
        return redirect('payment_failed')

def order_success(request, order_id):
    order = get_object_or_404(ProductOrder, id=order_id)
    return render(request, 'order_success.html', {'order': order})

class BuyedProductList(LoginRequiredMixin,ListView):
    login_url = 'signin'
    model = ProductOrder
    template_name = 'buy_product_list.html'
    context_object_name = 'buyproduct'

    def get_queryset(self):
        return ProductOrder.objects.filter(user=self.request.user).order_by('-created_at')
    

class ListStations(LoginRequiredMixin, ListView):
    model = ChargingStations
    template_name = 'list_stations.html'
    context_object_name = 'stations'
    login_url = 'signin'

class StationSlotsView(DetailView):
    model = ChargingStations
    template_name = 'station_slots.html'
    context_object_name = 'station'

def release_expired_slot(slot):
    booking = SlotBooking.objects.filter(slot=slot).first()
    if booking:
        if timezone.now() > booking.booked_at + timedelta(hours=1):
            slot.is_booked = False
            slot.save()
            booking.delete()

@login_required
def book_slot(request, slot_id):
    slot = get_object_or_404(ChargingSlot, id=slot_id)

    release_expired_slot(slot)

    if slot.is_booked:
        messages.error(request, "Slot already booked!")
        return redirect(request.META.get('HTTP_REFERER'))

    slot.is_booked = True
    slot.save()

    SlotBooking.objects.create(
        user=request.user,
        slot=slot,
        payment_status=False
    )

    messages.success(request, "Slot booked! Proceed to payment.")
    return redirect('payment', slot.id)

@login_required
def cancel_slot(request, slot_id):
    slot = get_object_or_404(ChargingSlot, id=slot_id)

    booking = get_object_or_404(
        SlotBooking,
        slot=slot,
        user=request.user
    )

    slot.is_booked = False
    slot.save()
    booking.delete()

    return redirect('station_slots', pk=slot.station.id)

@login_required
def payment(request, slot_id):
    booking = get_object_or_404(SlotBooking, slot_id=slot_id, user=request.user)

    if request.method == "POST":
        booking.payment_status = True
        booking.save()
        messages.success(request, "Payment successful!")
        return redirect('u_station_li')

    return render(request, 'slot_payment.html', {'booking': booking})
