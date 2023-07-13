from datetime import datetime
from django.db.models import Sum

def calcula_total(obj, campo):
    total = 0
    for i in obj:
        total += getattr(i, campo)

    return total


def sum_total(objeto, campo):
    total = objeto.aggregate(Sum(campo))[f"{campo}__sum"]
    if total:
        return total
    else:
        return 0



def get_total_despesas_por_categoria(categorias, valores):
    mes_atual = datetime.now().month

    meses = {
        1: "JAN",
        2: "FEV",
        3: "MAR",
        4: "ABR",
        5: "MAI",
        6: "JUN",
        7: "JUL",
        8: "AGO",
        9: "SET",
        10: "OUT",
        11: "NOV",
        12: "DEZ",
    }
    data = {}
    for categoria in categorias:
        valores_lista = []
        for numero in meses.keys():
            if numero > mes_atual:
                break
            soma_por_categoria = sum_total(
                valores.filter(categoria=categoria).filter(data__month=numero),
                "valor",
            )
            if soma_por_categoria:
                valores_lista.append(soma_por_categoria)
            else:
                valores_lista.append(0)
        data[categoria.categoria] = valores_lista

    return data