from django.shortcuts import render

from django.shortcuts import render, redirect
from django.http import HttpResponse
from perfil.models import Conta, Categoria


from django.contrib import messages
from django.contrib.messages import constants
from django.db.models import Sum
from perfil.utils import calcula_total

from extrato.models import Valores
from datetime import datetime,timedelta
from django.db.models import Sum
from django.db.models.functions import ExtractMonth


import json
from django.http import HttpResponse
from django.http import JsonResponse
from contas.models import ContaPagar, ContaPaga
from datetime import datetime,timedelta


def nova_conta(request):
    if request.method == "GET":
        categorias = Categoria.objects.all()
        return render(request, 'nova_conta.html', {'categorias': categorias}) 
    else:
        titulo = request.POST.get('titulo')
        categoria = request.POST.get('categoria')
        descricao = request.POST.get('descricao')
        valor = request.POST.get('valor')
        dia_pagamento = request.POST.get('dia_pagamento')

        conta = ContaPagar(
            titulo=titulo,
            categoria_id=categoria,
            descricao=descricao,
            valor=valor,
            dia_pagamento=dia_pagamento
        )

        conta.save()

        messages.add_message(request, constants.SUCCESS, 'Conta cadastrada com sucesso')
        return redirect('/contas/nova_conta')   

def ver_contas(request):
    MES_ATUAL = datetime.now().month
    DIA_ATUAL = datetime.now().day
    
    contas = ContaPagar.objects.all()

    contas_pagas = ContaPaga.objects.filter(data_pagamento__month=MES_ATUAL).values('conta')

    contas_vencidas = contas.filter(dia_pagamento__lt=DIA_ATUAL).exclude(id__in=contas_pagas)
    
    contas_proximas_vencimento = contas.filter(dia_pagamento__lte = DIA_ATUAL + 5).filter(dia_pagamento__gte=DIA_ATUAL).exclude(id__in=contas_pagas)
    
    restantes = contas.exclude(id__in=contas_vencidas).exclude(id__in=contas_pagas).exclude(id__in=contas_proximas_vencimento)

    return render(request, 'ver_contas.html', {'contas_pagas':contas_pagas,'contas_vencidas':contas_vencidas, 'contas_proximas_vencimento':contas_proximas_vencimento, 'restantes':restantes})



def pagar_conta(request, id):
    id_conta = json.load(request)['id_conta']
    contaPagar = ContaPagar.objects.get(id=id)

    data = datetime.now().date()
    contaPaga = ContaPaga(conta=contaPagar,data_pagamento=data)
    contaPaga.save()

    return JsonResponse({'status': 'Sucesso'})

