import os

def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path + filename
    valid_extensions = ['.png','.jpg','.jpeg']
    if not ext.lower() in valid_extensions:
        return False
    else:
        return True