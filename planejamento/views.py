from django.shortcuts import render, redirect
from django.http import HttpResponse


from django.contrib import messages
from django.contrib.messages import constants
from django.db.models import Sum
#from perfil.utils import calcula_total
from extrato.models import Valores
from perfil.models import Conta, Categoria

from datetime import datetime
import os
from io import BytesIO
from django.conf import settings

from django.template.loader import render_to_string
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from weasyprint import HTML
from django.http import FileResponse
import json
from django.http import HttpResponse
from django.http import JsonResponse

def definir_planejamento(request):
    categorias = Categoria.objects.all()
    return render(request, 'definir_planejamento.html', {'categorias': categorias})

def update_valor_categoria(request, id):
    novo_valor = json.load(request)['novo_valor']
    categoria = Categoria.objects.get(id=id)
    categoria.valor_planejamento = novo_valor
    categoria.save()

    return JsonResponse({'status': 'Sucesso'})

def ver_planejamento(request):
    categorias = Categoria.objects.all()

    valoresSaidas = Valores.objects.filter(tipo='S').filter(data__month=datetime.now().month).aggregate(Sum('valor'))
    valoresSaidas['valor__sum'] if valoresSaidas['valor__sum'] else 0
    valoresPlanejados = Categoria.objects.aggregate(Sum('valor_planejamento'))
    valoresPlanejados['valor_planejamento__sum'] if valoresPlanejados['valor_planejamento__sum'] else 0
    percentualTotaSaidas=int((100*valoresSaidas['valor__sum'])/valoresPlanejados['valor_planejamento__sum'])
    
    return render(request, 'ver_planejamento.html', {'valoresPlanejados':valoresPlanejados['valor_planejamento__sum'],'percentualTotaSaidas':percentualTotaSaidas,'valoresSaidas':valoresSaidas['valor__sum'],'categorias': categorias})