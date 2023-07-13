from django.shortcuts import render, redirect
from django.http import HttpResponse
from perfil.models import Conta, Categoria

from django.contrib import messages
from django.contrib.messages import constants
from django.db.models import Sum
#from perfil.utils import calcula_total
# Create your views here.
from .models import Valores

#########
from django.db.models import Sum
from perfil.utils import calcula_total
from datetime import datetime
#total_contas = contas.aggregate(Sum('valor'))['valor__sum']



import os
from io import BytesIO
from django.conf import settings

from django.template.loader import render_to_string
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from weasyprint import HTML
from django.http import FileResponse

def novo_valor(request):


    if request.method == "GET":
        contas = Conta.objects.all()
        categorias = Categoria.objects.all() 
        return render(request, 'novo_valor.html', {'contas': contas, 'categorias': categorias})
    elif request.method == "POST":
        valor = request.POST.get('valor')
        categoria = request.POST.get('categoria')
        descricao = request.POST.get('descricao')
        data = request.POST.get('data')
        conta = request.POST.get('conta')
        tipo = request.POST.get('tipo')
        
        valores = Valores(
            valor=valor,
            categoria_id=categoria,
            descricao=descricao,
            data=data,
            conta_id=conta,
            tipo=tipo,
        )

        valores.save()

        conta = Conta.objects.get(id=conta)

        msg=''
        if tipo == 'E':
            conta.valor += int(valor)
            msg='Nova entrada cadastrada com sucesso'
        else:
            conta.valor -= int(valor)
            msg='Nova saída cadastrada com sucesso'

        conta.save()

        

        messages.add_message(request, constants.SUCCESS, msg)
        return redirect('/extrato/novo_valor')  

def view_extrato(request):
    contas = Conta.objects.all()
    categorias = Categoria.objects.all()

        
    valores = Valores.objects.filter(data__month=datetime.now().month)
    periodo_get = request.GET.get('periodo')
    conta_get = request.GET.get('conta')
    categoria_get = request.GET.get('categoria')

    #if periodo_get is not None and periodo_get.strip()=="mesAtual".strip():
    #    valores = Valores.objects.filter(data__month=datetime.now().month)
    #else:
    #    valores = Valores.objects.filter(data__month=datetime.now().month)    

    valores = Valores.filtrar_por_periodo(periodo_get)

    if(conta_get is not None and conta_get!='todas' and conta_get.strip()!=''):
      if conta_get:
        valores = valores.filter(conta__id=conta_get)
    if(categoria_get is not None and categoria_get!='todas' and conta_get.strip()!=''):
      if categoria_get:
        valores = valores.filter(categoria__id=categoria_get)
 


    




    return render(request, 'view_extrato.html', {'periodo_get':periodo_get,'categoria_get':categoria_get,'conta_get':conta_get,'valores': valores, 'contas': contas, 'categorias': categorias})

def exportar_pdf(request):
    #C:\Program Files\GTK3-Runtime Win64
    #pip install weasyprint
    #faltando importar o settings do core da app, o os, BytesIO, E OUTROS    
    #import weasyprint
    #from io import BytesIO
    valores = Valores.objects.filter(data__month=datetime.now().month)
    contas = Conta.objects.all()
    categorias = Categoria.objects.all()
    


    periodo_get = request.GET.get('periodo')
    conta_get = request.GET.get('conta')
    categoria_get = request.GET.get('categoria')
    if(periodo_get is not None and periodo_get!='todas' and periodo_get.strip()!=''):
         valores = Valores.filtrar_por_periodo(periodo_get)
    if(conta_get is not None and conta_get!='todas' and conta_get.strip()!=''):
      if conta_get:
        valores = valores.filter(conta__id=conta_get)
    if(categoria_get is not None and categoria_get!='todas' and conta_get.strip()!=''):
      if categoria_get:
        valores = valores.filter(categoria__id=categoria_get)







    path_template = os.path.join(settings.BASE_DIR, 'templates/partials/extrato.html')
    path_output = BytesIO()
    path_img_entrada_saida = os.path.join(settings.BASE_DIR, 'templates\static\extrato\img')
    print(path_img_entrada_saida)
    template_render = render_to_string(path_template, {'basedir':settings.BASE_DIR,'path_ent_sai':path_img_entrada_saida,'valores': valores, 'contas': contas, 'categorias': categorias})
    HTML(string=template_render).write_pdf(path_output)

    path_output.seek(0)
    
    return FileResponse(path_output, filename="extrato.pdf")