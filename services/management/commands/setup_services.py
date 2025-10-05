# management/commands/setup_services.py
from django.core.management.base import BaseCommand
from services.models import ThirdPartyService
from dotenv import load_dotenv
import os

load_dotenv()

class Command(BaseCommand):
    help = 'Setup default third-party services dengan encrypted API keys'

    def handle(self, *args, **options):
        services = [
            {
                'name': 'openweather',
                'api_endpoint': 'https://api.openweathermap.org/data/2.5',
                'api_key': os.getenv("OPENWEATHER_API_KEY"),
                'rate_limit_per_hour': 60
            },
            {
                'name': 'newsapi',
                'api_endpoint': 'https://newsapi.org',
                'api_key': os.getenv("NEWSAPI_API_KEY"),
                'rate_limit_per_hour': 100
            },
            {
                'name': 'github',
                'api_endpoint': 'https://api.github.com',
                'api_key': os.getenv("GITHUB_PERSONAL_TOKEN"),
                'rate_limit_per_hour': 60
            },
            {
                'name': 'coingecko',
                'api_endpoint': 'https://api.coingecko.com/api/v3',
                'api_key': os.getenv("COINGECKO_API_KEY"),
                'rate_limit_per_hour': 60
            },
            {
                'name': 'exchangeRate',
                'api_endpoint': 'https://v6.exchangerate-api.com/v6',
                'api_key': os.getenv("EXCHANGE-RATE-API-KEY"),
                'rate_limit_per_hour': 60
            }
        ]

        for service_data in services:
            # Gunakan set_api_key untuk encrypt
            api_key = service_data.pop('api_key')
            service, created = ThirdPartyService.objects.get_or_create(
                name=service_data['name'],
                defaults=service_data
            )

            decrypted_key = service.get_api_key() if not created else None

            if created or decrypted_key != api_key:
                service.set_api_key(api_key)
                service.save()
                action = "Created" if created else "Updated"
                self.stdout.write(
                    self.style.SUCCESS(f"{action} service: {service_data['name']}")
                )
