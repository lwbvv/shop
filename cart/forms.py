from django import forms

class AddProductForm(forms.Form):
     # 상품 수량 설정 field
    quantity = forms.IntegerField()
     # 수정 여부 확인 field
    is_update = forms.BooleanField(required = False, initial=False, widget=forms.HiddenInput)
