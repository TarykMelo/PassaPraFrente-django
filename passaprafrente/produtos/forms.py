from django import forms
from produtos.models import Produto
from pedidos.models import Feedback

class ProdutoForm(forms.ModelForm):

    class Meta:
        model = Produto
        fields = ['nome', 'descricao', 'preco', 'categoria', 'imagem']
        labels = {
            'nome': 'Nome do produto',
            'descricao': 'Descrição',
            'preco': 'Preço(R$)',
            'categoria' : 'Categoria',
            'imagem' : 'Foto do produto',
        }

    def clean_preco(self):
        preco = self.cleaned_data.get('preco')
        if preco <= 0:
            raise forms.ValidationError("O preço precisa ser maior do que zero")
        return preco
    
    def clean_nome(self):
        nome = self.cleaned_data.get('nome')
        if not nome:
            raise forms.ValidationError("O nome não pode ser vazio")
        return nome
    

class FeedbackForm(forms.ModelForm): 

    class Meta: 
        model = Feedback 
        fields = ['nota', 'comentario']
        widgets = {
            'nota': forms.Select(attrs={'class': 'form-control', 'rows':3, 'placeholder': 'Conte como foi sua experiência...'}),
        }