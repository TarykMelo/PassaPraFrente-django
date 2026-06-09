import re
from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .models import Usuario

class CadastroForm(UserCreationForm):
    """
    Função de cadastro do usuário e suas validações
    """

    email = forms.EmailField(label="Email institucional")
    nickname = forms.CharField(max_length=50, label="Nickname")
    telefone = forms.CharField(max_length=11, label="Telefone")

    class Meta:
        model = Usuario
        fields = ['email', 'nickname', 'telefone', 'password1', 'password2']
    

    def clean_email(self):
        email = self.cleaned_data['email']
        if not re.match(r'^[a-zA-Z]+\.[a-zA-Z]+@ufrpe\.br$', email):
            raise forms.ValidationError("Use o padrão nome.sobrenome@ufrpe.br")
        return email
    
    def clean_password1(self):
        senha = self.cleaned_data.get('password1')
        erros = validar_senha(senha)

        if erros:
            raise forms.ValidationError(erros)
        
        return senha

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("As duas senhas não combinam")
        return password2
    
    def clean_nickname(self):
        nick = self.cleaned_data['nickname']
        if ' ' in nick:
            raise forms.ValidationError("Nickname não pode ter espaços, use _")
        return nick

    def clean_telefone(self):
        tel = self.cleaned_data['telefone']
        if not re.match(r'^\(?81\)?[\s-]?\d{4,5}-?\d{4}$', tel):
            raise forms.ValidationError("Use o formato (81) XXXXX-XXXX")
        return tel
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        if commit:
            user.save()
        return user
    
class NicknameForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nickname']
        labels = {'nickname': 'Novo nickname'}

    def clean_nickname(self):
        nick = self.cleaned_data.get('nickname')
        if ' ' in nick:
            raise forms.ValidationError("Nickname não pode ter espaços, use _")
        return nick
    
class TelefoneForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['telefone']
        labels = {'telefone': 'Novo telefone'}

    def clean_telefone(self):
        tel = self.cleaned_data.get('telefone')
        if not re.match(r'^\(?81\)?[\s-]?\d{4,5}-?\d{4}$', tel):
            raise forms.ValidationError("Use o formato (81) XXXXX-XXXX")
        return tel

class SenhaForm(PasswordChangeForm):
    error_messages = {
        'password_incorrect': 'Senha atual incorreta',
        'password_mismatch': 'As senhas não coincidem',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].validators = []
        self.fields['new_password1'].help_text = ''

    def clean_new_password1(self):
        senha = self.cleaned_data.get('new_password1')
        erros = validar_senha(senha)
        if erros:
            raise forms.ValidationError(erros)
        return senha


def validar_senha(senha):
    erros = []

    if len(senha) < 8:
        erros.append("A senha precisa ter pelo menos 8 caracteres")
    if not re.search(r"[A-Z]", senha):
        erros.append("A senha precisa ter pelo menos uma letra maiúscula")
    if not re.search(r"[0-9]", senha):
        erros.append("A senha precisa ter pelo menos um número")
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", senha):
        erros.append("A senha precisa ter pelo menos um símbolo")
    if re.search(r"\s", senha):
        erros.append("A senha não pode conter espaços")
    if re.search(r"[À-ÿ]", senha):
        erros.append("A senha não pode conter caracteres acentuados")

    return erros