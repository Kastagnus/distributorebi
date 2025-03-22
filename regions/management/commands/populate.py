import json
from django.core.management.base import BaseCommand
from regions.models import Region, City  # Update with your actual app name

class Command(BaseCommand):
    help = "Populates the Region and City tables from a JSON file"

    def handle(self, *args, **kwargs):
        with open("regions/management/commands/region_data.json", "r", encoding="utf-8") as file:
            data = json.load(file)

        regions_data = data.get("საქართველო", {}).get("რეგიონები", [])

        for region_data in regions_data:
            region_name = region_data["დასახელება"]
            region, created = Region.objects.get_or_create(name=region_name)

            for city_name in region_data["ქალაქები"]:
                City.objects.get_or_create(name=city_name, region=region)

        self.stdout.write(self.style.SUCCESS("Regions and cities populated successfully!"))
