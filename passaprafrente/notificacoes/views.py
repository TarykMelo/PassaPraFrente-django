from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Notificacao

class NotificacoesView(LoginRequiredMixin, View):
    def get(self, request):
        notificacoes = Notificacao.objects.filter(usuario=request.user)

        notificacoes.filter(lida=False).update(lida=True)

        return render(request, 'notificacoes/notificacoes.html', {
            'notificacoes': notificacoes,
        })
    
class LimparNotificacoes(LoginRequiredMixin, View):
    def post(self, request):
        Notificacao.objects.filter(usuario=request.user).delete()
        return redirect('notificacoes')