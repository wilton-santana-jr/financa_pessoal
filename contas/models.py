from django.db import models

from datetime import datetime
from django.db.models import Sum
from perfil.utils import calcula_total
from perfil.models import Categoria
#total_contas = contas.aggregate(Sum('valor'))['valor__sum']

class ContaPagar(models.Model):
    titulo = models.CharField(max_length=50)
    categoria = models.ForeignKey(Categoria, on_delete=models.DO_NOTHING)
    descricao = models.TextField()
    valor = models.FloatField()
    dia_pagamento = models.IntegerField()
    
    def __str__(self):
        return self.titulo

class ContaPaga(models.Model):
    conta = models.ForeignKey(ContaPagar, on_delete=models.DO_NOTHING)
    data_pagamento = models.DateField()
