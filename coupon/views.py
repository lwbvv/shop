from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Coupon
from .forms import AddCouponForm
from log import log

@require_POST
def add_coupon(request):
    now = timezone.now()
    log("쿠폰 add_coupon 시간", now)
    form = AddCouponForm(request.POST)
    log("쿠폰 add_coupon Form", form)
    log("쿠폰 add_coupon form.is_valid", form.is_valid())
    if form.is_valid():
        code = form.cleaned_data['code']

        try:
            coupon = Coupon.objects.get(code__iexact=code, use_from__lte=now, use_to__gte=now, active=True)
            request.session['coupon_id'] = coupon.id

        except Coupon.DoesNotExist as e:
            request.session['coupon_id'] = None
        log("쿠폰 add_coupon 쿠폰 세션", request.session['coupon_id'])
    return redirect('cart:detail')
