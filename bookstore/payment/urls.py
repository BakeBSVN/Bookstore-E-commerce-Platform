from django.urls import path
from .views import BraintreePaymentProcessView, VNPayPaymentProcessView, PaymentDoneView, PaymentCanceledView, vnpay_return

urlpatterns = [
    path('process/paypal/', BraintreePaymentProcessView.as_view(), name='paypal_process'),
    path('process/vnpay/', VNPayPaymentProcessView.as_view(), name='vnpay_process'),
    path('done/', PaymentDoneView.as_view(), name='done'),
    path('canceled/', PaymentCanceledView.as_view(), name='canceled'),
    path('payment_return/', vnpay_return, name='vnpay_return'),
]

# urlpatterns = [
#     path('process/', views.payment_process, name='process'),
#     path('done/', views.payment_done, name='done'),
#     path('canceled/', views.payment_canceled, name='canceled'),
# ]
