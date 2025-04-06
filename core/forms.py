from django import forms
from .models import Pelada

class PeladaForm(forms.ModelForm):
    recorrente = forms.BooleanField(
        required=False,
        label='Pelada semanal?',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    semanas_duracao = forms.IntegerField(
        required=False,
        label='Número de semanas',
        min_value=1,
        max_value=52,
        initial=4,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Quantas semanas?',
            'style': 'display: none;'  # Escondido por padrão
        })
    )

    class Meta:
        model = Pelada
        fields = ['nome', 'data', 'hora', 'local', 'recorrente', 'semanas_duracao']
        widgets = {
            'data': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'id': 'data-field'
            }),
            'hora': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),  
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome da pelada'
            }),
            'local': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Local do jogo'
            })
        }
        labels = {
            'nome': 'Nome da Pelada',
            'data': 'Data do Jogo',
            'hora': 'Horário',  
            'local': 'Local'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Se estiver editando uma pelada existente, mostra o campo de semanas se for recorrente
        if self.instance and self.instance.recorrente:
            self.fields['semanas_duracao'].widget.attrs['style'] = 'display: block;'

    def clean(self):
        cleaned_data = super().clean()
        recorrente = cleaned_data.get('recorrente')
        semanas_duracao = cleaned_data.get('semanas_duracao')
        
        if recorrente and not semanas_duracao:
            cleaned_data['semanas_duracao'] = 4  # Valor padrão
        elif recorrente and semanas_duracao < 1:
            self.add_error('semanas_duracao', 'O número de semanas deve ser pelo menos 1')
        
        return cleaned_data