// Color Carnival Game - Simplified Version
document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const colorGrid = document.getElementById('colorGrid');
    const colorPopup = document.getElementById('colorPopup');
    const popupColor = document.getElementById('popupColor');
    const popupName = document.getElementById('popupName');
    const closePopup = document.getElementById('closePopup');
    
    // Game State
    let colors = [];
    let speechSynthesis = window.speechSynthesis;
    
    // Initialize
    loadColors();
    setupEventListeners();
    
    // Pre-load voices for smoother speech
    if (speechSynthesis) {
        speechSynthesis.getVoices();
        speechSynthesis.addEventListener('voiceschanged', function initialLoad() {
            speechSynthesis.removeEventListener('voiceschanged', initialLoad);
        });
    }
    
    // Load colors from API
    async function loadColors() {
        try {
            const response = await fetch('/api/colors');
            if (!response.ok) throw new Error('Failed to load colors');
            colors = await response.json();
            renderColors();
        } catch (error) {
            console.error('Error loading colors:', error);
            // Fallback colors
            colors = [
                {"name": "Red", "code": "#FF0000"},
                {"name": "Blue", "code": "#0000FF"},
                {"name": "Green", "code": "#00FF00"},
                {"name": "Yellow", "code": "#FFFF00"},
                {"name": "Purple", "code": "#800080"},
                {"name": "Orange", "code": "#FFA500"},
                {"name": "Pink", "code": "#FFC0CB"},
                {"name": "Brown", "code": "#A52A2A"},
                {"name": "Cyan", "code": "#00FFFF"},
                {"name": "Magenta", "code": "#FF00FF"}
            ];
            renderColors();
        }
    }
    
    // Render colors to grid
    function renderColors() {
        if (!colorGrid) return;
        
        colorGrid.innerHTML = '';
        colors.forEach(color => {
            const card = document.createElement('div');
            card.className = 'color-card';
            card.style.backgroundColor = color.code;
            
            // Set text color based on brightness
            const brightness = getBrightness(color.code);
            card.style.color = brightness > 128 ? '#000000' : '#FFFFFF';
            
            // Only show color name, no hex code
            card.textContent = color.name;
            
            card.addEventListener('click', () => showColorPopup(color));
            colorGrid.appendChild(card);
        });
    }
    
    // Calculate brightness for text color
    function getBrightness(hex) {
        const r = parseInt(hex.substr(1, 2), 16);
        const g = parseInt(hex.substr(3, 2), 16);
        const b = parseInt(hex.substr(5, 2), 16);
        return (r * 0.299 + g * 0.587 + b * 0.114);
    }
    
    // Show color popup
    function showColorPopup(color) {
        // Update popup
        popupColor.style.backgroundColor = color.code;
        popupName.textContent = color.name;
        
        // Show popup
        colorPopup.style.display = 'flex';
        
        // Always speak color name (voice is always on)
        speakColor(color.name);
    }
    
    // Speak color name
    function speakColor(text) {
        if (!speechSynthesis) return;
        
        // Ensure text is a valid string
        if (!text || typeof text !== 'string') {
            console.error('Invalid text for speech synthesis:', text);
            return;
        }
        
        // Convert to string and trim
        const textToSpeak = String(text).trim();
        
        if (!textToSpeak) {
            console.error('Empty text for speech synthesis');
            return;
        }
        
        // Cancel any ongoing speech
        speechSynthesis.cancel();
        
        const utterance = new SpeechSynthesisUtterance(textToSpeak);
        
        // Set language explicitly for proper pronunciation
        utterance.lang = 'en-US';
        utterance.rate = 0.9;
        utterance.pitch = 1;
        utterance.volume = 1;
        
        // Function to get voice and speak
        const trySpeak = () => {
            let voices = [];
            
            try {
                voices = speechSynthesis.getVoices() || [];
            } catch (e) {
                console.warn('Error getting voices:', e);
            }
            
            // Try to find an English voice
            let selectedVoice = null;
            
            // First, try to find US English voice
            selectedVoice = voices.find(voice => voice.lang === 'en-US');
            
            // If not found, try any English voice
            if (!selectedVoice) {
                selectedVoice = voices.find(voice => voice.lang.startsWith('en'));
            }
            
            // If still not found, try any voice (fallback)
            if (!selectedVoice && voices.length > 0) {
                selectedVoice = voices[0];
                console.warn('No English voice found, using fallback:', selectedVoice.name);
            }
            
            if (selectedVoice) {
                utterance.voice = selectedVoice;
            }
            
            // Handle errors with user feedback
            utterance.onerror = function(event) {
                console.error('Speech synthesis error:', event.error);
            };
            
            utterance.onstart = function() {
                console.log('Speaking color:', textToSpeak);
            };
            
            utterance.onend = function() {
                console.log('Speech completed');
            };
            
            // Speak the text
            try {
                speechSynthesis.speak(utterance);
            } catch (e) {
                console.error('Error speaking:', e);
            }
        };
        
        // Check if voices are already loaded
        let voices = [];
        try {
            voices = speechSynthesis.getVoices() || [];
        } catch (e) {
            console.warn('Error getting voices:', e);
        }
        
        if (voices.length > 0) {
            trySpeak();
        } else {
            // Wait for voices to be loaded
            const onVoicesChanged = () => {
                try {
                    speechSynthesis.removeEventListener('voiceschanged', onVoicesChanged);
                } catch (e) {
                    // Ignore if already removed
                }
                trySpeak();
            };
            
            speechSynthesis.addEventListener('voiceschanged', onVoicesChanged);
            
            // Safety timeout - try to speak anyway after 2 seconds
            setTimeout(() => {
                try {
                    // Check again if voices are now available
                    voices = speechSynthesis.getVoices() || [];
                    if (voices.length > 0) {
                        trySpeak();
                    } else {
                        // No voices available, try to speak anyway (some browsers will use default)
                        console.warn('No voices available, attempting to speak anyway');
                        try {
                            speechSynthesis.speak(utterance);
                        } catch (e) {
                            console.error('Could not speak:', e);
                        }
                    }
                } catch (e) {
                    console.error('Error in timeout:', e);
                }
            }, 2000);
        }
    }
    
    // Event Listeners
    function setupEventListeners() {
        // Close popup
        if (closePopup) {
            closePopup.addEventListener('click', () => {
                colorPopup.style.display = 'none';
            });
        }
        
        // Close popup when clicking outside
        if (colorPopup) {
            colorPopup.addEventListener('click', (e) => {
                if (e.target === colorPopup) {
                    colorPopup.style.display = 'none';
                }
            });
        }
        
        // Close with Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && colorPopup) {
                colorPopup.style.display = 'none';
            }
        });
    }
});