from django import forms 
from .models import Snippet, Entry


class SnippetForm(forms.ModelForm):

    class Meta: 
        model = Entry 
        fields = ('region',)