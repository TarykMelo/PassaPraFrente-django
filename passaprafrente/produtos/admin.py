from django.contrib import admin
from .models import Produto, Denuncia

admin.site.register(Produto)

@admin.register(Denuncia)
class DenunciaAdmin(admin.ModelAdmin):
    list_display  = ('id', 'produto', 'get_vendedor', 'motivo', 'resolvido', 'criado_em')
    list_filter   = ('resolvido', 'criado_em')
    list_editable = ('resolvido',)
    search_fields = ('motivo', 'produto__nome')

    def get_vendedor(self, obj):
        return obj.produto.vendedor
    get_vendedor.short_description = 'Vendedor Denunciado'