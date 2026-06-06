from django.contrib import admin
from .models import Produto, Denuncia 


admin.site.register(Produto)
# Register your models here.

class DenunciaAdmin(admin.ModelAdmin):
    list_display = ('id', 'produto', 'get_vendedor', 'status', 'criado_em')
    
    list_filter = ('status', 'criado_em')
    
    list_editable = ('status',)
    
    search_fields = ('motivo', 'produto__nome')

    def get_vendedor(self, obj):
        return obj.produto.vendedor
    get_vendedor.short_description = 'Vendedor Denunciado'