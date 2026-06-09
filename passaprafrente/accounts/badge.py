class Badge:
    NIVEIS = [
        ('diamante', '💎', 'Diamante', 50, 4.6, None,       None),
        ('platina',  '🔷', 'Platina',  25, 4.4, 'Diamante', (50, 4.6)),
        ('ouro',     '🥇', 'Ouro',     10, 4.0, 'Platina',  (25, 4.4)),
        ('prata',    '🥈', 'Prata',     5, 0.0, 'Ouro',     (10, 4.0)),
        ('bronze',   '🥉', 'Bronze',    0, 0.0, 'Prata',    (5,  0.0)),
    ]

    def __init__(self, user):
        self.vendas = user.total_avaliacoes
        self.media  = user.media_avaliacoes

    def calcular(self):
        for nivel, icone, nome, min_vendas, min_media, proximo_nome, proximo_req in self.NIVEIS:
            if self.vendas >= min_vendas and self.media >= min_media:
                return {
                    'badge_nivel':      nivel,
                    'badge_icone':      icone,
                    'badge_nome':       nome,
                    'badge_proximo':    proximo_nome,
                    'badge_requisitos': self._requisitos(proximo_req),
                }

        return {
            'badge_nivel':      'bronze',
            'badge_icone':      '🥉',
            'badge_nome':       'Bronze',
            'badge_proximo':    'Prata',
            'badge_requisitos': 'faça sua primeira venda',
        }

    def _requisitos(self, proximo_req):
        if not proximo_req:
            return None

        partes = []
        vendas_faltam = proximo_req[0] - self.vendas
        if vendas_faltam > 0:
            partes.append(f'faltam {vendas_faltam} {"venda" if vendas_faltam == 1 else "vendas"}')
        if proximo_req[1] > 0 and self.media < proximo_req[1]:
            partes.append(f'nota ≥ {proximo_req[1]} (atual: {self.media})')

        return ' e '.join(partes) if partes else None