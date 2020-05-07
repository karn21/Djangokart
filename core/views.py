from django.shortcuts import render, get_object_or_404, redirect
from .models import Item, OrderItem, Order, ShippingAddress, Payment, Coupon, Refund
from django.views.generic import ListView, DetailView, View
from django.utils import timezone
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from .forms import CheckoutForm, CouponForm, RefundForm
import stripe
from django.conf import settings
import random
import string


def create_order_id():
    order_id = "".join(random.choices(
        string.ascii_uppercase + string.digits, k=20))
    order_qs = Order.objects.filter(order_id=order_id)
    if order_qs.exists():
        return create_order_id()
    else:
        return order_id


def is_valid_form(values):
    for value in values:
        if value == '':
            return False
    return True


class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
        except:
            messages.warning(self.request, 'You do not have an active Order.')
            return redirect('core:cart')
        form = CheckoutForm()
        coupon_form = CouponForm()
        context = {
            'order': order,
            'form': form,
            'coupon_form': coupon_form
        }
        address_qs = ShippingAddress.objects.filter(
            user=self.request.user, default=True)
        if address_qs.exists():
            context.update({'shipping_address': address_qs[0]})
        return render(self.request, 'checkout-page.html', context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
        except:
            messages.info(self.request, "You do not have any active orders.")
            return redirect('core:checkout')
        if form.is_valid():
            use_default = form.cleaned_data.get('use_default')
            payment_method = form.cleaned_data['payment_method']
            if use_default:
                address_qs = ShippingAddress.objects.filter(
                    user=self.request.user, default=True)
                if address_qs.exists():
                    shipping_address = address_qs[0]
                else:
                    messages.info(
                        self.request, 'You do not have any default Address.')
                    return redirect(".")
            else:
                street_address = form.cleaned_data['street_address']
                apartment_address = form.cleaned_data['apartment_address']
                country = form.cleaned_data['country']
                zip = form.cleaned_data['zip']
                save_address = form.cleaned_data['save_address']
                if is_valid_form([street_address, country, zip]):
                    shipping_address = ShippingAddress(
                        user=self.request.user,
                        street_address=street_address,
                        apartment_address=apartment_address,
                        country=country,
                        zip=zip,
                    )
                    shipping_address.save()
                    if save_address:
                        shipping_address.default = True
                        shipping_address.save()
                        address_qs = ShippingAddress.objects.filter(
                            user=self.request.user, default=True)
                        if address_qs.exists():
                            old_address = address_qs[0]
                            old_address.default = False
                            old_address.save()
                else:
                    messages.warning(
                        self.request, 'Fill in the necessary fields.')
                    return redirect('.')
            order.shipping_address = shipping_address
            order_id = create_order_id()
            order.order_id = order_id
            order.save()
            if payment_method == 'S':
                return redirect('core:payment_stripe')
            elif payment_method == 'P':
                return redirect('core:checkout')
            else:
                messages.info(self.request.user, 'Inavlid Payment Method')
                return redirect('core:home')
        else:
            messages.warning(self.request, "Check the form for errors")
            return redirect('core:checkout')


class StripePaymentView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
        except:
            messages.info(self.request, 'You do not have any active order.')
            return redirect("core:home")
        if order.shipping_address:
            context = {
                'order': order
            }
            return render(self.request, 'payment-stripe.html', context)
        else:
            messages.warning(
                self.request, "You have not added a Shipping Address.")
            return redirect('core:checkout')

    def post(self, *args, **kwargs):

        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            stripe.api_key = settings.STRIPE_PUBLIC_KEY
            token = self.request.POST.get('stripeToken')
            charge = stripe.Charge.create(
                amount=int(order.get_final_total()*100),
                currency="inr",
                source=token,
                description="My First Test Charge (created for API docs)",
            )
            payment = Payment()
            payment.payment_id = charge.id
            payment.user = self.request.user
            payment.save()

            order.payment = payment
            order.amount = order.get_final_total()
            order.ordered = True
            order.save()
            messages.success(self.request, "Your Payment was successful!")
            return redirect('core:home')

        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            messages.warning(
                self.request, f'Error - {e.error.code} { e.error.message }')
            return redirect('core:checkout')
        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.warning(self.request, "Too many requests")
            return redirect('core:checkout')
        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            messages.warning(self.request, "Invalid Parameters")
            return redirect('core:checkout')
        except stripe.error.AuthenticationError as e:
            messages.warning(self.request, "Authentication Failed")
            return redirect('core:checkout')
        except stripe.error.APIConnectionError as e:
            messages.warning(self.request, "Network Error")
            return redirect('core:checkout')
        except stripe.error.StripeError as e:
            messages.warning(
                self.request, "Error Occured!! We have been informed")
            return redirect('core:checkout')
        except Exception as e:
            messages.warning(self.request, "Error Occured!! Try Again")
            return redirect('core:checkout')


class HomeView(ListView):
    paginate_by = 10
    template_name = 'home-page.html'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query is not None:
            queryset = Item.objects.filter(
                Q(title__icontains=query) | Q(description__icontains=query))
        else:
            queryset = Item.objects.all()
        return queryset


class ItemDetailView(DetailView):
    model = Item
    template_name = 'product-page.html'


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'order': order
            }
            return render(self.request, 'cart.html', context)
        except:
            messages.info(self.request, "Your cart is empty!")
            return redirect('core:home')


