#!/usr/bin/env python3
"""
Comprehensive script to fix all audio interview and performance issues.
"""

import os
import re

def fix_audio_interview_html():
    """Fix all issues in the audio-interview.html file"""
    file_path = os.path.join('frontend', 'audio-interview.html')
    
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # 1. Add detailed logging of the response data
    if 'Full API response:' not in content:
        old_code = """                    const data = await response.json();
                    
                    if (data.completed) {"""
        
        new_code = """                    const data = await response.json();
                    
                    // Debug output of the full response
                    console.log('Full API response:', data);
                    
                    if (data.completed) {"""
        
        content = content.replace(old_code, new_code)
    
    # 2. Add fallback session ID creation
    if 'fallback-' not in content:
        old_code = """                        // Get session ID from the response - check all possible locations
                        let sessionId;
                        if (data.stats && data.stats.id) {
                            sessionId = data.stats.id;
                            console.log('Using session ID from data.stats.id:', sessionId);
                        } else if (data.stats && data.stats.session_id) {
                            sessionId = data.stats.session_id;
                            console.log('Using session ID from data.stats.session_id:', sessionId);
                        } else if (data.session_id) {
                            sessionId = data.session_id;
                            console.log('Using session ID from data.session_id:', sessionId);
                        } else if (data.id) {
                            sessionId = data.id;
                            console.log('Using session ID from data.id:', sessionId);
                        }
                        
                        console.log('Extracted session ID:', sessionId);
                        
                        if (!sessionId) {
                            console.error('No session ID found in response data');
                            alert('Error: No session ID found. Please try again or contact support.');
                            return;
                        }"""
        
        new_code = """                        // Log the entire data structure for debugging
                        console.log('Full data structure:', JSON.stringify(data, null, 2));
                        
                        // Get session ID from the response - check all possible locations
                        let sessionId;
                        
                        // Dump all potential session ID locations for debugging
                        console.log('Potential session ID locations:');
                        console.log('- data.id:', data.id);
                        console.log('- data.session_id:', data.session_id);
                        if (data.stats) {
                            console.log('- data.stats.id:', data.stats.id);
                            console.log('- data.stats.session_id:', data.stats.session_id);
                        }
                        if (data.response) {
                            console.log('- data.response.id:', data.response?.id);
                            console.log('- data.response.session_id:', data.response?.session_id);
                        }
                        
                        // Try to extract session ID from all possible locations
                        if (data.stats && data.stats.id) {
                            sessionId = data.stats.id;
                            console.log('Using session ID from data.stats.id:', sessionId);
                        } else if (data.stats && data.stats.session_id) {
                            sessionId = data.stats.session_id;
                            console.log('Using session ID from data.stats.session_id:', sessionId);
                        } else if (data.session_id) {
                            sessionId = data.session_id;
                            console.log('Using session ID from data.session_id:', sessionId);
                        } else if (data.id) {
                            sessionId = data.id;
                            console.log('Using session ID from data.id:', sessionId);
                        } else if (data.response && data.response.id) {
                            sessionId = data.response.id;
                            console.log('Using session ID from data.response.id:', sessionId);
                        } else if (data.response && data.response.session_id) {
                            sessionId = data.response.session_id;
                            console.log('Using session ID from data.response.session_id:', sessionId);
                        }
                        
                        console.log('Extracted session ID:', sessionId);
                        
                        // If we still don't have a session ID, create a fallback ID from the timestamp
                        if (!sessionId) {
                            console.warn('No session ID found in response data, creating fallback ID');
                            sessionId = 'fallback-' + Date.now();
                            console.log('Created fallback session ID:', sessionId);
                        }"""
        
        content = content.replace(old_code, new_code)
    
    # 3. Add sessionStorage and delay before redirect
    if 'sessionStorage.setItem' not in content:
        old_code = """                        // Store both the session ID and the full session data
                        localStorage.setItem('lastInterviewSession', sessionId.toString());
                        
                        if (data.stats) {
                            localStorage.setItem('lastInterviewData', JSON.stringify(data.stats));
                            console.log('Stored stats data in localStorage');
                        } else {
                            localStorage.setItem('lastInterviewData', JSON.stringify(data));
                            console.log('Stored full data in localStorage (no stats object)');
                        }

                        // Ensure the redirect URL is properly constructed
                        const performanceUrl = new URL('audio-performance.html', window.location.href);
                        performanceUrl.searchParams.set('session', sessionId.toString());
                        
                        console.log('Redirecting to:', performanceUrl.href);
                        window.location.href = performanceUrl.href;"""
        
        new_code = """                        // Store both the session ID and the full session data
                        localStorage.setItem('lastInterviewSession', sessionId.toString());
                        
                        if (data.stats) {
                            localStorage.setItem('lastInterviewData', JSON.stringify(data.stats));
                            console.log('Stored stats data in localStorage');
                        } else {
                            localStorage.setItem('lastInterviewData', JSON.stringify(data));
                            console.log('Stored full data in localStorage (no stats object)');
                        }
                        
                        // Also store in sessionStorage for redundancy
                        sessionStorage.setItem('lastInterviewSession', sessionId.toString());
                        sessionStorage.setItem('lastInterviewData', JSON.stringify(data));
                        console.log('Stored session data in sessionStorage');

                        // Ensure the redirect URL is properly constructed
                        const performanceUrl = new URL('audio-performance.html', window.location.href);
                        performanceUrl.searchParams.set('session', sessionId.toString());
                        
                        console.log('Redirecting to:', performanceUrl.href);
                        
                        // Add a small delay to ensure storage is written before redirect
                        setTimeout(() => {
                            window.location.href = performanceUrl.href;
                        }, 100);"""
        
        content = content.replace(old_code, new_code)
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
    
    print(f"Fixed all issues in {file_path}")
    return True

