from django import forms


class ZipFileForm(forms.Form):
    docfile = forms.FileField(label='Select a file', help_text='max. 10 megabytes')
    file_name = forms.TextInput()
    language = forms.TextInput()
