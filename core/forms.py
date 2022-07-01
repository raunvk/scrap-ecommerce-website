from django import forms
from core.models import*

class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'price', 'quantity', 'address', 'city', 'zip_code', 'phone', 'image']
        widgets = {
            'name' : forms.TextInput(attrs={'class':'form-control'}),
            'category' : forms.Select(attrs={'class':'form-control'}),
            'description' : forms.TextInput(attrs={'class':'form-control'}),
            'price' : forms.NumberInput(attrs={'class':'form-control'}),
            'quantity' : forms.NumberInput(attrs={'class':'form-control'}),
            'address' : forms.TextInput(attrs={'class':'form-control'}),
            'city' : forms.TextInput(attrs={'class':'form-control'}),
            'zip_code' : forms.TextInput(attrs={'class':'form-control'}),
            'phone' : forms.TextInput(attrs={'class':'form-control'}),
            'image' : forms.FileInput(attrs={'class':'form-control'}),
        }



class CheckoutForm(forms.Form):

    
    address = forms.CharField(widget=forms.TextInput(attrs={
        'class' : 'form-control',
    }))

    city = forms.CharField(widget=forms.TextInput(attrs={
        'class' : 'form-control',
    }))

    zip_code = forms.CharField(widget=forms.TextInput(attrs={
        'class' : 'form-control',
    }))