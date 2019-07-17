from django.contrib.auth import get_user_model
from django.db import models

from csv_parser.settings import COLS_NUM

User = get_user_model()


class Variable(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    created_at = models.DateTimeField()

    class Meta:
        get_latest_by = 'created_at'
        indexes = [
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        return f'Variable {self.name}'


for i in range(1, COLS_NUM+1):
    Variable.add_to_class(
            f'D{i}',
            models.CharField(max_length=8, blank=True)
        )