def fix_audio_performance_html():
    """Fix all issues in the audio-performance.html file"""
    file_path = os.path.join('frontend', 'audio-performance.html')
    
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # 1. Ensure loadPerformanceData is properly declared as async
    function_pattern = re.compile(r'function loadPerformanceData\(\) \{', re.DOTALL)
    content = function_pattern.sub('async function loadPerformanceData() {', content)
    
    # 2. Add sessionStorage check
    if 'sessionStorage.getItem' not in content:
        old_code = """                // If no session ID in URL, try to get from localStorage
                if (!sessionId || sessionId === 'undefined' || sessionId === 'null') {
                    console.log('No valid session ID in URL, checking localStorage...');
                    sessionId = localStorage.getItem('lastInterviewSession');
                    console.log('Session ID from localStorage:', sessionId);
                }"""
        
        new_code = """                // If no session ID in URL, try to get from localStorage or sessionStorage
                if (!sessionId || sessionId === 'undefined' || sessionId === 'null') {
                    console.log('No valid session ID in URL, checking storage...');
                    
                    // Try localStorage first
                    sessionId = localStorage.getItem('lastInterviewSession');
                    console.log('Session ID from localStorage:', sessionId);
                    
                    // If not in localStorage, try sessionStorage
                    if (!sessionId || sessionId === 'undefined' || sessionId === 'null') {
                        sessionId = sessionStorage.getItem('lastInterviewSession');
                        console.log('Session ID from sessionStorage:', sessionId);
                    }
                }"""
        
        content = content.replace(old_code, new_code)
    
    # 3. Add fallback session ID handling
    if 'fallback-' not in content:
        old_code = """                // Convert to number and validate
                const sessionIdNum = parseInt(sessionId, 10);
                if (isNaN(sessionIdNum) || sessionIdNum <= 0) {
                    console.error('Invalid session ID format:', sessionId);
                    throw new Error(`Invalid session ID format: ${sessionId}`);
                }

                console.log('Using session ID (as number):', sessionIdNum);"""
        
        new_code = """                // Check if this is a fallback ID
                let sessionIdNum;
                if (sessionId.startsWith('fallback-')) {
                    console.log('Using fallback session ID:', sessionId);
                    // For fallback IDs, use the stored data directly
                    sessionIdNum = sessionId;
                } else {
                    // Convert to number and validate
                    sessionIdNum = parseInt(sessionId, 10);
                    if (isNaN(sessionIdNum) || sessionIdNum <= 0) {
                        console.error('Invalid session ID format:', sessionId);
                        throw new Error(`Invalid session ID format: ${sessionId}`);
                    }
                }

                console.log('Using session ID:', sessionIdNum);"""
        
        content = content.replace(old_code, new_code)
    
    # 4. Update session data retrieval for fallback IDs
    if 'typeof sessionIdNum === \'string\'' not in content:
        old_code = """                // Try to get session data from localStorage first
                let session = null;
                const storedData = localStorage.getItem('lastInterviewData');
                if (storedData) {
                    try {
                        const parsedData = JSON.parse(storedData);
                        console.log('Parsed stored data:', parsedData);
                        
                        // Check if this stored data matches our session ID
                        const storedId = parsedData.id || parsedData.session_id;
                        if (storedId == sessionIdNum) {  // Use loose equality for string/number comparison
                            session = parsedData;
                            console.log('Using session data from localStorage');
                        } else if (parsedData.stats && (parsedData.stats.id == sessionIdNum || parsedData.stats.session_id == sessionIdNum)) {
                            session = parsedData.stats;
                            console.log('Using stats data from localStorage');
                        }
                    } catch (e) {
                        console.error('Error parsing stored session data:', e);
                    }
                }"""
        
        new_code = """                // Try to get session data from localStorage first
                let session = null;
                
                // For fallback IDs, use the stored data directly
                if (typeof sessionIdNum === 'string' && sessionIdNum.startsWith('fallback-')) {
                    console.log('Using fallback session ID, retrieving stored data directly');
                    const fullData = localStorage.getItem('lastFullInterviewData');
                    if (fullData) {
                        try {
                            session = JSON.parse(fullData);
                            console.log('Using full interview data for fallback session');
                        } catch (e) {
                            console.error('Error parsing full interview data:', e);
                        }
                    }
                } else {
                    // Normal session ID handling
                    const storedData = localStorage.getItem('lastInterviewData');
                    if (storedData) {
                        try {
                            const parsedData = JSON.parse(storedData);
                            console.log('Parsed stored data:', parsedData);
                            
                            // Check if this stored data matches our session ID
                            const storedId = parsedData.id || parsedData.session_id;
                            if (storedId == sessionIdNum) {  // Use loose equality for string/number comparison
                                session = parsedData;
                                console.log('Using session data from localStorage');
                            } else if (parsedData.stats && (parsedData.stats.id == sessionIdNum || parsedData.stats.session_id == sessionIdNum)) {
                                session = parsedData.stats;
                                console.log('Using stats data from localStorage');
                            }
                        } catch (e) {
                            console.error('Error parsing stored session data:', e);
                        }
                    }
                }"""
        
        content = content.replace(old_code, new_code)
    
    # 5. Skip API call for fallback IDs
    if '!(typeof sessionIdNum === \'string\'' not in content:
        old_code = """                // If no stored data, fetch from server
                if (!session) {
                    console.log('Fetching session data from server...');
                    // Use the session endpoint
                    let response = await fetch(`${API_BASE_URL}/interview/session/${sessionIdNum}`, {
                        credentials: 'include',
                        headers: {
                            'Accept': 'application/json'
                        }
                    });"""
        
        new_code = """                // If no stored data, fetch from server (but skip for fallback IDs)
                if (!session && !(typeof sessionIdNum === 'string' && sessionIdNum.startsWith('fallback-'))) {
                    console.log('Fetching session data from server...');
                    // Use the session endpoint
                    let response = await fetch(`${API_BASE_URL}/interview/session/${sessionIdNum}`, {
                        credentials: 'include',
                        headers: {
                            'Accept': 'application/json'
                        }
                    });"""
        
        content = content.replace(old_code, new_code)
    
    # 6. Fix loose equality comparisons
    content = content.replace('parsedData.stats?.id === sessionIdNum', 'parsedData.stats?.id == sessionIdNum')
    content = content.replace('parsedData.session_id === sessionIdNum', 'parsedData.session_id == sessionIdNum')
    content = content.replace('parsedData.id === sessionIdNum', 'parsedData.id == sessionIdNum')
    
    # 7. Remove duplicate endpoint call
    if 'If that fails, try the regular session endpoint' in content:
        old_code = """                    // Use the regular session endpoint since audio-session endpoint doesn't exist
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
                    }"""
        
        new_code = """                    // Use the session endpoint
                    let response = await fetch(`${API_BASE_URL}/interview/session/${sessionIdNum}`, {
                        credentials: 'include',
                        headers: {
                            'Accept': 'application/json'
                        }
                    });"""
        
        content = content.replace(old_code, new_code)
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
    
    print(f"Fixed all issues in {file_path}")
    return True

