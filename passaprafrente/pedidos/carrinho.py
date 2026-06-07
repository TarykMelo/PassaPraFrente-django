from produtos.models import Produto

class Carrinho:
    def __init__(self, request):
        self.session = request.session
        if 'carrinho' not in self.session:
            self.session['carrinho'] = []
        self.carrinho = self.session['carrinho']
    
    def adicionar(self, produto_id):
        """
        Adicionar um produto ao carrinho de compras
        """
        if produto_id not in self.carrinho:
            self.carrinho.append(produto_id)
            self.salvar()

    def remover(self, produto_id):
        """
        Remove um produto do carrinho
        """
        if produto_id in self.carrinho:
            self.carrinho.remove(produto_id)
            self.salvar()
    
    def salvar(self):
        """
        Marca a sessão como modificada para o Django salvar
        """
        self.session.modified = True

    def limpar(self):
        """
        Esvazia o carrinho
        """
        self.session['carrinho'] = []
        self.salvar()

    def produtos(self, usuario):
        """
        Retorna os produtos do carrinho
        """
        return Produto.objects.filter(
            id__in=self.carrinho
        ).exclude(vendedor=usuario)
    
    def total(self, usuario):
        """
        Retorna o valor total dos produtos no carrinho
        """
        return sum(p.preco for p in self.produtos(usuario))
    
    def __len__(self):
        """
        Retorna a quantidade de produtos no carrinho
        """
        return len(self.carrinho)