"""
Fetch All Users Script
This script displays all users in the database
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xyz_store.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def fetch_all_users():
    """Fetch and display all users"""
    print("=" * 80)
    print("All Users in Database")
    print("=" * 80)
    
    users = User.objects.all().order_by('date_joined')
    total_users = users.count()
    
    if total_users == 0:
        print("\nNo users found in database.")
        return
    
    print(f"\nTotal Users: {total_users}")
    print("\nNOTE: Passwords are hashed in database (cannot be retrieved)")
    print("      Sample customers created by restore script use password: 'customer123'")
    print()
    
    # Separate superusers and regular users
    superusers = users.filter(is_superuser=True)
    regular_users = users.filter(is_superuser=False)
    
    if superusers.exists():
        print(f"SUPERUSERS ({superusers.count()}):")
        print("-" * 80)
        for user in superusers:
            status = "Active" if user.is_active else "Inactive"
            print(f"  Username: {user.username}")
            print(f"  Password: [Django hashed - cannot retrieve]")
            print(f"  Email:    {user.email}")
            print(f"  Name:     {user.get_full_name() or 'N/A'}")
            print(f"  Status:   {status}")
            print(f"  Joined:   {user.date_joined.strftime('%Y-%m-%d %H:%M:%S')}")
            print()
    
    if regular_users.exists():
        print(f"REGULAR USERS ({regular_users.count()}):")
        print("-" * 80)
        for user in regular_users:
            status = "Active" if user.is_active else "Inactive"
            staff = " (Staff)" if user.is_staff else ""
            print(f"  Username: {user.username}{staff}")
            print(f"  Password: customer123 (default for restored users)")
            print(f"  Email:    {user.email}")
            print(f"  Name:     {user.get_full_name() or 'N/A'}")
            print(f"  Status:   {status}")
            print(f"  Joined:   {user.date_joined.strftime('%Y-%m-%d %H:%M:%S')}")
            print()
    
    print("=" * 80)
    print(f"Summary: {superusers.count()} superuser(s), {regular_users.count()} regular user(s)")
    print("=" * 80)

if __name__ == '__main__':
    fetch_all_users()
