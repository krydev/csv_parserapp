import csv
import string
import random
from io import TextIOWrapper

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.db import transaction
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import FormView, TemplateView
from django.utils import timezone

from parser_app.forms import UploadFileForm
from parser_app.models import Variable


def _generate_rand_unique_str(str_len):
    source_chars = string.ascii_letters + string.digits + string.punctuation
    return random.sample(source_chars, str_len)


def _get_relevant_fields(exclude_fields, model=Variable):
    return [f.name for f in model._meta.get_fields()
            if f.name not in exclude_fields]


def _group_transform_data(rows):
    alpha_a, alpha_b = [], []
    field_names = _get_relevant_fields(
        exclude_fields={'id', 'created_at', 'user', 'name'}
    )
    for row in rows:
        if row['name'][-1].lower() == 'a':
            values = [row[field] if row[field] != '0' else '9'
                      for field in field_names]
            alpha_a.append(values)
        else:
            values = [row[field] if row[field] in string.ascii_letters else ''
                      for field in field_names]
            alpha_b.append(values)
    return alpha_a, alpha_b, [_generate_rand_unique_str(len(field_names))]


class UploaderView(LoginRequiredMixin, FormView):
    template_name = 'upload.html'
    login_url = reverse_lazy('parser_app:login')
    form_class = UploadFileForm
    success_url = reverse_lazy('parser_app:results')
    extra_context = {'title': 'Uploader'}

    @method_decorator(transaction.atomic)
    def _parse_and_save(self, file):
        encoded_f = TextIOWrapper(file, encoding='utf-8')
        csv_reader = csv.reader(encoded_f)
        header = next(csv_reader)
        # checking if indeed csv
        if len(header) <= 1:
            raise ValidationError('Unrecognized format. Too few columns.')

        # retrieving field names corresponding to csv content
        field_names = _get_relevant_fields(
            exclude_fields={'id', 'created_at', 'user'}
        )
        # fixating the timestamp for all new records
        transaction_time = timezone.now()
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
        try:
            self._parse_and_save(file)
        except ValidationError as err:
            form.add_error('file', error=err)
            return super().form_invalid(form)
        return super().form_valid(form)


class TableDisplayView(LoginRequiredMixin, TemplateView):
    template_name = 'results.html'
    login_url = reverse_lazy('parser_app:login')

    def _retrieve_latest_data(self):
        latest_date = Variable.objects.filter(user=self.request.user) \
                                      .latest('created_at').created_at
        return Variable.objects.filter(
            Q(user=self.request.user) & Q(created_at=latest_date)
        ).values()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        latest_uploaded = self._retrieve_latest_data()
        if latest_uploaded:
            context['result_tables'] = _group_transform_data(latest_uploaded)
        return context
