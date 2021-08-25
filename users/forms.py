from django import forms


"""A multi-purpose confirmation form."""


class ConfirmationForm(forms.Form):
    model = forms.CharField(
        label="Model", max_length=100, required=False, empty_value=None
    )
    application = forms.CharField(
        label="Application", max_length=100, required=False, empty_value=None
    )
