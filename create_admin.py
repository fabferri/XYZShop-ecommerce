import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xyz_store.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Create superuser if it doesn't exist
username = 'admin'
email = 'admin@xyzshop.com'
password = 'admin123'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f'\n[SUCCESS] Superuser created successfully!')
    print(f'\nAdmin Credentials:')
    print(f'   Username: {username}')
    print(f'   Password: {password}')
    print(f'\nLogin at: http://127.0.0.1:8000/admin/')
else:
    print(f'\n[INFO] Superuser "{username}" already exists.')
    print(f'\nUse these credentials:')
    print(f'   Username: {username}')
    print(f'   Password: {password}')
