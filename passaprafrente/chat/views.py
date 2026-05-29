from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from pedidos.models import Pedido
from .models import Mensagem

@login_required
def chat_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)

    comprador = pedido.comprador == request.user
    vendedor = pedido.produto.vendedor == request.user

    if not comprador and not vendedor:
        return redirect('user_menu')
    
    if request.method == 'POST':
        conteudo = request.POST.get('conteudo', '').strip()
        if conteudo:
            Mensagem.objects.create(
                pedido=pedido,
                remetente=request.user,
                conteudo=conteudo
            )
        if request.headers.get('X-CSRFToken'):
            return JsonResponse({'ok': True})
        return redirect('chat_pedido', pedido_id=pedido_id)
    
    mensagens = Mensagem.objects.filter(pedido=pedido)
    ultimo_id = mensagens.last().id if mensagens.exists() else 0

    return render(request, 'chat/chat.html', {
        'pedido': pedido,
        'mensagens': mensagens,
        'ultimo_id': ultimo_id,
    })

@login_required
def mensagens_novas(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)

    comprador = pedido.comprador == request.user
    vendedor = pedido.produto.vendedor == request.user

    if not comprador and not vendedor:
        return JsonResponse({'erro': 'Acesso negado'}, status=403)
    
    ultimo_id = request.GET.get('ultimo_id', 0)

    mensagens = Mensagem.objects.filter(
        pedido=pedido,
        id__gt=ultimo_id
    )

    dados = [
        {
            'id': m.id,
            'remetente': m.remetente.nickname,
            'conteudo': m.conteudo,
            'hora': m.enviado_em.strftime('%d/%m/%Y %H:%M'),
        }
        for m in mensagens
    ]

    return JsonResponse({'mensagens': dados})