@login_required
def add_to_cart(request, slug):
    user = request.user
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        try:
            order_item = order.items.get(item__slug=slug)
        except:
            order_item = None
        if order_item:
            order_item.quantity += 1
            order_item.save()
            messages.info(request, 'This item was updated in your cart.')
        else:
            order_item = OrderItem.objects.create(item=item)
            order.items.add(order_item)
            messages.info(request, 'This item was added to your cart.')
    else:
        ordered_date = timezone.now()
        order_item = OrderItem.objects.create(item=item)
        order = Order.objects.create(
            user=user, ordered_date=ordered_date, amount=0)
        order.items.add(order_item)
        messages.info(request, 'This item was added to your cart.')
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def remove_from_cart(request, slug):
    user = request.user
    order_qs = Order.objects.filter(user=user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        try:
            order_item = order.items.get(item__slug=slug)
        except:
            order_item = None
        if order_item:
            order.items.remove(order_item)
            messages.info(request, 'This item was removed from your cart.')
            return redirect(request.META.get('HTTP_REFERER', '/'))
        else:
            messages.info(request, 'You do not have this item in your cart.')
            return redirect(request.META.get('HTTP_REFERER', '/'))
    else:
        messages.info(request, 'You do not have an active order.')
        return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def decrease_cart(request, slug):
    user = request.user
    order_qs = Order.objects.filter(user=user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        try:
            order_item = order.items.get(item__slug=slug)
        except:
            order_item = None
        if order_item:
            if order_item.quantity == 1:
                order.items.remove(order_item)
                messages.info(request, 'This item was removed from your cart.')
                return redirect(request.META.get('HTTP_REFERER', '/'))
            else:
                order_item.quantity -= 1
                order_item.save()
                messages.info(request, 'This item was updated in your cart.')
                return redirect(request.META.get('HTTP_REFERER', '/'))
        else:
            messages.info(request, 'You do not have this item in your cart.')
            return redirect(request.META.get('HTTP_REFERER', '/'))
    else:
        messages.info(request, 'You do not have an active order.')
        return redirect(request.META.get('HTTP_REFERER', '/'))


class CouponApply(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST)
        if form.is_valid():
            code = form.cleaned_data.get('code')
            try:
                coupon = Coupon.objects.get(code=code)
            except:
                messages.info(self.request, 'Coupon is not valid.')
                return redirect('core:checkout')
            try:
                order = Order.objects.get(
                    user=self.request.user, ordered=False)
            except:
                messages.info(self.request, 'You do not have an active order.')
                return redirect('core:cart')
            order.coupon = coupon
            order.save()
            messages.success(self.request, 'Coupon applied.')
        return redirect("core:checkout")


def coupon_remove(request):
    try:
        order = Order.objects.get(
            user=request.user, ordered=False)
    except:
        messages.info(request, 'You do not have an active order.')
        return redirect('core:cart')
    order.coupon = None
    order.save()
    messages.info(request, 'Coupon removed.')
    return redirect('core:checkout')


class RefundRequest(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, 'request_refund.html', context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST or None)
        if form.is_valid():
            order_id = form.cleaned_data.get('order_id')
            try:
                order = Order.objects.get(order_id=order_id)
            except:
                messages.warning(self.request, 'The Order does not exist.')
                return redirect(".")
            refund = Refund()
            refund.user = self.request.user
            refund.order = order
            refund.amount = order.get_final_total()
            refund.message = form.cleaned_data.get('message')
            refund.email = form.cleaned_data.get('email')
            refund.save()
            order.refund_requested = True
            order.save()
            messages.success(
                self.request, 'We have received your refund request.')
            return redirect("core:home")
