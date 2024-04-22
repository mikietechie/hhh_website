from django import forms


class SignInUpForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(required=False)
    hasaccount = forms.BooleanField(required=False)

