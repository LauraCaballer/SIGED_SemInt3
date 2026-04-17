from django.contrib import admin
from .models import Compra, CompraPrenda, Venta, VentaPrenda
# Register your models here.
admin.site.register(Compra)
admin.site.register(CompraPrenda)
admin.site.register(Venta)
admin.site.register(VentaPrenda)