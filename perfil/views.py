from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Conta, Categoria

from django.contrib import messages
from django.contrib.messages import constants
from django.db.models import Sum
from .utils import calcula_total

from extrato.models import Valores
from contas.models import ContaPagar, ContaPaga
from datetime import datetime,timedelta
from django.db.models import Sum
from django.db.models.functions import ExtractMonth


def home(request):
    contas = Conta.objects.all()
    total_contas = calcula_total(contas, 'valor')
    #total_contas = contas.aggregate(Sum('valor'))['valor__sum']
    entradas_mes_corrente = Valores.objects.filter(tipo='E').filter(data__month=datetime.now().month).aggregate(Sum('valor'))['valor__sum']
    saidas_mes_corrente = Valores.objects.filter(tipo='S').filter(data__month=datetime.now().month).aggregate(Sum('valor'))['valor__sum']


    entradas_mes_corrente = entradas_mes_corrente if entradas_mes_corrente is not None else 0
    #entradas_mes_anterior = registros_mes_anterior.count() if registros_mes_anterior.exists() else 0    
    saidas_mes_corrente = saidas_mes_corrente if saidas_mes_corrente is not None else 0


    #valor do mes anterior + entradas do mes corrente
    # Obtendo o mês atual
    mes_atual = datetime.now().month
    # Obtendo o mês anterior
    mes_anterior = (mes_atual - 2) % 12 + 1
    entradas_mes_anterior = Valores.objects.filter(tipo='E').filter(data__month=mes_anterior).aggregate(Sum('valor'))['valor__sum']
    saidas_mes_anterior = Valores.objects.filter(tipo='S').filter(data__month=mes_anterior).aggregate(Sum('valor'))['valor__sum']
    
    entradas_mes_anterior = entradas_mes_anterior if entradas_mes_anterior is not None else 0
    #entradas_mes_anterior = registros_mes_anterior.count() if registros_mes_anterior.exists() else 0    
    saidas_mes_anterior = saidas_mes_anterior if saidas_mes_anterior is not None else 0
    

    saldo_mensal=entradas_mes_corrente + (entradas_mes_anterior-saidas_mes_anterior)
    despesas_mensal=saidas_mes_corrente 
    total_livre=saldo_mensal-despesas_mensal



    gastos_essenciais_mes_corrente = Valores.objects.filter(tipo='S').filter(categoria__essencial=True).filter(data__month=mes_atual).aggregate(Sum('valor'))['valor__sum']
    gastos_nao_essenciais_mes_corrente = Valores.objects.filter(tipo='S').filter(categoria__essencial=False).filter(data__month=mes_atual).aggregate(Sum('valor'))['valor__sum']

    gastos_essenciais_mes_corrente = gastos_essenciais_mes_corrente if gastos_essenciais_mes_corrente is not None else 0
    gastos_nao_essenciais_mes_corrente = gastos_nao_essenciais_mes_corrente if gastos_nao_essenciais_mes_corrente is not None else 0    
    gastos_totais_mes_corrente = (gastos_essenciais_mes_corrente+gastos_nao_essenciais_mes_corrente)
    if gastos_totais_mes_corrente:
        percentual_gastos_essenciais_mes_corrente2 = (gastos_essenciais_mes_corrente *100)/gastos_totais_mes_corrente
        percentual_gastos_nao_essenciais_mes_corrente2 = (gastos_nao_essenciais_mes_corrente *100)/gastos_totais_mes_corrente
    else:
        percentual_gastos_essenciais_mes_corrente2=0          
        percentual_gastos_nao_essenciais_mes_corrente2 =0

    percentual_gastos_nao_essenciais_mes_corrente2 = (gastos_nao_essenciais_mes_corrente *100)/gastos_totais_mes_corrente
    percentual_gastos_essenciais_mes_corrente = int(percentual_gastos_essenciais_mes_corrente2)
    percentual_gastos_nao_essenciais_mes_corrente = int(percentual_gastos_nao_essenciais_mes_corrente2)




    #pegar os boletos de contas da pessoa 
    MES_ATUAL = datetime.now().month    
    DIA_ATUAL = datetime.now().day    
    contasboletos = ContaPagar.objects.all()
    contasboletos = contasboletos if contasboletos is not None else 0
    contas_pagas = ContaPaga.objects.filter(data_pagamento__month=MES_ATUAL).values('conta')
    contas_pagas = contas_pagas if contas_pagas is not None else 0    
    contas_vencidas = contasboletos.filter(dia_pagamento__lt=DIA_ATUAL).exclude(id__in=contas_pagas)    
    contas_vencidas = contas_vencidas if contas_vencidas is not None else 0    
    contas_proximas_vencimento = contasboletos.filter(dia_pagamento__lte = DIA_ATUAL + 5).filter(dia_pagamento__gte=DIA_ATUAL).exclude(id__in=contas_pagas)    
    contas_proximas_vencimento = contas_proximas_vencimento if contas_proximas_vencimento is not None else 0    
    restantes = contasboletos.exclude(id__in=contas_vencidas).exclude(id__in=contas_pagas).exclude(id__in=contas_proximas_vencimento)
    restantes = restantes if restantes is not None else 0    


    if(contas_proximas_vencimento!=0):
        contas_proximas_vencimento_size=len(list(contas_proximas_vencimento))
    else:
        contas_proximas_vencimento_size=0
    
    if(contas_vencidas!=0):
        contas_vencidas_size=len(list(contas_vencidas))
    else:
        contas_vencidas_size=0




    return render(request, 'home.html', {
    'contas_proximas_vencimento_size':contas_proximas_vencimento_size,
    'contas_vencidas_size':contas_vencidas_size,
    'percentual_gastos_essenciais_mes_corrente2':round(percentual_gastos_essenciais_mes_corrente2,2),
    'percentual_gastos_nao_essenciais_mes_corrente2':round(percentual_gastos_nao_essenciais_mes_corrente2,2),
    'percentual_gastos_essenciais_mes_corrente':percentual_gastos_essenciais_mes_corrente,
    'percentual_gastos_nao_essenciais_mes_corrente':percentual_gastos_nao_essenciais_mes_corrente,
    'total_livre':total_livre,'despesas_mensal':despesas_mensal,'saldo_mensal':saldo_mensal,
    'saidas_mes_corrente':saidas_mes_corrente,'entradas_mes_corrente':entradas_mes_corrente,'contas': contas, 'total_contas': total_contas, })


