from django.shortcuts import render,redirect,get_object_or_404
from django.urls import reverse_lazy,reverse
from decimal import Decimal, InvalidOperation
from django.views.generic import CreateView,ListView,UpdateView,DeleteView,View
from django.contrib import messages
from service_app.forms import *
from service_app.models import *
from user_app.models import *
from django.contrib.auth.decorators import login_required
import random
from django.core.mail import send_mail
from django.conf import settings

# Create your views here.

class ServicecenterView(CreateView):
    model = Service_Centre
    form_class = ServiceCenterForm
    template_name = "service_add.html"
    success_url = reverse_lazy("servicelist")


class ServiceListView(ListView):
    model = Service_Centre
    template_name = "servicelist.html"
    context_object_name='vehicle'
    
class ServicecenterUpdate(UpdateView):
    model = Service_Centre
    form_class = ServiceCenterForm
    template_name = 'serviceupdate.html'
    success_url = reverse_lazy("servicelist")

class ServicecenterDelete(DeleteView):
    model = Service_Centre
    template_name = 'delete.html'
    success_url = reverse_lazy("Servicelist")

class CreateProduct(CreateView):
    model = Products
    form_class = CreateProduct
    template_name = 'productadd.html'
    success_url = reverse_lazy("productlist")
    def form_valid(self, form):
        form.instance.service_centre_id = self.kwargs['service_centre_id']
        return super().form_valid(form)
    def get_success_url(self):
        # Dynamically pass service_centre_id to the product list
        return reverse('productlist', kwargs={
            'service_centre_id': self.kwargs['service_centre_id']
        })
    
class ListProductView(ListView):
    model = Products
    template_name = 'productlist.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Products.objects.filter(service_centre_id=self.kwargs['service_centre_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service_centre_id'] = self.kwargs['service_centre_id']
        return context
    
class UpdateProduct(UpdateView):
    model = Products
    fields = ['name', 'description', 'price', 'quantity', 'image']  # form fields
    template_name = 'productupdate.html'

    def get_success_url(self):
        return reverse('productlist', kwargs={
            'service_centre_id': self.object.service_centre_id
        })
    
class DeleteProduct(DeleteView):
    model = Products
    template_name = 'productdelete.html'

    def get_success_url(self):
        return reverse('productlist', kwargs={
            'service_centre_id': self.object.service_centre_id
        })
    
class ServiceRquestInCenter(ListView):
    model = EVService
    template_name = "servicelist_center.html"
    context_object_name = "servicerq"
    def get_queryset(self):
        return EVService.objects.filter(service_centre_id=self.kwargs['service_centre_id'])
    

class ServiceCenterInlineUpdate(View):
    
    def post(self, request, pk):
        service = get_object_or_404(EVService, pk=pk)

        # Lock completed services
        if service.status == "completed":
            messages.error(request, "Completed service cannot be modified.")
            return redirect(
                "ServiceRquestInCenter",  # Matches your URL name exactly
                service_centre_id=service.service_centre.id
            )

        # Handle price safely
        price = request.POST.get("price")
        if price:
            try:
                service.price = Decimal(price)
            except InvalidOperation:
                messages.error(request, "Invalid price value.")
                return redirect(
                    "ServiceRquestInCenter",
                    service_centre_id=service.service_centre.id
                )
        else:
            service.price = None

        # Status update
        service.status = request.POST.get("status")
        service.save()

        messages.success(request, "Service updated successfully.")
        return redirect(
            "ServiceRquestInCenter",
            service_centre_id=service.service_centre.id
        )
    
class BuyedProductseviceList(ListView):
    model = ProductOrder
    template_name = 'service_buy_product_list.html'
    context_object_name = 'buyproduct'

    def get_queryset(self):
        return ProductOrder.objects.filter(service_centre_id=self.kwargs['service_centre_id']).order_by("-created_at")
    
@login_required
def send_order_otp(request, order_id):
    order = get_object_or_404(ProductOrder, id=order_id)

    # Generate 4-digit OTP
    otp = str(random.randint(1000, 9999))

    # Store OTP and order_id in session
    request.session['otp_order_id'] = order.id
    request.session['otp_code'] = otp

    # Optional: set expiration time for session OTP (e.g., 5 minutes)
    request.session.set_expiry(300)  # 300 seconds = 5 minutes

    # Send OTP email to user
    send_mail(
        subject=f"Confirm your order '{order.product.name}'",
        message=f"Your OTP is {otp}",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[order.user.email],
        fail_silently=False,
    )

    # Redirect to OTP confirmation page
    return redirect('confirm_order_otp', order_id=order.id)

@login_required
def confirm_order_otp(request,order_id):
    otp_entered = None
    order = None

    # Retrieve OTP and order_id from session
    otp_code = request.session.get('otp_code')
    order_id = request.session.get('otp_order_id')

    if order_id:
        order = get_object_or_404(ProductOrder, id=order_id)
    else:
        messages.error(request, "No OTP found. Please try again.")
        return redirect('service_orders', service_centre_id=request.user.service_centre.id)

    if request.method == "POST":
        otp_entered = request.POST.get('otp')

        if otp_entered == otp_code:
            order.order_status = 'received'
            order.save()

            # Clear OTP from session
            request.session.pop('otp_code')
            request.session.pop('otp_order_id')

            messages.success(request, "Order confirmed successfully!")
            return redirect('service_orders', service_centre_id=order.service_centre.id)
        else:
            messages.error(request, "Invalid OTP. Please try again.")

    return render(request, 'confirm_order_otp.html', {'order': order})
