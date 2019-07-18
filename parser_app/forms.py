import magic

from django.forms import Form, FileField, FileInput, ValidationError
from django.utils.safestring import mark_safe

from csv_parser.settings import MAX_UPLOAD_SIZE, MIME_UPLOAD_TYPE, FILE_UPLOAD_TYPE

MB_FACTOR = 1 << 20


class UploadFileForm(Form):
    file = FileField(label=mark_safe('Upload a csv file to parse. '
                           f'Max size is {MAX_UPLOAD_SIZE}Mb'),
                     widget=FileInput(attrs={'accept': '.csv'}))

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if not file:
            raise ValidationError('No file was uploaded.')
        file_type = magic.from_buffer(file.read(), mime=True)
        file.seek(0)
        print(file_type)
        # Checking if text file
        if MIME_UPLOAD_TYPE != file_type:
            raise ValidationError('Invalid file format. '
                                  f'Should be {FILE_UPLOAD_TYPE}.')
        if file.size > MAX_UPLOAD_SIZE * MB_FACTOR:
            raise ValidationError('The file is too large. '
                                  f'Max size is {MAX_UPLOAD_SIZE}Mb.')
        return file
