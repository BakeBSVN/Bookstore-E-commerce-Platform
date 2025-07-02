import braintree
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.views import View
from orders.models import Order
from cart.cart import Cart
from .forms import PaymentForm
from .vnpay import vnpay
from datetime import datetime
from django.http import JsonResponse

gateway = braintree.BraintreeGateway(settings.BRAINTREE_CONF)


class BasePaymentProcessView(View):
    payment_method = None
    template_name = None

    def get_order(self, request):
        order_id = request.session.get('order_id')
        return get_object_or_404(Order, id=order_id)

    def handle_payment(self, request, order, total_cost):
        raise NotImplementedError("Subclasses must implement this method")

    def get(self, request, *args, **kwargs):
        order = self.get_order(request)
        client_token = gateway.client_token.generate()
        return render(request, self.template_name, {'order': order, 'client_token': client_token})

    def post(self, request, *args, **kwargs):
        order = self.get_order(request)
        cart = Cart(request)
        total_cost = order.get_total_cost()
        result = self.handle_payment(request, order, total_cost)

        if result.get('is_success'):
            if 'payment_url' in result:
                return redirect(result['payment_url'])
            order.paid = True
            order.transaction_id = result.get('transaction_id', None)
            order.save()
            cart.clear()
            return redirect('done')
        else:
            return redirect('canceled')


class BraintreePaymentProcessView(BasePaymentProcessView):
    payment_method = 'braintree'
    template_name = 'payment/process_paypal.html'

    def handle_payment(self, request, order, total_cost):
        nonce = request.POST.get('payment_method_nonce', None)
        result = gateway.transaction.sale({
            'amount': f'{total_cost:.2f}',
            'payment_method_nonce': nonce,
            'options': {'submit_for_settlement': True}
        })
        return {
            'is_success': result.is_success,
            'transaction_id': result.transaction.id if result.is_success else None
        }


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class VNPayPaymentProcessView(BasePaymentProcessView):
    payment_method = 'vnpay'
    template_name = 'vnpay/process_vnpay.html'

    def handle_payment(self, request, order, total_cost):
        form = PaymentForm(request.POST)
        if form.is_valid():
            order_type = form.cleaned_data['order_type']
            order_id = form.cleaned_data['order_id']
            amount = form.cleaned_data['amount']
            order_desc = form.cleaned_data['order_desc']
            bank_code = form.cleaned_data['bank_code']
            language = form.cleaned_data['language']
            ipaddr = get_client_ip(request)
            # Build URL Payment
            vnp = vnpay()
            vnp.requestData['vnp_Version'] = '2.1.0'
            vnp.requestData['vnp_Command'] = 'pay'
            vnp.requestData['vnp_TmnCode'] = settings.VNPAY_TMN_CODE
            vnp.requestData['vnp_Amount'] = amount * 100
            vnp.requestData['vnp_CurrCode'] = 'VND'
            vnp.requestData['vnp_TxnRef'] = order_id
            vnp.requestData['vnp_OrderInfo'] = order_desc
            vnp.requestData['vnp_OrderType'] = order_type
            if language and language != '':
                vnp.requestData['vnp_Locale'] = language
            else:
                vnp.requestData['vnp_Locale'] = 'vn'
            if bank_code and bank_code != "":
                vnp.requestData['vnp_BankCode'] = bank_code

            vnp.requestData['vnp_CreateDate'] = datetime.now().strftime('%Y%m%d%H%M%S')
            vnp.requestData['vnp_IpAddr'] = ipaddr
            vnp.requestData['vnp_ReturnUrl'] = settings.VNPAY_RETURN_URL
            vnpay_payment_url = vnp.get_payment_url(settings.VNPAY_PAYMENT_URL, settings.VNPAY_HASH_SECRET_KEY)
            print(vnpay_payment_url)
            return {
                'is_success': True,
                'payment_url': vnpay_payment_url
            }
        else:
            return {
                'is_success': False,
                'transaction_id': None
            }

    def get(self, request, *args, **kwargs):
        order = self.get_order(request)
        return render(request, self.template_name, {'order': order})


