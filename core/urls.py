from django.urls import path
from . import views
app_name = 'core'


urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('cart/', views.OrderSummaryView.as_view(), name='cart'),
    path('product/<slug>/', views.ItemDetailView.as_view(), name='product_detail'),
    path('add_to_cart/<slug>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<slug>/',
         views.remove_from_cart, name='remove_from_cart'),
    path('decrease_cart/<slug>/', views.decrease_cart, name='decrease_cart'),
    path('payment/stripe/', views.StripePaymentView.as_view(), name='payment_stripe'),
    path('coupon/apply/', views.CouponApply.as_view(), name='coupon_apply'),
    path('coupon/remove/', views.coupon_remove, name='coupon_remove'),
    path('refund_apply/', views.RefundRequest.as_view(), name='refund_request'),
]
