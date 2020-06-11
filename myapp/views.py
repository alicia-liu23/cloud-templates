from django.shortcuts import render
from django.http import HttpResponse
from .forms import SnippetForm
from .models import Entry
from envyaml import EnvYAML
from python_terraform import * 

import json 
import yaml
import io
import os
import re 

def contact(request):
    return HttpResponse("Hello, world")

# modifies terraform template with user input 
def terraform_form(request):

    if request.method == "POST": 
        form = SnippetForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['region']
            form.save()

            # with override file and json serializer 
            with open('terraform_template_override.tf.json') as f:
                data = json.load(f)
            data['provider']['aws']['region'] = name
            with open('terraform_template_override.tf.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            
            # with variable file 
            with open('terraform_template.tfvars.json') as f:
                data = json.load(f)
            data['NAME'] = name 
            with open('terraform_template.tfvars.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            
    form = SnippetForm()
    return render(request, 'form.html', {'form':form})

# modifies loader for yaml Loader function (method 3)
path_matcher = re.compile(r'\$\{([^}^{]+)\}')
def path_constructor(loader, node):
  ''' Extract the matched value, expand env variable, and replace the match '''
  value = node.value
  match = path_matcher.match(value)
  env_var = match.group()[2:-1]
  return os.environ.get(env_var) + value[match.end():]

yaml.add_implicit_resolver('!path', path_matcher)
yaml.add_constructor('!path', path_constructor)

# renders form that modifies .yaml templates 
def yaml_form(request):

    if request.method == "POST": 
        form = SnippetForm(request.POST)
        if form.is_valid():
            form.save()
            name = form.cleaned_data['region']
            
            # with yaml library 
            with open("template.yaml", 'r') as stream:
                data_loaded = yaml.safe_load(stream)
                data_loaded['Resources']['MyEC2Instance']['Properties']['AvailabilityZone'] = name
            
            with open("new_template.yaml", "w") as f:
                yaml.dump(data_loaded, f)
            
            # with env variables and envyaml library (env variables in template must be referenced with $VAR)
            os.environ['NAME'] = name 
            data = EnvYAML('template.yaml')
            print(data)
            with open("new_template.yaml", "w") as f:
                yaml.dump(data['Resources'], f)
            
            # with yaml.add_implicit_resolver and yaml.add_constructor (env variables in template mus be referenced with ${VAR})           
            os.environ['NAME'] = name 
            with open('template.yaml', 'r') as stream: 
                p = yaml.load(stream, Loader=yaml.FullLoader)
            print(p['Resources'])
            with open("new_template.yaml", "w") as f:
                yaml.dump(p, f)
            
    form = SnippetForm()
    return render(request, 'form.html', {'form':form})
