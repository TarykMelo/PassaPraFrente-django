from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.http import JsonResponse 
from produtos.models import Produto
from accounts.models import Usuario
from .models import Pedido, Feedback, Mensagem
from .forms import FeedbackForm
from .carrinho import Carrinho
from .emails import enviar_email_status_pedido
from .moderacao import ModeracaoMensagem
from notificacoes.utils import CriarNotificacao


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

        pedido = Pedido.objects.create(
            produto=produto, 
            comprador=request.user,
            vendedor=produto.vendedor,
            status='pendente'
            )
        
        CriarNotificacao.pedido_recebido(pedido)

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
        ).exclude(
            feedback_pedido__isnull=False
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
        CriarNotificacao.pedido_cancelado(pedido, request.user)

        return redirect('meus_pedidos')


class MinhasVendasView(LoginRequiredMixin, View):
    """
    View para o vendedor visualizar e gerenciar os pedidos que fizeram de seus produtos
    """
    def get(self, request):
        vendas = Pedido.objects.filter(vendedor=request.user).exclude(
            status__in=['finalizado', 'cancelado', 'cancelamento_solicitado']
        ).select_related('produto', 'comprador')
        return render(request, 'pedidos/minhas_vendas.html', {'vendas': vendas})

    
    
class MudarStatusVendaView(LoginRequiredMixin, View):
    def post(self, request, pedido_id):
        pedido = get_object_or_404(Pedido, id=pedido_id, vendedor=request.user)
        nova_acao = request.POST.get('acao')

        if nova_acao == 'confirmar':
            pedido.status = 'compra_confirmada'
            messages.success(request, f"Pedido de {pedido.comprador.nickname} confirmado!")
            CriarNotificacao.pedido_confirmado(pedido)
            
            enviar_email_status_pedido(
                email_destinatario=pedido.comprador.email,
                nome_comprador=pedido.comprador.first_name if pedido.comprador.first_name else pedido.comprador.nickname,
                nome_produto=pedido.produto.nome,
                numero_pedido=pedido.id,
                status='confirmado'
            )


        elif nova_acao == 'finalizar':
            pedido.status = 'aguardando_confirmacao'
            messages.success(request, f"Produto marcado como entregue! Aguardando confirmação do comprador.")
        
        elif nova_acao == 'cancelar': 
            pedido.status = 'cancelado'
            messages.success(request, f"Pedido de {pedido.comprador.nickname} cancelado.")
        
            enviar_email_status_pedido(
                email_destinatario=pedido.comprador.email,
                nome_comprador=pedido.comprador.first_name if pedido.comprador.first_name else pedido.comprador.nickname,
                nome_produto=pedido.produto.nome,
                numero_pedido=pedido.id,
                status='cancelado'
            )


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
        CriarNotificacao.venda_concluida(pedido)

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
            
            CriarNotificacao.nova_avaliacao(feedback) 
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

        from django.db.models import Avg
        media = feedbacks.aggregate(media=Avg('nota'))['media']

        return render(request, 'pedidos/meus_feedbacks.html', { #Adicionar depois essa página no histórico de produtos vendidos
            'feedbacks': feedbacks,
            'media': round(media, 1) if media else None,
        })

class HistoricoView(LoginRequiredMixin, View):
    """
    Página inicial com a escolha do usuário se quer ver os produtos vendidos ou comprados
    """
    def get(self, request):
        return render(request, 'pedidos/historico.html')

class HistoricoComprasView(LoginRequiredMixin, View):
    """
    Histórico de compras do usuário
    """
    def get(self, request):
        filtro = request.GET.get('filtro', 'todos')

        pedidos = Pedido.objects.filter(
            comprador=request.user,
            status__in=['finalizado', 'cancelado', 'cancelamento_solicitado']
        ).select_related('produto', 'produto__vendedor').order_by('-criado_em')

        total_finalizados=pedidos.filter(status='finalizado').count()

        if filtro == 'finalizado':
            pedidos = pedidos.filter(status='finalizado')
        elif filtro == 'cancelado':
            pedidos = pedidos.filter(status__in=['cancelado', 'cancelamento_solicitado'])

        return render(request, 'pedidos/historico_compras.html',{
            'pedidos': pedidos,
            'filtro': filtro,
            'total_finalizados': total_finalizados,
        })

class HistoricoVendasView(LoginRequiredMixin, View):
    """
    Classe que retorna o histórico de vendas do usuário
    """
    def get(self, request):
        filtro = request.GET.get('filtro', 'todos')

        vendas= Pedido.objects.filter(
            vendedor=request.user,
            status__in=['finalizado', 'cancelado', 'cancelamento_solicitado']
        ).select_related('produto', 'comprador').order_by('-criado_em')

        total_finalizados=vendas.filter(status='finalizado').count()

        if filtro == 'finalizado':
            vendas = vendas.filter(status='finalizado')
        elif filtro == 'cancelado':
            vendas = vendas.filter(status__in=['cancelado', 'cancelamento_solicitado'])

        return render(request, 'pedidos/historico_vendas.html',{
            'vendas': vendas,
            'filtro': filtro,
            'total_finalizados': total_finalizados,
        })

class DetalheHistoricoView(LoginRequiredMixin, View):
    """
    Informações do produto que está no histórico
    """
    def get(self, request, pedido_id):
        pedido = get_object_or_404(
            Pedido,
            id=pedido_id,
            status__in=['finalizado', 'cancelado', 'cancelamento_solicitado']
        )

        if pedido.comprador != request.user and pedido.vendedor != request.user:
            return redirect('user_menu')
        
        feedback = getattr(pedido, 'feedback_pedido', None)

        comprador = pedido.comprador == request.user

        return render(request, 'pedidos/detalhe_historico.html',{
        'pedido': pedido,
        'feedback': feedback,
        'comprador': comprador,
        })
    
class CarrinhoView(LoginRequiredMixin, View):
    """
    Exibe o carrinho do usuário
    """
    def get(self, request):
        carrinho = Carrinho(request)
        produtos = carrinho.produtos(request.user)
        total = carrinho.total(request.user)
        return render(request, 'pedidos/carrinho.html',{
            'produtos': produtos,
            'total': total,
        })

class AdicionarCarrinhoView(LoginRequiredMixin, View):
    """
    Adiciona um produto ao carrinho
    """
    def post(self, request, produto_id):
        produto = get_object_or_404(Produto, id=produto_id)
        carrinho = Carrinho(request)

        if produto.vendedor == request.user:
            messages.error(request, "Você não pode adicionar seu próprio produto!")
            return redirect('user_menu')

        if produto.vendido:
            messages.error(request, "Esse produto ja foi vendido!")
            return redirect('user_menu')
        
        carrinho.adicionar(produto_id)
        messages.success(request, f"{produto.nome} adicionado ao carrinho")
        return redirect('user_menu')
    
class RemoverCarrinhoView(LoginRequiredMixin, View):
    """
    Remove um produto do carrinho
    """
    def post(self, request, produto_id):
        carrinho = Carrinho(request)
        carrinho.remover(produto_id)
        messages.success(request, "Produto removido do carrinho.")
        return redirect('ver_carrinho')
    
class CheckoutView(LoginRequiredMixin, View):
    """
    Confirma todos os pedidos do carrinho
    """
    def get(self, request):
        carrinho = Carrinho(request)
        produtos = carrinho.produtos(request.user)
        total = carrinho.total(request.user)
        return render(request, 'pedidos/carrinho_checkout.html',{
            'produtos': produtos,
            'total': total,
        })
    
    def post(self, request):
        carrinho = Carrinho(request)
        produtos = carrinho.produtos(request.user)

        for produto in produtos:
            ja_pedido = Pedido.objects.filter(
                produto=produto,
                comprador=request.user
            ).exists()

            if not ja_pedido and not produto.vendido:
                Pedido.objects.create(
                    produto=produto,
                    comprador=request.user,
                    vendedor=produto.vendedor,
                    status='pendente'
                )
        
        carrinho.limpar()
        messages.success(request, "Pedidos realizados com sucesso!")
        return redirect('meus_pedidos')
    
class ChatView(LoginRequiredMixin, View):
    """
    Página principal do chat
    """
    def get(self, request, pedido_id):
        pedido = get_object_or_404(Pedido, id=pedido_id)

        comprador = pedido.comprador == request.user
        vendedor = pedido.vendedor == request.user

        if not comprador and not vendedor:
            return redirect('user_menu')
        
        mensagens = Mensagem.objects.filter(pedido=pedido)
        ultimo_id = mensagens.last().id if mensagens.exists() else 0

        return render(request, 'pedidos/chat.html', {
            'pedido': pedido,
            'mensagens': mensagens,
            'ultimo_id': ultimo_id,
        })

    def post(self, request, pedido_id):
        pedido = get_object_or_404(Pedido, id=pedido_id)

        comprador = pedido.comprador == request.user
        vendedor = pedido.vendedor == request.user

        if not comprador and not vendedor:
            return redirect('user_menu')
        
        conteudo = request.POST.get('conteudo', '').strip()

        if conteudo:

            permitido, motivo = ModeracaoMensagem.verificar(conteudo)

            if not permitido:
                return JsonResponse({
                    'ok': False,
                    'erro': f'Mensagem bloqueada: {motivo}'
                })

            mensagem = Mensagem.objects.create(
                pedido=pedido,
                remetente=request.user,
                conteudo=conteudo
            )
            CriarNotificacao.nova_mensagem(mensagem)

        if request.headers.get('X-CSRFToken'):
            return JsonResponse({'ok': True})
        return redirect('chat', pedido_id=pedido_id)
    
class MensagensNovasView(LoginRequiredMixin, View):
    """
    Retorna mensagens novas em JSON para o polling
    """
    def get(self, request, pedido_id):
        pedido = get_object_or_404(Pedido, id=pedido_id)

        comprador = pedido.comprador == request.user
        vendedor = pedido.vendedor == request.user

        if not comprador and not vendedor:
            return JsonResponse({'erro': 'Acesso negado'}, status=403)
        
        ultimo_id = request.GET.get('ultimo_id', 0)

        mensagens = Mensagem.objects.filter(
            pedido=pedido,
            id__gt=ultimo_id
        )

        dados = [
            {
                'id': mensagem.id,
                'remetente': mensagem.remetente.nickname,
                'conteudo': mensagem.conteudo,
                'hora': mensagem.enviado_em.strftime('%d/%m/%Y %H:%M'),
                'user_id': mensagem.remetente.id,
            }
            for mensagem in mensagens
        ]

        return JsonResponse({'mensagens': dados})