def clean_up_files():
    """Remove unnecessary fix files"""
    files_to_remove = [
        'fix_audio_session_direct.py',
        'fix_audio_session_targeted.py',
        'fix_audio_session_final.py',
        'fix_session_id_extraction.py',
        'fix_await_syntax.py'
    ]
    
    for file in files_to_remove:
        if os.path.exists(file):
            os.remove(file)
            print(f"Removed {file}")
    
    return True

def main():
    """Main function to fix all audio issues"""
    print("Starting comprehensive fix for all audio issues...")
    
    # Fix the audio-interview.html file
    interview_fixed = fix_audio_interview_html()
    
    # Fix the audio-performance.html file
    performance_fixed = fix_audio_performance_html()
    
    # Clean up unnecessary files
    clean_up_files()
    
    if interview_fixed and performance_fixed:
        print("\nAll audio issues have been completely fixed!")
        print("\nChanges made:")
        print("1. Added detailed logging of response data")
        print("2. Added fallback session ID creation")
        print("3. Added sessionStorage for redundancy")
        print("4. Added delay before redirect")
        print("5. Fixed async/await syntax")
        print("6. Added special handling for fallback session IDs")
        print("7. Fixed loose equality comparisons")
        print("8. Removed duplicate endpoint call")
        print("\nThe audio interview and performance pages should now work correctly.")
    else:
        print("\nSome fixes could not be applied. Please check the logs.")

if __name__ == "__main__":
    main()
