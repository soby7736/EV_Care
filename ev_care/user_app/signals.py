from django.db.models.signals import post_save
from django.dispatch import receiver
from user_app.models import *
from django.core.mail import send_mail
from django.conf import settings
import random


@receiver(post_save,sender = CustomUser)
def send_register_mail(sender,instance,created,**kwargs):
    if created:
        subject = "Welcome to EV-care"
        message = ("Thank you for registering with EV-Care!\n\n"
            "EV-Care is your one-stop solution for:\n"
            "• Electric vehicle services\n"
            "• Charging station booking\n"
            "• Buying EV accessories and products\n\n"
            "We’re happy to have you with us!")
        from_email = settings.EMAIL_HOST_USER 
        recipient_list = [instance.email]
        send_mail(subject=subject,message=message,from_email = from_email,recipient_list=recipient_list,fail_silently=True)
        print("mail sent")



@receiver(post_save, sender=ProductOrder)
def send_product_order_receipt(sender, instance, created, **kwargs):
    """
    Send email receipt when payment is successful
    """

    # Only send email when payment is marked as PAID
    if instance.payment_status == 'paid':

        subject = "Payment Receipt - Product Purchase"

        message = f"""
Hi {instance.user.first_name},

Thank you for your purchase! 🎉

Here are your order details:

Product Name: {instance.product.name}
Quantity: {instance.quantity}
Total Amount: ₹{instance.total_amount}

Payment Status: PAID
Order ID: {instance.id}
Razorpay Payment ID: {instance.razorpay_payment_id}

Service Centre:
{instance.service_centre.name}

We hope to serve you again!

Regards,
EV Care Team
"""

        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [instance.user.email],
            fail_silently=False,
        )

