from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from shop.models import Product
from .forms import AddProductForm
from .cart import Cart

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

# Create your views here.
