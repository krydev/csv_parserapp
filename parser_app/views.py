import csv
from datetime import datetime
from io import TextIOWrapper

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import FormView

from parser_app.forms import UploadFileForm
from parser_app.models import Variable

MB_FACTOR = 1 << 20


class UploaderView(LoginRequiredMixin, FormView):
    template_name = "upload.html"
    login_url = reverse_lazy('parser_app:login')
    form_class = UploadFileForm
    success_url = reverse_lazy('parser_app:results')
    extra_context = {'title': 'Uploader'}

    @method_decorator(transaction.atomic)
    def parse_and_save(self, file):
        encoded_f = TextIOWrapper(file, encoding='utf-8')
        csv_reader = csv.reader(encoded_f)
        header = next(csv_reader)
        # either not csv or corrupted
        if len(header) <= 1:
            raise ValidationError('Unrecognized format. Too few columns.')

        # retrieving field names corresponding to csv content
        non_displayable_fields = {'id', 'created_at', 'user'}
        field_names = [f.name for f in Variable._meta.get_fields()
                       if f.name not in non_displayable_fields]
        # fixating the timestamp for all new records
        transaction_time = datetime.utcnow()
        # If header is absent
        if header[0].lower() != 'variable' and header[1].lower() != 'd1':
            Variable.objects.create(
                **dict(zip(field_names, header)),
                created_at=transaction_time,
                user=self.request.user
            )
        for row in csv_reader:
            Variable.objects.create(
                **dict(zip(field_names, row)),
                created_at=transaction_time,
                user=self.request.user
            )

    def form_valid(self, form):
        file = self.request.FILES['file']
        # To avoid denial of service and overloading
        if file.size > 10 * MB_FACTOR:
            raise ValidationError('The file is too large. Max size is 10Mb.')
        self.parse_and_save(file)
        return super().form_valid(form)


@login_required
def results(request):
    current_user_records = Variable.objects.filter(user=request.user)
    latest_date = current_user_records.latest('created_at').created_at
    latest_records = current_user_records.filter(created_at=latest_date).values()
    print(latest_records)
    return HttpResponse(latest_records)
