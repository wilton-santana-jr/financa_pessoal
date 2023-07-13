from django.urls import path,include
from . import views
urlpatterns = [

    path('nova_conta/', views.nova_conta, name="nova_conta"),
    path('ver_contas/', views.ver_contas, name="ver_contas"),    
    path('pagar_conta/<int:id>', views.pagar_conta, name="pagar_conta"),

]