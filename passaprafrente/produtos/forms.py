from django import forms
from produtos.models import Produto

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