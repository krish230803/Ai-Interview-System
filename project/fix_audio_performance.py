#!/usr/bin/env python3
"""
Script to fix the audio performance page not showing data after completing an interview.
This script modifies the audio-interview.html file to redirect to the audio-performance.html
page when an interview is completed, instead of showing a dashboard within the same page.
"""

import os

def fix_audio_interview_html():
    """Fix the audio-interview.html file to redirect to audio-performance.html"""
    file_path = os.path.join('frontend', 'audio-interview.html')
    
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Find the line where showDashboard is called when interview is completed
    # and replace it with a redirect to audio-performance.html
    updated_content = content.replace(
        'if (data.completed) {\n                        showDashboard(data.stats);',
        'if (data.completed) {\n                        // Redirect to audio performance page instead of showing dashboard\n                        localStorage.setItem("lastInterviewData", JSON.stringify(data.stats));\n                        localStorage.setItem("lastInterviewSession", data.stats.id);\n                        window.location.href = `audio-performance.html?session=${data.stats.id}`;'
    )
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(updated_content)
    
    print(f"Fixed audio interview redirect in {file_path}")

def fix_audio_performance_html():
    """Fix the audio-performance.html file to properly retrieve session ID"""
    file_path = os.path.join('frontend', 'audio-performance.html')
    
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Update the loadPerformanceData function to handle the session ID correctly
    # Find the part where it tries to fetch from audio-session endpoint
    updated_content = content.replace(
        '                    // First try the audio-session endpoint\n                    let response = await fetch(`${API_BASE_URL}/interview/audio-session/${sessionIdNum}`, {',
        '                    // Use the regular session endpoint since audio-session endpoint doesn\'t exist\n                    let response = await fetch(`${API_BASE_URL}/interview/session/${sessionIdNum}`, {'
    )
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(updated_content)
    
    print(f"Fixed audio performance page in {file_path}")

def main():
    """Main function to fix the audio performance issue"""
    print("Starting to fix audio performance page issue...")
    
    # Fix the audio-interview.html file
    fix_audio_interview_html()
    
    # Fix the audio-performance.html file
    fix_audio_performance_html()
    
    print("Audio performance page issue has been fixed!")

if __name__ == "__main__":
    main()