class PaymentDoneView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'payment/done.html')


class PaymentCanceledView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'payment/canceled.html')


def payment_ipn(request):
    inputData = request.GET
    if inputData:
        vnp = vnpay()
        vnp.responseData = inputData.dict()
        order_id = inputData['vnp_TxnRef']
        amount = inputData['vnp_Amount']
        order_desc = inputData['vnp_OrderInfo']
        vnp_TransactionNo = inputData['vnp_TransactionNo']
        vnp_ResponseCode = inputData['vnp_ResponseCode']
        vnp_TmnCode = inputData['vnp_TmnCode']
        vnp_PayDate = inputData['vnp_PayDate']
        vnp_BankCode = inputData['vnp_BankCode']
        vnp_CardType = inputData['vnp_CardType']
        if vnp.validate_response(settings.VNPAY_HASH_SECRET_KEY):
            # Check & Update Order Status in your Database
            # Your code here
            firstTimeUpdate = True
            totalamount = True
            if totalamount:
                if firstTimeUpdate:
                    if vnp_ResponseCode == '00':
                        print('Payment Success. Your code implement here')
                    else:
                        print('Payment Error. Your code implement here')

                    # Return VNPAY: Merchant update success
                    result = JsonResponse({'RspCode': '00', 'Message': 'Confirm Success'})
                else:
                    # Already Update
                    result = JsonResponse({'RspCode': '02', 'Message': 'Order Already Update'})
            else:
                # invalid amount
                result = JsonResponse({'RspCode': '04', 'Message': 'invalid amount'})
        else:
            # Invalid Signature
            result = JsonResponse({'RspCode': '97', 'Message': 'Invalid Signature'})
    else:
        result = JsonResponse({'RspCode': '99', 'Message': 'Invalid request'})

    return result


#

def vnpay_return(request):
    inputData = request.GET
    if inputData:
        vnp = vnpay()
        vnp.responseData = inputData.dict()
        order_id = inputData['vnp_TxnRef']
        amount = int(inputData['vnp_Amount']) / 100
        order_desc = inputData['vnp_OrderInfo']
        vnp_TransactionNo = inputData['vnp_TransactionNo']
        vnp_ResponseCode = inputData['vnp_ResponseCode']
        vnp_TmnCode = inputData['vnp_TmnCode']
        vnp_PayDate = inputData['vnp_PayDate']
        vnp_BankCode = inputData['vnp_BankCode']
        vnp_CardType = inputData['vnp_CardType']

        if vnp.validate_response(settings.VNPAY_HASH_SECRET_KEY):
            if vnp_ResponseCode == "00":
                order = get_object_or_404(Order, id=order_id)
                order.paid = True
                order.save()
                return render(request, "payment/payment_return.html", {"title": "Kết quả thanh toán",
                                                                       "result": "Thành công", "order_id": order_id,
                                                                       "amount": amount,
                                                                       "order_desc": order_desc,
                                                                       "vnp_TransactionNo": vnp_TransactionNo,
                                                                       "vnp_ResponseCode": vnp_ResponseCode})
            else:
                return render(request, "payment/payment_return.html", {"title": "Kết quả thanh toán",
                                                                       "result": "Lỗi", "order_id": order_id,
                                                                       "amount": amount,
                                                                       "order_desc": order_desc,
                                                                       "vnp_TransactionNo": vnp_TransactionNo,
                                                                       "vnp_ResponseCode": vnp_ResponseCode})
        else:
            return render(request, "payment/payment_return.html",
                          {"title": "Kết quả thanh toán", "result": "Lỗi", "order_id": order_id, "amount": amount,
                           "order_desc": order_desc, "vnp_TransactionNo": vnp_TransactionNo,
                           "vnp_ResponseCode": vnp_ResponseCode, "msg": "Sai checksum"})
    else:
        return render(request, "payment/payment_return.html", {"title": "Kết quả thanh toán", "result": ""})
