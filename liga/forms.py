from django import forms
from .models import Jugador

class JugadorPerfilForm(forms.ModelForm):
    class Meta:
        model = Jugador
        # Especificamos solo los campos que el usuario puede editar
        fields = ['nickname_pokemmo', 'avatar', 'lema']
        
        # Añadimos estilos de Bootstrap a los campos
        widgets = {
            'nickname_pokemmo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu nick en PokeMMO'}),
            'lema': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Una frase épica (máx. 200 caract.)', 'rows': 3}),
            'avatar': forms.FileInput(attrs={'class': 'form-control-file'}), # Específico para archivos
        }