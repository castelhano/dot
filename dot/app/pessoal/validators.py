import os
from django.core.exceptions import ValidationError


def cpf_valid(cpf):
    # VALIDA CPF JA MASCARADO
    if (not cpf) or (len(cpf) < 14) or (not '.' in cpf) or (not '-' in cpf):
        return False
    else:
        return True

def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.pdf', '.doc', '.docx','.odt','.png','.jpg','.xls','.xlsx']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Tipo de arquivo não suportado')