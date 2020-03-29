from django.shortcuts import render, get_object_or_404
from .models import *
from cart.cart import Cart
from .forms import *

from log import log

def order_create(request):
    cart = Cart(request)

    if request.method == "POST":
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()

            if cart.coupon:
                order.coupon = cart.coupon
                order.discount = cart.coupon.amount
                order.save()

            for item in cart:
                OrderItem.objects.create(order=order, product=item['product'], price=item['price'], quantity=item['quantity'])

            cart.clear()

            return render(request, 'order/created.html', {'order': order})

    else:
        form = OrderCreateForm()
    return render(request, 'order/create.html', {'cart': cart, 'form': form})


def order_complete(request):
    order_id = request.GET.get('order_id')
    order = Order.objects.get(id=order_id)
    return render(request, 'order/created.html', {'order':order})


from django.views.generic.base import View
from django.http import JsonResponse

class OrderCreateAjaxView(View):
    def post(self, request, *args, **kwargs):

        log("OrderCreateAjaxView post request",request)

        if not request.user.is_authenticated:
            return JsonResponse({"authentication":False}, status=403)


        cart = Cart(request)
        form = OrderCreateForm(request.POST)

        if form.is_valid():
            order = form.save(commit=False)
            if cart.coupon:
                order.coupon = cart.coupon
                order.discount = cart.coupon.amount #쿠폰 디비에서 할인가 불러오기
            order = form.save()

            for item in cart:
                OrderItem.objects.create(order=order, product=item['product'], \
                price=item['price'], quantity=item['quantity'])

            cart.clear()

            data = {
                "order_id": order.id
            }

            return JsonResponse(data)
        else:
            return JsonResponse({}, status=401)


class OrderCheckoutAjaxView(View):
    def post(self, request, *args, **kwargs):

        log("OrderCheckoutAjaxView post request.user.is_authenticated: ",request.user.is_authenticated )
        if not request.user.is_authenticated:
            return JsonResponse({"authenticated": False}, status=403)

        order_id = request.POST.get('order_id')
        order = Order.objects.get(id=order_id)
        amount = request.POST.get('amount')

        log("OrderCheckoutAjaxView post order_id: ",order_id )
        log("OrderCheckoutAjaxView post order: ",order )
        log("OrderCheckoutAjaxView post amount: ",amount )

        try:
            merchant_order_id = OrderTransaction.objects.create_new(order = order, amount = amount)
        except :
            merchant_order_id = None

        log("OrderCheckoutAjaxView post merchant_order_id: ",merchant_order_id )
        if merchant_order_id is not None:
            data = {
                "works": True,
                "merchant_id": merchant_order_id
            }
            return JsonResponse(data)

        else:
            return JsonResponse({}, status=401)



#실제 결제가 끝난 뒤에 결제를 검증하는 뷰
class OrderImpAjaxView(View):
    def post(self, request, *args, **kwargs):

        log("OrderImpAjaxView post request.user.is_authenticated: ",request.user.is_authenticated )

        if not request.user.is_authenticated:
            return JsonResponse({"authenticated": False}, status=403)

        order_id = request.POST.get('order_id')
        log("OrderImpAjaxView post order_id: ",order_id )
        order = get_object_or_404(Order,id=order_id)
        log("OrderImpAjaxView post order: ",order )
        merchant_id = request.POST.get('merchant_id')
        log("OrderImpAjaxView post merchant_id: ",merchant_id )
        imp_id = request.POST.get('imp_id')
        log("OrderImpAjaxView post imp_id: ",imp_id )
        amount = request.POST.get('amount')
        log("OrderImpAjaxView post amount: ",amount )

        try:
            trans = OrderTransaction.objects.get(
                order=order,
                merchant_order_id = merchant_id,
                amount = amount
            )
        except :
            trans = None
        log("OrderImpAjaxView post trans: ",trans )
        if trans is not None:
            trans.transaction_id = imp_id
            log("OrderImpAjaxView post trans.transaction_id: ",trans.transaction_id )
            trans.success = True
            log("OrderImpAjaxView post trans.success: ",trans.success )
            trans.save()
            order.paid = True
            log("OrderImpAjaxView post order.paid: ",order.paid )
            order.save()

            data = {
                "works":True
            }

            return JsonResponse(data)

        else:
            return JsonResponse({}, status=401)
