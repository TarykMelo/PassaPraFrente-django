from groq import Groq
from django.conf import settings

class ModeracaoMensagem:
    @staticmethod
    def verificar(conteudo):
        """
        LLM que verifica se a mensagem tem indicio de golpe.
        Retorna (permitido, motivo)
        """
        try:
            cliente = Groq(api_key=settings.GROQ_API_KEY)
            resposta = cliente.chat.completions.create(
                model="llama-3.1-8b-instant",
                max_tokens=50,
                messages=[
                    {
                        "role": "system",
                        "content": """Você é um moderador de mensagens de um marketplace universitário brasileiro.
                        Analise se a mensagem tem indício de golpe, fraude ou comportamento suspeito.
                        Exemplos de golpe: pedir para continuar conversa fora da plataforma, 
                        pedir dados bancários, pedir PIX antes da entrega, links suspeitos,
                        pressão para fechar negócio rápido fora do sistema.
                        Responda APENAS com JSON no formato:
                        {"permitido": true, "motivo": ""}
                        ou
                        {"permitido": false, "motivo": "motivo curto aqui"}"""
                    },
                    {
                        "role": "user",
                        "content": f"Mensagem: {conteudo}"
                    }
                ]
            )

            import json
            texto = resposta.choices[0].message.content.strip()
            resultado = json.loads(texto)
            return resultado.get('permitido', True), resultado.get('motivo', '')
        
        except Exception as e:
            print(f"Erro na moderação: {e}")
            return True, ''