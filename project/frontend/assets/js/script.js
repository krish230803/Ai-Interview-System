// API Configuration
const API_BASE_URL = 'http://localhost:5000';

// Common fetch options for all API calls
const fetchOptions = {
    credentials: 'include',
    mode: 'cors',
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
};

// Global state object
const state = {
    submitAnswerBtn: null,
    userResponseInput: null,
    statusContainer: null,
    questionText: null,
    audioRecordBtn: null,
    loadingSpinner: null,
    progressBar: null,
    interviewSection: null,
    dashboardSection: null,
    sessionId: null,
    currentQuestion: '',
    questionNumber: 0,
    isSubmitting: false,
    isRecording: false,
    recognition: null,
    existingText: '',
    startTime: null,
    totalQuestions: 10,
    sentimentChart: null,
    scoresChart: null,
    isInitialized: false
};

// Helper functions
function updateProgress(questionNum) {
    if (!state.progressBar) return;
    const progress = (questionNum / state.totalQuestions) * 100;
    state.progressBar.style.width = `${progress}%`;
    state.progressBar.setAttribute('aria-valuenow', progress);
    state.progressBar.textContent = `${questionNum}/${state.totalQuestions} Questions`;
}

function showLoading() {
    if (!state.loadingSpinner || !state.questionText) return;
    state.loadingSpinner.style.display = 'block';
    state.questionText.style.opacity = '0.5';
}

function hideLoading() {
    if (!state.loadingSpinner || !state.questionText) return;
    state.loadingSpinner.style.display = 'none';
    state.questionText.style.opacity = '1';
}

function updateStatus(message, type = 'info') {
    if (!state.statusContainer) return;
    state.statusContainer.textContent = message;
    state.statusContainer.className = `mt-3 alert alert-${type}`;
    state.statusContainer.style.display = 'block';
}

function hideStatus() {
    if (!state.statusContainer) return;
    state.statusContainer.style.display = 'none';
}

function stopRecording() {
    if (state.isRecording) {
        try {
            state.recognition?.stop();
            console.log("Speech recognition stopped");
        } catch (e) {
            console.error('Error stopping recognition:', e);
        }
        state.isRecording = false;
        if (state.audioRecordBtn) {
            state.audioRecordBtn.innerHTML = '<i class="bi bi-mic"></i> Record Answer';
            state.audioRecordBtn.classList.remove('btn-danger');
            state.audioRecordBtn.classList.add('btn-secondary');
        }
        updateStatus('Recording stopped', 'info');
    }
}

// Initialize speech recognition
function initializeSpeechRecognition() {
    if (window.SpeechRecognition || window.webkitSpeechRecognition) {
        state.recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        state.recognition.lang = 'en-US';
        state.recognition.continuous = true;
        state.recognition.interimResults = true;
        state.recognition.maxAlternatives = 1;

        state.recognition.onresult = (event) => {
            if (state.isSubmitting) return;
            
            let finalTranscript = '';
            let interimTranscript = '';
            
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript + ' ';
                } else {
                    interimTranscript += transcript;
                }
            }
            
            if (state.userResponseInput) {
                if (finalTranscript) {
                    state.existingText = finalTranscript;
                    state.userResponseInput.value = finalTranscript;
                }
                if (interimTranscript) {
                    state.userResponseInput.value = state.existingText + interimTranscript;
                }
            }
            
            if (finalTranscript || interimTranscript) {
                updateStatus('Speech captured! Click Submit Answer when ready.', 'success');
            }
        };

        state.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            if (event.error !== 'no-speech') {
                updateStatus('Error with speech recognition: ' + event.error, 'danger');
            }
            stopRecording();
        };

        state.recognition.onend = () => {
            if (state.isRecording && !state.isSubmitting) {
                try {
                    setTimeout(() => {
                        if (state.isRecording && !state.isSubmitting && state.recognition) {
                            state.recognition.start();
                            console.log("Restarted speech recognition");
                        }
                    }, 100);
                } catch (error) {
                    console.error('Error restarting recognition:', error);
                    stopRecording();
                }
            }
        };
    }
}

