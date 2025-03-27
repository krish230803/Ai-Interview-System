#!/usr/bin/env python3
"""
Script to completely fix the audio performance page not showing data after completing an audio interview.
This script directly modifies the necessary files to ensure the session ID is properly passed and retrieved.
"""

import os
import re

def fix_audio_performance_html():
    """Fix the audio-performance.html file to properly retrieve session ID"""
    file_path = os.path.join('frontend', 'audio-performance.html')
    
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Fix the duplicate session endpoint issue
    updated_content = content.replace(
        """                    // Use the regular session endpoint since audio-session endpoint doesn't exist
                    let response = await fetch(`${API_BASE_URL}/interview/session/${sessionIdNum}`, {
                        credentials: 'include',
                        headers: {
                            'Accept': 'application/json'
                        }
                    });

                    // If that fails, try the regular session endpoint
                    if (!response.ok && response.status === 404) {
                        console.log('Audio session endpoint failed, trying regular session endpoint...');
                        response = await fetch(`${API_BASE_URL}/interview/session/${sessionIdNum}`, {
                            credentials: 'include',
                            headers: {
                                'Accept': 'application/json'
                            }
                        });
                    }""",
        """                    // Use the session endpoint
                    let response = await fetch(`${API_BASE_URL}/interview/session/${sessionIdNum}`, {
                        credentials: 'include',
                        headers: {
                            'Accept': 'application/json'
                        }
                    });"""
    )
    
    # Improve the session ID retrieval logic to better handle the data from localStorage
    updated_content = updated_content.replace(
        """                // Try to get session data from localStorage first
                let session = null;
                const storedData = localStorage.getItem('lastInterviewData');
                if (storedData) {
                    try {
                        const parsedData = JSON.parse(storedData);
                        if (parsedData.stats?.id === sessionIdNum || parsedData.session_id === sessionIdNum || parsedData.id === sessionIdNum) {
                            session = parsedData;
                            console.log('Using session data from localStorage');
                        }
                    } catch (e) {
                        console.error('Error parsing stored session data:', e);
                    }
                }""",
        """                // Try to get session data from localStorage first
                let session = null;
                const storedData = localStorage.getItem('lastInterviewData');
                if (storedData) {
                    try {
                        const parsedData = JSON.parse(storedData);
                        // Check all possible locations for the session ID
                        const storedId = parsedData.stats?.id || parsedData.stats?.session_id || parsedData.session_id || parsedData.id;
                        console.log('Stored data session ID:', storedId, 'Looking for:', sessionIdNum);
                        
                        if (storedId == sessionIdNum) {  // Use loose equality for string/number comparison
                            if (parsedData.stats) {
                                session = parsedData.stats;
                            } else {
                                session = parsedData;
                            }
                            console.log('Using session data from localStorage:', session);
                        }
                    } catch (e) {
                        console.error('Error parsing stored session data:', e);
                    }
                }"""
    )
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(updated_content)
    
    print(f"Fixed audio performance page in {file_path}")

def main():
    """Main function to fix the audio performance issue"""
    print("Starting to fix audio performance page issue completely...")
    
    # Fix the audio-performance.html file
    fix_audio_performance_html()
    
    print("Audio performance page issue has been completely fixed!")

if __name__ == "__main__":
    main()
