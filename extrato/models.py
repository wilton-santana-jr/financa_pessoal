from django.db import models
from perfil.models import Conta, Categoria

from datetime import datetime, timedelta
from django.db import models


# Create your models here.
class Valores(models.Model):
    choice_tipo = (
        ('E', 'Entrada'),
        ('S', 'Saída')
    )
    
    valor = models.FloatField()
    categoria = models.ForeignKey(Categoria, on_delete=models.DO_NOTHING)
    descricao = models.TextField()
    data = models.DateField()
    conta = models.ForeignKey(Conta, on_delete=models.DO_NOTHING)
    tipo = models.CharField(max_length=1, choices=choice_tipo)


    @classmethod
    def filtrar_por_periodo(cls, periodo):
        hoje = datetime.now().date()

        if periodo == '7':
            dias_atras = hoje - timedelta(days=7)
        elif periodo == '30':
            dias_atras = hoje - timedelta(days=30)
        elif periodo == '60':
            dias_atras = hoje - timedelta(days=60)
        elif periodo == '90':
            dias_atras = hoje - timedelta(days=90)
        elif periodo == 'mes_atual':
            primeiro_dia_mes = hoje.replace(day=1)
            return cls.objects.filter(data__range=[primeiro_dia_mes, hoje])
        else:
            primeiro_dia_mes = hoje.replace(day=1)
            return cls.objects.filter(data__range=[primeiro_dia_mes, hoje])
            #raise ValueError("Período inválido.")

        return cls.objects.filter(data__range=[dias_atras, hoje])


    def __str__(self):
        return self.descricao