// Clean up function for speech recognition
function cleanupSpeechRecognition() {
    if (state.recognition) {
        try {
            state.recognition.stop();
        } catch (e) {
            console.warn('Error stopping recognition during cleanup:', e);
        }
        state.recognition = null;
    }
}

// Initialize DOM elements
function initializeElements() {
    state.submitAnswerBtn = document.getElementById('submit-answer-btn');
    state.userResponseInput = document.getElementById('user-response');
    state.statusContainer = document.getElementById('status-container');
    state.questionText = document.getElementById('question-text');
    state.audioRecordBtn = document.getElementById('audio-record-btn');
    state.loadingSpinner = document.getElementById('loading-spinner');
    state.progressBar = document.getElementById('progress-bar');
    state.interviewSection = document.getElementById('interview-section');
    state.dashboardSection = document.getElementById('dashboard-section');
    
    state.startTime = new Date();
}

// Add event listeners
function setupEventListeners() {
    // Add logout functionality
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }

    // Display user name
    const userEmailElement = document.getElementById('user-email');
    if (userEmailElement) {
        const user = JSON.parse(localStorage.getItem('user'));
        if (user?.name) {
            userEmailElement.textContent = user.name;
        }
    }

    // Add submit answer event listener
    if (state.submitAnswerBtn) {
        state.submitAnswerBtn.addEventListener('click', handleSubmitAnswer);
    }

    // Add audio recording event listener
    if (state.audioRecordBtn && state.recognition) {
        state.audioRecordBtn.addEventListener('click', handleAudioRecording);
    }
}

// Initialize everything when the page loads
document.addEventListener('DOMContentLoaded', () => {
    try {
        console.log('Page loaded, initializing...');
        
        if (!state.isInitialized) {
            initializeElements();
            initializeSpeechRecognition();
            setupEventListeners();
            state.isInitialized = true;
        }
        
        if (state.questionText) {
            console.log('Interview page detected, getting first question...');
            getFirstQuestion().catch(error => {
                console.error('Error getting first question:', error);
                updateStatus('Failed to start interview. Please refresh the page.', 'danger');
            });
        }
    } catch (error) {
        console.error('Error during initialization:', error);
        updateStatus('Error initializing the interview. Please refresh the page.', 'danger');
    }
});

// Cleanup when leaving the page
window.addEventListener('beforeunload', () => {
    cleanupSpeechRecognition();
});

