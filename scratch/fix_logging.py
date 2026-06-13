import os

settings_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'settings.py')

with open(settings_path, 'rb') as f:
    content = f.read()

old = b"""    'loggers': {
        'core': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },"""

new = b"""    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'core': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },"""

if old in content:
    content = content.replace(old, new)
    with open(settings_path, 'wb') as f:
        f.write(content)
    print("OK: LOGGING updated successfully")
else:
    print("WARNING: pattern not found, trying with \\r\\n")
    old_rn = old.replace(b'\n', b'\r\n')
    new_rn = new.replace(b'\n', b'\r\n')
    if old_rn in content:
        content = content.replace(old_rn, new_rn)
        with open(settings_path, 'wb') as f:
            f.write(content)
        print("OK: LOGGING updated successfully (CRLF)")
    else:
        print("ERROR: could not find the logging block to replace")
