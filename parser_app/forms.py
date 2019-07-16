from django.forms import Form, FileField, FileInput


class UploadFileForm(Form):
    file = FileField(label='Upload a csv file to parse.\n' +
                           'Max size is 10Mb',
                     widget=FileInput(attrs={'accept': '.csv'}))
