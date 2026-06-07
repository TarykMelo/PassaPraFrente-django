from groq import Groq
from django.conf import settings

def recomendar_produtos(usuario, produtos_disponiveis):
    from pedidos.models import Pedido

    pedidos_recentes = Pedido.objects.filter(
        comprador=usuario,
        status='finalizado'
    ).select_related('produto')[:5]

    if not pedidos_recentes:
        return []
    
    historico = "\n".join([
        f"- {pedido.produto.nome} (categoria: {pedido.produto.categoria})"
        for pedido in pedidos_recentes
    ])

    catalogo = "\n".join([
        f"- ID:{produto.id} | Nome:{produto.nome} | Categoria:{produto.categoria} | Preço:R${produto.preco}"
        for produto in produtos_disponiveis
    ])

    if not catalogo:
        return []
    
    try:
        cliente = Groq(api_key=settings.GROQ_API_KEY)
        resposta = cliente.chat.completions.create(
            model="llama-3.1-8b-instant",
            max_tokens=512,
            messages=[
                {
                    "role": "system",
                    "content": "Você é um sistema de recomendação de produtos. Responda APENAS com IDs numéricos separados por vírgula, sem texto adicional."
                },
                {
                    "role": "user",
                    "content": f"""
                        O usuário comprou recentemente:
                        {historico}

                        Produtos dispomíveis:
                        {catalogo}

                        Recomende até 3 IDS de produtos do catálogo que o usuário provavelmente vai gostar
                        Responda APENAS com os IDS separados por vírgula.
                        Exepmlo: 12,45,67
                    """
                }
            ]
        )

        texto = resposta.choices[0].message.content.strip()
        ids = [int(i.strip()) for i in texto.split(',') if i.strip().isdigit()]
        return list(produtos_disponiveis.filter(id__in=ids))
    
    except Exception as e:
        print(f"Erro ao recomendar produtos: {e}")
        return []