import os

def validate_excluded_files(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path + filename
    excluded_extensions = ['.exe','.bat','.js']
    if ext.lower() in excluded_extensions:
        return False
    else:
        return True

def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path + filename
    valid_extensions = ['.png','.jpg']
    if not ext.lower() in valid_extensions:
        return False
    else:
        return True