function createCharts(stats) {
    console.log('Creating charts with stats:', stats);

    // Ensure we have the required data
    if (!stats || !stats.sentiment_distribution || !stats.detailed_responses) {
        console.error('Missing required data for charts:', stats);
        return;
    }

    try {
        // Destroy existing charts if they exist
        if (state.sentimentChart) {
            state.sentimentChart.destroy();
            state.sentimentChart = null;
        }
        if (state.scoresChart) {
            state.scoresChart.destroy();
            state.scoresChart = null;
        }

        // Sentiment Distribution Chart
        const sentimentCtx = document.getElementById('sentiment-chart');
        if (!sentimentCtx) {
            console.error('Sentiment chart canvas not found');
            return;
        }

        state.sentimentChart = new Chart(sentimentCtx.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: Object.keys(stats.sentiment_distribution),
                datasets: [{
                    data: Object.values(stats.sentiment_distribution),
                    backgroundColor: ['#4caf50', '#f44336', '#2196f3'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            font: {
                                family: 'Inter'
                            }
                        }
                    }
                },
                cutout: '70%'
            }
        });

        // Scores Chart
        const scoresCtx = document.getElementById('scores-chart');
        if (!scoresCtx) {
            console.error('Scores chart canvas not found');
            return;
        }

        // Ensure scores are valid numbers
        const scores = stats.detailed_responses.map(r => {
            const score = parseFloat(r.score);
            return isNaN(score) ? 0 : score;
        });

        state.scoresChart = new Chart(scoresCtx.getContext('2d'), {
            type: 'line',
            data: {
                labels: Array.from({length: scores.length}, (_, i) => `Q${i+1}`),
                datasets: [{
                    label: 'Response Scores',
                    data: scores,
                    borderColor: '#2196f3',
                    backgroundColor: 'rgba(33, 150, 243, 0.1)',
                    tension: 0.1,
                    fill: true,
                    pointBackgroundColor: '#ffffff',
                    pointBorderColor: '#2196f3',
                    pointBorderWidth: 2,
                    pointRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 5,
                        ticks: {
                            stepSize: 1,
                            font: {
                                family: 'Inter'
                            }
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    },
                    x: {
                        ticks: {
                            font: {
                                family: 'Inter'
                            }
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error creating charts:', error);
        updateStatus('Error creating performance charts', 'warning');
    }
}

function updateDashboard(stats) {
    console.log('Updating dashboard with stats:', stats);

    try {
        if (!stats) {
            throw new Error('No stats provided for dashboard update');
        }

        // Update summary stats
        const overallScore = document.getElementById('overall-score');
        const avgLength = document.getElementById('avg-length');
        const totalQuestions = document.getElementById('total-questions');
        const completionTime = document.getElementById('completion-time');

        if (overallScore) overallScore.textContent = stats.average_score.toFixed(2);
        if (avgLength) avgLength.textContent = Math.round(stats.average_response_length);
        if (totalQuestions) totalQuestions.textContent = stats.total_questions;
        
        // Calculate completion time
        if (completionTime && state.startTime) {
            const duration = Math.round((new Date() - state.startTime) / 60000); // minutes
            completionTime.textContent = duration;
        }

        // Update detailed responses table
        const tbody = document.getElementById('responses-table-body');
        if (tbody && stats.detailed_responses) {
            tbody.innerHTML = '';
            stats.detailed_responses.forEach(response => {
                const row = document.createElement('tr');
                const scoreValue = typeof response.score === 'number' ? response.score.toFixed(2) : '0.00';
                row.innerHTML = `
                    <td>${response.question || 'N/A'}</td>
                    <td>${response.response || 'N/A'}</td>
                    <td><span class="badge bg-${getSentimentColor(response.sentiment)}">${response.sentiment || 'Neutral'}</span></td>
                    <td>${scoreValue}</td>
                `;
                tbody.appendChild(row);
            });
        }

        // Create or update charts
        createCharts(stats);
    } catch (error) {
        console.error('Error updating dashboard:', error);
        updateStatus('Error updating dashboard display', 'danger');
    }
}

// Helper function to get sentiment color
function getSentimentColor(sentiment) {
    if (!sentiment) return 'secondary';
    switch (sentiment.toLowerCase()) {
        case 'positive': return 'success';
        case 'negative': return 'danger';
        default: return 'warning';
    }
}

function showDashboard(stats) {
    state.interviewSection.style.display = 'none';
    state.dashboardSection.style.display = 'block';
    updateDashboard(stats);
}

function updateSentimentDisplay(sentiment) {
    try {
        const sentimentValue = document.getElementById('sentiment-value');
        const confidenceValue = document.getElementById('confidence-value');
        const subjectivityValue = document.getElementById('subjectivity-value');
        const sentimentContainer = document.querySelector('.sentiment-container');

        // If any required element is missing, log a warning and return
        if (!sentimentContainer || !sentimentValue || !confidenceValue || !subjectivityValue) {
            console.warn('Some sentiment display elements not found, skipping sentiment update');
            return;
        }

        // Only update if we have valid sentiment data
        if (sentiment && typeof sentiment === 'object') {
            sentimentValue.textContent = sentiment.sentiment || 'N/A';
            confidenceValue.textContent = sentiment.confidence ? `${sentiment.confidence.toFixed(1)}%` : 'N/A';
            subjectivityValue.textContent = sentiment.subjectivity ? `${sentiment.subjectivity.toFixed(1)}%` : 'N/A';
            sentimentContainer.style.display = 'block';
        }
    } catch (error) {
        console.warn('Error updating sentiment display:', error);
    }
}

// Update the getNextQuestion function to handle sentiment display safely
async function getNextQuestion(responseText, inputType = 'text') {
    try {
        showLoading();
        updateStatus('Processing your answer...', 'info');
        
        stopRecording();
        
        if (!state.sessionId) {
            throw new Error('No active session. Please refresh the page.');
        }
        
        const data = {
            session_id: state.sessionId,
            response: responseText,
            current_question: state.currentQuestion,
            question_number: state.questionNumber,
            inputType: inputType  // Ensure inputType is included
        };

        console.log('Sending answer:', data);
        let response;
        try {
            response = await fetch(`${API_BASE_URL}/interview`, {
                method: 'POST',
                ...fetchOptions,
                body: JSON.stringify(data)
            });
        } catch (fetchError) {
            console.error('Network error:', fetchError);
            throw new Error('Network error. Please check your connection.');
        }

        if (response.status === 401) {
            // Unauthorized - redirect to login
            window.location.href = 'login.html';
            return;
        }

        let result;
        try {
            result = await response.json();
            console.log('Received response:', result);
        } catch (parseError) {
            console.error('Parse error:', parseError);
            throw new Error('Invalid response from server.');
        }

        if (!response.ok) {
            throw new Error(result.error || `Server error: ${response.status}`);
        }

        if (result.completed) {
            try {
                showDashboard(result.stats);
            } catch (dashboardError) {
                console.error('Dashboard error:', dashboardError);
                throw new Error('Error displaying results.');
            }
            return;
        }

        if (!result.next_question) {
            throw new Error('No next question received');
        }

        state.currentQuestion = result.next_question;
        state.questionNumber = result.question_number || (state.questionNumber + 1);
        
        try {
            state.questionText.textContent = state.currentQuestion;
            updateProgress(state.questionNumber);
        } catch (uiError) {
            console.error('UI update error:', uiError);
            throw new Error('Error updating display.');
        }

        // Handle sentiment data safely
        if (result.sentiment) {
            try {
                let message = 'Response analyzed';
                if (typeof result.sentiment === 'string') {
                    message += ` as: ${result.sentiment}`;
                } else if (typeof result.sentiment === 'object' && result.sentiment.sentiment) {
                    message += ` as: ${result.sentiment.sentiment}`;
                }
                if (result.category) {
                    message += ` (Category: ${result.category})`;
                }
                updateStatus(message, 'success');
            } catch (sentimentError) {
                console.warn('Sentiment display error:', sentimentError);
                // Don't throw error for sentiment display issues
            }
        } else {
            hideStatus();
        }

        try {
            state.userResponseInput.value = '';
            state.userResponseInput.focus();
        } catch (inputError) {
            console.warn('Input reset error:', inputError);
            // Don't throw error for input reset issues
        }

    } catch (error) {
        console.error('Error submitting answer:', error);
        updateStatus(error.message || 'Failed to submit answer. Please try again.', 'danger');
        throw error; // Re-throw to be handled by submitAnswer
    } finally {
        hideLoading();
        state.isSubmitting = false;
    }
}

// Event handler for submit answer button
async function handleSubmitAnswer() {
    if (state.isSubmitting) return;
    
    const responseText = state.userResponseInput.value.trim();
    if (!responseText) {
        updateStatus('Please enter your answer before submitting.', 'warning');
        return;
    }

    state.isSubmitting = true;
    state.submitAnswerBtn.disabled = true;
    
    try {
        // Try up to 3 times
        let error;
        for (let attempt = 0; attempt < 3; attempt++) {
            try {
                console.log(`Submitting answer, attempt ${attempt + 1}/3`);
                const result = await getNextQuestion(responseText);
                
                if (result && result.completed) {
                    showDashboard(result.stats);
                    return; // Exit early since we're redirecting
                } else {
                    state.userResponseInput.value = '';
                    state.userResponseInput.focus();
                }
                
                // If we get here, the submission was successful
                error = null;
                break;
            } catch (e) {
                error = e;
                console.error(`Attempt ${attempt + 1} failed:`, e);
                
                // If this wasn't the last attempt, wait before retrying
                if (attempt < 2) {
                    updateStatus(`Retrying submission (${attempt + 1}/3)...`, 'warning');
                    await new Promise(resolve => setTimeout(resolve, 1000));
                }
            }
        }
        
        // If we still have an error after all attempts
        if (error) {
            throw error;
        }
    } catch (error) {
        console.error('All attempts to submit answer failed:', error);
        updateStatus('Failed to submit answer. Please try again or refresh the page.', 'danger');
    } finally {
        state.isSubmitting = false;
        state.submitAnswerBtn.disabled = false;
    }
}

// Event handler for audio recording button
function handleAudioRecording() {
    if (state.isRecording) {
        stopRecording();
    } else {
        try {
            // Make sure any previous recognition session is stopped
            try {
                state.recognition.stop();
            } catch (e) {
                // Ignore errors when stopping non-started recognition
            }
            
            // Store the existing text when starting a new recording
            state.existingText = state.userResponseInput.value || '';
            
            // Configure recognition for continuous speech
            state.recognition.continuous = true;
            state.recognition.interimResults = true;
            
            // Start recognition after a small delay to ensure clean start
            setTimeout(() => {
                state.recognition.start();
                state.isRecording = true;
                state.audioRecordBtn.innerHTML = '<i class="bi bi-mic-fill me-2"></i> Stop Recording';
                state.audioRecordBtn.classList.remove('btn-secondary');
                state.audioRecordBtn.classList.add('btn-danger');
                
                updateStatus('Recording started. Speak clearly into your microphone.', 'info');
            }, 50);
        } catch (e) {
            console.error('Error starting recognition:', e);
            updateStatus('Failed to start recording. Please try again.', 'danger');
        }
    }
}

async function getFirstQuestion() {
    try {
        showLoading();
        state.questionText.textContent = 'Preparing your first question...';
        
        console.log('Fetching first question...');
        const response = await fetch(`${API_BASE_URL}/interview/start`, {
            method: 'GET',
            ...fetchOptions
        });

        if (response.status === 401) {
            // Unauthorized - redirect to login
            window.location.href = 'login.html';
            return;
        }

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            console.error('Server error:', errorData);
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        console.log('Received first question:', result);

        if (result && result.next_question) {
            state.sessionId = result.session_id;
            state.currentQuestion = result.next_question;
            state.questionNumber = result.question_number || 1;
            state.questionText.textContent = state.currentQuestion;
            updateProgress(state.questionNumber);
            hideStatus();
        } else {
            throw new Error('No question received from server');
        }
    } catch (error) {
        console.error('Error fetching first question:', error);
        state.questionText.textContent = 'Error loading question';
        updateStatus('Error starting the interview. Please refresh the page.', 'danger');
    } finally {
        hideLoading();
    }
}

// Logout handler function
async function handleLogout() {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/logout`, {
            ...fetchOptions,
            method: 'GET'
        });

        if (!response.ok) {
            throw new Error('Logout failed');
        }

        localStorage.removeItem('user');
        window.location.href = 'login.html';
    } catch (error) {
        console.error('Logout error:', error);
        alert('Failed to logout. Please try again.');
    }
}

// Handle Start New Interview button clicks
function handleStartNewInterview(event) {
    event.preventDefault();
    window.location.href = 'index.html#interview-modes';
    setTimeout(() => {
        const interviewModes = document.querySelector('#interview-modes');
        if (interviewModes) {
            interviewModes.scrollIntoView({ behavior: 'smooth' });
        }
    }, 100);
}