def gerenciar(request):
    contas = Conta.objects.all()
    categorias = Categoria.objects.all()
    total_contas = calcula_total(contas, 'valor')

    banco_choices = (
        ('NU', 'Nubank'),
        ('CE', 'Caixa Econômica'),
        ('BB', 'Banco do Brasil'),
        ('BI', 'Banco Inter'),
        ('BD', 'Banco do Bradesco'),
    )

    tipo_choices = (
        ('pf', 'Pessoa física'),
        ('pj', 'Pessoa jurídica'),
    )

    return render(request, 'gerenciar.html', {       
        'bancos':banco_choices,'tipos':tipo_choices,'categorias': categorias, 'contas': contas, 'total_contas': total_contas})


def cadastrar_banco(request):

    apelido = request.POST.get('apelido')
    banco = request.POST.get('banco')
    tipo = request.POST.get('tipo')
    valor = request.POST.get('valor')
    icone = request.FILES.get('icone')

    if len(apelido.strip()) == 0 or len(valor.strip()) == 0:
        messages.add_message(request, constants.ERROR,
                             'Preencha todos os campos')
        return redirect('/perfil/gerenciar/')
    #realizar mais validações para o banco,tipo,icone
    conta = Conta(apelido=apelido, banco=banco,
                  tipo=tipo, valor=valor, icone=icone)

    conta.save()

    messages.add_message(request, constants.SUCCESS,
                         'Conta cadastrada com sucesso')
    return redirect('/perfil/gerenciar/')


def deletar_banco(request, id):
    conta = Conta.objects.get(id=id)
    conta.delete()

    messages.add_message(request, constants.SUCCESS,
                         'Conta removida com sucesso')
    return redirect('/perfil/gerenciar/')

def cadastrar_categoria(request):
    nome = request.POST.get('categoria')
    essencial = bool(request.POST.get('essencial'))
    if nome is None or nome.strip() == "":
        messages.add_message(request, constants.ERROR, 'Nome da categoria não pode estar vazio')
        return redirect('/perfil/gerenciar/')

    if essencial is None:
        messages.add_message(request, constants.ERROR, 'Valor essencial não foi fornecido')
        return redirect('/perfil/gerenciar/')

    if not isinstance(essencial, bool):
        messages.add_message(request, constants.ERROR, 'Valor essencial inválido')
        return redirect('/perfil/gerenciar/')

    categoria = Categoria(categoria=nome, essencial=essencial)
    categoria.save()

    messages.add_message(request, constants.SUCCESS, 'Categoria cadastrada com sucesso')
    return redirect('/perfil/gerenciar/')


def update_categoria(request, id):
    categoria = Categoria.objects.get(id=id)

    categoria.essencial = not categoria.essencial

    categoria.save()

    return redirect('/perfil/gerenciar/')


def dashboard(request):
    titulo='Gastos por categoria'
    dados = {}
    categorias = Categoria.objects.all()
    mes_atual=datetime.now().month

    for categoria in categorias:
        valores = Valores.objects.filter(tipo='S').filter(data__month=mes_atual).filter(categoria=categoria).aggregate(Sum('valor'))['valor__sum']
        valores = valores if valores is not None else 0
        dados[categoria.categoria] =  valores

    return render(request, 'dashboard.html', {'titulo':titulo,'labels': list(dados.keys()), 'values': list(dados.values())})


def dashboard2(request):
    titulo='Entradas por categoria'
    dados = {}
    categorias = Categoria.objects.all()
    mes_atual=datetime.now().month

    for categoria in categorias:
        valores = Valores.objects.filter(tipo='E').filter(data__month=mes_atual).filter(categoria=categoria).aggregate(Sum('valor'))['valor__sum']
        valores = valores if valores is not None else 0
        dados[categoria.categoria] =  valores
    return render(request, 'dashboard.html', {'titulo':titulo,'labels': list(dados.keys()), 'values': list(dados.values())})    