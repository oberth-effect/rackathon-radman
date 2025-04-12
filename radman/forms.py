from django import forms


class StyledModelForm(forms.ModelForm):
    error_css_class = 'border-red-500 text-red-600'
    required_css_class = 'border-blue-500'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'border border-gray-300 rounded p-2'})


