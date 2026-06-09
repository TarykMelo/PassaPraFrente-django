from .models import Notificacao


def notificacoes_nao_lidas(request):
        if not request.user.is_authenticated:
            return {'notificacoes_count': 0}

        count = Notificacao.objects.filter(
            usuario=request.user,
            lida=False
        ).count()

        return {'notificacoes_count': count}