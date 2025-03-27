#!/usr/bin/env python3
"""
Script to fix the endpoint mismatch in the dashboard.html file.
This script updates the fetch URL from '/auth/update-profile' to '/auth/update-name'
to match the backend endpoint.
"""

import os

def fix_dashboard_html():
    """Fix the endpoint in dashboard.html"""
    file_path = os.path.join('frontend', 'dashboard.html')
    
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Update the endpoint from update-profile to update-name
    updated_content = content.replace(
        '`${API_BASE_URL}/auth/update-profile`',
        '`${API_BASE_URL}/auth/update-name`'
    )
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(updated_content)
    
    print(f"Fixed endpoint in {file_path}")

def main():
    """Main function to fix the endpoint"""
    print("Starting to fix endpoint mismatch...")
    
    # Fix the dashboard.html file
    fix_dashboard_html()
    
    print("Endpoint mismatch has been fixed!")

if __name__ == "__main__":
    main()
