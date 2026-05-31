from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages 
from produtos.models import Produto
from .models import Pedido, Feedback
from .forms import FeedbackForm
from django.db.models import AVG

class FazerPedidoView(LoginRequiredMixin, View):
    """
    View de fazer pedido com restrições de pedido duplicado
    e produto do próprio usuário
    """
    def get(self, request, produto_id):
        produto = get_object_or_404(Produto, id=produto_id)

        if produto.vendedor == request.user:
            return redirect('user_menu')

        ja_pedido = Pedido.objects.filter(
            produto=produto,
            comprador=request.user
        ).exists()

        if ja_pedido:
            return redirect('user_menu')

        return render(request, 'pedidos/confirmar_pedido.html', {'produto': produto})

    def post(self, request, produto_id):
        produto = get_object_or_404(Produto, id=produto_id)

        if produto.vendedor == request.user:
            return redirect('user_menu')

        ja_pedido = Pedido.objects.filter(
            produto=produto,
            comprador=request.user
        ).exists()

        if ja_pedido:
            return redirect('user_menu')

        Pedido.objects.create(
            produto=produto, 
            comprador=request.user,
            vendedor=produto.vendedor,
            status='pendente'
            )
        return redirect('user_menu')


class MeusPedidosView(LoginRequiredMixin, View):
    """
    View para a página de ver meus pedidos
    """
    def get(self, request):
        pedidos = Pedido.objects.filter(
            comprador=request.user
        ).exclude(
            status='cancelado'
        ).select_related('produto', 'produto__vendedor')
        return render(request, 'pedidos/meus_pedidos.html', {'pedidos': pedidos})


class CancelarPedidoView(LoginRequiredMixin, View):
    """
    View para deletar o pedido feito pelo usuário
    """
    def post(self, request, pedido_id):
        pedido = get_object_or_404(Pedido, id=pedido_id, comprador=request.user)
        pedido.status = 'cancelado'
        pedido.save()
        messages.success(request, "Pedido cancelado com sucesso.")
        return redirect('meus_pedidos')


class MinhasVendasView(LoginRequiredMixin, View):
    """
    View para o vendedor visualizar e gerenciar os pedidos que fizeram de seus produtos
    """
    def get(self, request):
        vendas = Pedido.objects.filter(vendedor=request.user).select_related('produto', 'comprador')
        return render(request, 'pedidos/minhas_vendas.html', {'vendas': vendas})

    
    
class MudarStatusVendaView(LoginRequiredMixin, View):
    def post(self, request, pedido_id):
        pedido = get_object_or_404(Pedido, id=pedido_id, vendedor=request.user)
        nova_acao = request.POST.get('acao')

        if nova_acao == 'confirmar':
            pedido.status = 'compra_confirmada'
            messages.success(request, f"Pedido de {pedido.comprador.nickname} confirmado!")
        elif nova_acao == 'finalizar':
            pedido.status = 'aguardando_confirmacao'
            messages.success(request, f"Produto marcado como entregue! Aguardando confirmação do comprador.")
        elif nova_acao == 'cancelar': 
            pedido.status = 'cancelado'
            messages.success(request, f"Pedido de {pedido.comprador.nickname} cancelado.")
        
        pedido.save()
        return redirect('minhas_vendas')

    
class ConfirmarRecebimentoView(LoginRequiredMixin, View):
    """
    Comprador confirma que recebeu o produto
    """
    def post(self, request, pedido_id):
        pedido = get_object_or_404(
            Pedido,
            id=pedido_id,
            comprador=request.user,
            status='aguardando_confirmacao'
        )
        pedido.finalizar()
        messages.success(request, "Recebimento confirmado! Obrigado pela compra.")
        return redirect('meus_pedidos')

class EnviarFeedbackView(LoginRequiredMixin, View):
    """
    View em POO para processar a avaliação que o comprador dá ao vendedor
    após a conclusão do pedido.
    """
    def get(self, request, pedido_id):
        pedido = get_object_or_404(Pedido, id=pedido_id, comprador=request.user)
        
        # Só deixa avaliar se o pedido estiver finalizado
        if pedido.status != 'finalizado':
            messages.error(request, "Você só pode dar feedback para um pedido finalizado.")
            return redirect('meus_pedidos') 

        if hasattr(pedido, 'feedback_pedido'):
        messages.error(request, "Você já avaliou este pedido.")
        return redirect('meus_pedidos')
            
        form = FeedbackForm()
        return render(request, 'pedidos/enviar_feedback.html', {'form': form, 'pedido': pedido})

    def post(self, request, pedido_id):
        pedido = get_object_or_404(Pedido, id=pedido_id, comprador=request.user)
        
        if pedido.status != 'finalizado':
            messages.error(request, "Ação não permitida.")
            return redirect('meus_pedidos')

        if hasattr(pedido, 'feedback_pedido'):
        messages.error(request, "Você já avaliou este pedido.")
        return redirect('meus_pedidos')

        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.pedido = pedido
            feedback.avaliador = request.user
            feedback.vendedor = pedido.vendedor 
            feedback.save()
            
            messages.success(request, "Obrigado! Seu feedback foi enviado com sucesso.")
            return redirect('meus_pedidos')
            
        return render(request, 'pedidos/enviar_feedback.html', {'form': form, 'pedido': pedido})

class MeusFeedbacksView(LoginRequiredMixin, View):
    """
    Vendedor Vê os feedbacks que recebeu
    """
    def get(self, request):
        feedbacks = Feedback.objects.filter(
            vendedor=request.user
        ).select_related('avaliador', 'pedido__produto')

        media = feedbacks.aggregate(media=Avg('nota'))['media']

        return render(request, 'pedidos/meus_feedbacks.html', { #Adicionar depois essa página no histórico de produtos vendidos
            'feedbacks': feedbacks,
            'media': round(media, 1) if media else None,
        })