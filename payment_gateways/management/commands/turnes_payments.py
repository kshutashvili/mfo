from datetime import date

from django.core.management.base import BaseCommand

from payment_gateways.helpers import run_payments_distribution


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        run_payments_distribution()
