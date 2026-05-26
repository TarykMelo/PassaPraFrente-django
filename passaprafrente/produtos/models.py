from django.db import models
from django.conf import settings

CATEGORIAS = [
    ('Eletrônicos', 'Eletrônicos'),
    ('Esportes', 'Esportes'),
    ('Livros', 'Livros'),
    ('Roupas', 'Roupas'),
    ('Móveis', 'Móveis'),
    ('Comidas', 'Comidas'),
    ('Utilidades', 'Utilidades'),
    ('Acessórios', 'Acessórios')
]

class Produto(models.Model):
    nome = models.CharField(max_length=200)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.CharField(max_length=50, choices=CATEGORIAS)
    imagem = models.ImageField(upload_to='produtos/', blank=True, null=True)
    vendedor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='produtos'
    )

    def __str__(self):
        return self.nome
    
    def preco_formatado(self):
        return f"R$ {self.preco:.2f}"

    