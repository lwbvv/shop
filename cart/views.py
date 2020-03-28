from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from shop.models import Product
from .forms import AddProductForm
from .cart import Cart

from coupon.forms import AddCouponForm

@require_POST
def add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)


    form = AddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product=product, quantity=cd['quantity'], is_update=cd['is_update'])

        return redirect('cart:detail')




def remove(request, product_id):
    #리퀘스트 값을 카트 객체 생성
    cart = Cart(request)
    #상품의 아이디 값으로 해당 상품이 있는지 조회
    product = get_object_or_404(Product, id=product_id)
    #카트의 세션 삭제
    cart.remove(product)
    return redirect('cart:detail')

def detail(request):
    cart = Cart(request)
    add_coupon = AddCouponForm()
    #카트 객체로부터 노출 시킬 제품을 가져옴. 제품 수량을 수정하기 위해 AddProductForm을 제품마다 하나씩 추가
    for product in cart:
        product['quantity_form'] = AddProductForm(initial = {'quantity':product['quantity'], 'is_update':True})

        return render(request, 'cart/detail.html', {'cart': cart, 'add_coupon': add_coupon}) #템플릿 변수로 카트와 쿠폰 전달
