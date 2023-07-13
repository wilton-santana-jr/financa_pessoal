from django.contrib import admin


# Register your models here.
from .models import Conta, Categoria
# Register your models here.
admin.site.register(Conta)
admin.site.register(Categoria)