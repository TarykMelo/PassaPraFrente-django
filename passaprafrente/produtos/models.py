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
    vendido = models.BooleanField(default=False)
    vendedor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='produtos'
    )

    def __str__(self):
        return self.nome
    
    def preco_formatado(self):
        return f"R$ {self.preco:.2f}"

class ImagemProduto(models.Model):
    produto = models.ForeignKey(
        Produto, on_delete=models.CASCADE,
        related_name='imagens'
    )
    imagem = models.ImageField(upload_to='produtos/')

class Denuncia(models.Model):
    MOTIVOS_CHOICES = [
        ('GOLPE', 'Suspeita de Golpe ou Fraude'),
        ('ILEGAL', 'Produto Ilegal ou Proibido'),
        ('OFENSIVO', 'Conteúdo Ofensivo ou Inadequado'),
        ('PRECO', 'Preço Abusivo ou Irreal'),
        ('OUTRO', 'Outro Motivo'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='denuncias_feitas'
    )
   
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='denuncias')
    
    motivo = models.CharField(max_length=20, choices=MOTIVOS_CHOICES)
    descricao = models.TextField(verbose_name="Detalhes da denúncia", blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    resolvido = models.BooleanField(default=False) 

    def __str__(self):
        return f"Denúncia do produto {self.produto.nome} - Motivo: {self.get_motivo_display()}"