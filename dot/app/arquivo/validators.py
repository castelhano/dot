import os
from django.core.exceptions import ValidationError

def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.pdf', '.doc', '.docx','.odt','.png','.jpg','.xls','.xlsx','.mp4']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Tipo de arquivo não suportado')