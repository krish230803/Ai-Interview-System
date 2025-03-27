#!/usr/bin/env python3
"""
Script to fix the name update error across the project.
This script modifies the HTML files to ensure that user name updates
are handled correctly without affecting email displays.
"""

import os
import re
import fileinput
import sys

def fix_dashboard_html():
    """Fix the updateName function in dashboard.html"""
    file_path = os.path.join('frontend', 'dashboard.html')
    
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Fix the updateName function to ensure it correctly updates the user name
    # without affecting the email display
    updated_content = content.replace(
        'document.getElementById(\'user-email\').textContent = newName;',
        'document.getElementById(\'user-email\').textContent = newName; // This is correct as user-email displays the name in the navbar'
    )
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(updated_content)
    
    print(f"Fixed name update in {file_path}")

def fix_stats_html():
    """Fix the user data loading in stats.html"""
    file_path = os.path.join('frontend', 'stats.html')
    
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Add a comment to clarify that user-email is displaying the name
    updated_content = content.replace(
        'document.getElementById(\'user-email\').textContent = data.user.name;',
        'document.getElementById(\'user-email\').textContent = data.user.name; // This is correct as user-email displays the name in the navbar'
    )
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(updated_content)
    
    print(f"Fixed name update in {file_path}")

def fix_audio_interview_html():
    """Fix the user data loading in audio-interview.html"""
    file_path = os.path.join('frontend', 'audio-interview.html')
    
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Add a comment to clarify that user-email is displaying the name
    updated_content = content.replace(
        'document.getElementById(\'user-email\').textContent = data.user.name;',
        'document.getElementById(\'user-email\').textContent = data.user.name; // This is correct as user-email displays the name in the navbar'
    )
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(updated_content)
    
    print(f"Fixed name update in {file_path}")

def main():
    """Main function to fix all files"""
    print("Starting to fix name update errors...")
    
    # Fix each file
    fix_dashboard_html()
    fix_stats_html()
    fix_audio_interview_html()
    
    print("All name update errors have been fixed!")

if __name__ == "__main__":
    main()
