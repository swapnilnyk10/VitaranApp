from import_export import resources
from .models import Bill

class BillResources(resources.ModelResource):
    class meta:
        model = Bill