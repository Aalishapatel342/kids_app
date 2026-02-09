// Game configuration
const CONFIG = {
    totalCards: 8,
    colors: [
        { name: "Red", color: "#EF4444", audio: "🔴" },
        { name: "Blue", color: "#3B82F6", audio: "🔵" },
        { name: "Green", color: "#10B981", audio: "🟢" },
        { name: "Yellow", color: "#F59E0B", audio: "🟡" },
        { name: "Purple", color: "#8B5CF6", audio: "🟣" },
        { name: "Orange", color: "#F97316", audio: "🟠" },
        { name: "Pink", color: "#EC4899", audio: "🌸" },
        { name: "Teal", color: "#14B8A6", audio: "🧊" }
    ],
    flipBackDelay: 3000,
    rearrangeDelay: 1000,
    spinDuration: 2000
};

class ColorRoulette {
    constructor() {
        this.cards = [];
        this.cardElements = [];
        this.currentCard = null;
        this.speechQueue = [];
        this.isSpeaking = false;
        this.isSpinning = false;
        this.isCircleFormed = false;
        this.init();
    }

    init() {
        this.createCards();
        this.startCircleSpin();
    }

    createCards() {
        const grid = document.getElementById('cardGrid');
        grid.innerHTML = '';
        
        for (let i = 0; i < CONFIG.totalCards; i++) {
            const card = document.createElement('div');
            card.className = 'card';
            card.dataset.index = i;
            
            const inner = document.createElement('div');
            inner.className = 'card-inner';
            
            const back = document.createElement('div');
            back.className = 'card-back';
            back.textContent = '?';
            
            const face = document.createElement('div');
            face.className = 'card-face';
            face.innerHTML = `<div class="color-name"></div>`;
            
            inner.appendChild(back);
            inner.appendChild(face);
            card.appendChild(inner);
            
            card.addEventListener('click', () => this.handleCardClick(i));
            
            grid.appendChild(card);
            this.cards.push({
                element: card,
                index: i,
                x: 0,
                y: 0,
                isFlipped: false,
                color: null
            });
            this.cardElements.push(card);
        }
    }

    startCircleSpin() {
        // Start all cards from center
        const centerX = 250;
        const centerY = 250;
        
        this.cards.forEach((card, index) => {
            card.element.style.left = `${centerX}px`;
            card.element.style.top = `${centerY}px`;
            card.element.style.transition = 'all 0s';
        });
        
        // Start the spinning animation
        setTimeout(() => {
            this.spinCardsInCircle();
        }, 500);
    }

    spinCardsInCircle() {
        this.isSpinning = true;
        const centerX = 250;
        const centerY = 250;
        const radius = 200;
        
        // Position cards in a circle
        this.cards.forEach((card, index) => {
            const angle = (index * 2 * Math.PI) / CONFIG.totalCards;
            const x = centerX + radius * Math.cos(angle) - 50;
            const y = centerY + radius * Math.sin(angle) - 50;
            
            card.x = x;
            card.y = y;
            card.element.style.left = `${x}px`;
            card.element.style.top = `${y}px`;
            card.element.style.transition = 'all 1s cubic-bezier(0.34, 1.56, 0.64, 1)';
        });
        
        // Start rotating animation
        setTimeout(() => {
            this.animateRotation();
        }, 1000);
    }

    animateRotation() {
        const totalSpins = 2; // Number of full rotations
        const steps = 60; // Animation steps per rotation
        const stepDuration = (CONFIG.spinDuration / totalSpins) / steps;
        let currentStep = 0;
        const totalSteps = totalSpins * steps;
        const radius = 200;
        const centerX = 250;
        const centerY = 250;
        
        const rotateStep = () => {
            if (currentStep >= totalSteps) {
                this.isSpinning = false;
                this.isCircleFormed = true;
                this.randomizeCardPositions();
                return;
            }
            
            this.cards.forEach((card, index) => {
                const baseAngle = (index * 2 * Math.PI) / CONFIG.totalCards;
                const rotationAngle = (currentStep * 2 * Math.PI) / steps;
                const totalAngle = baseAngle + rotationAngle;
                
                const x = centerX + radius * Math.cos(totalAngle) - 50;
                const y = centerY + radius * Math.sin(totalAngle) - 50;
                
                card.x = x;
                card.y = y;
                card.element.style.left = `${x}px`;
                card.element.style.top = `${y}px`;
                card.element.style.transition = `all ${stepDuration}ms linear`;
            });
            
            currentStep++;
            setTimeout(rotateStep, stepDuration);
        };
        
        rotateStep();
    }

    randomizeCardPositions() {
        // First make all cards go to random positions
        this.cards.forEach(card => {
            const x = Math.random() * 400 + 100;
            const y = Math.random() * 400 + 100;
            
            card.x = x;
            card.y = y;
            card.element.style.left = `${x}px`;
            card.element.style.top = `${y}px`;
            card.element.style.transition = 'all 1s cubic-bezier(0.34, 1.56, 0.64, 1)';
        });
        
        // After random positions, form a circle again
        setTimeout(() => {
            this.formCircle();
        }, 1500);
    }

    arrangeInSquare() {
        const cols = Math.ceil(Math.sqrt(CONFIG.totalCards));
        const rows = Math.ceil(CONFIG.totalCards / cols);
        const cardSize = 100;
        const spacing = 20;
        const totalWidth = cols * (cardSize + spacing) - spacing;
        const totalHeight = rows * (cardSize + spacing) - spacing;
        const startX = (600 - totalWidth) / 2;
        const startY = (600 - totalHeight) / 2;

        this.cards.forEach((card, index) => {
            const row = Math.floor(index / cols);
            const col = index % cols;
            const x = startX + col * (cardSize + spacing);
            const y = startY + row * (cardSize + spacing);

            card.x = x;
            card.y = y;
            card.element.style.left = `${x}px`;
            card.element.style.top = `${y}px`;
            card.element.style.transition = 'all 1s cubic-bezier(0.34, 1.56, 0.64, 1)';
        });
    }

    handleCardClick(index) {
        // Don't allow clicks during spinning or if another card is active
        if (this.isSpinning || this.currentCard !== null || !this.isCircleFormed) {
            return;
        }
        
        this.currentCard = index;
        const card = this.cards[index];
        const cardElement = card.element;
        
        // Pick a random color
        const colorData = CONFIG.colors[Math.floor(Math.random() * CONFIG.colors.length)];
        card.color = colorData;
        
        // Flip the card
        cardElement.classList.add('flip');
        card.isFlipped = true;
        
        // Set the color on the face
        const face = cardElement.querySelector('.card-face');
        face.style.backgroundColor = colorData.color;
        face.querySelector('.color-name').textContent = colorData.name;
        
        // Speak the color name
        this.speakColor(colorData.name, colorData.audio);
        
        // Set timeout to flip back
        setTimeout(() => {
            cardElement.classList.remove('flip');
            card.isFlipped = false;
            
            // After flip back, start the spin animation again
            setTimeout(() => {
                this.startNewRound();
            }, CONFIG.rearrangeDelay);
            
        }, CONFIG.flipBackDelay);
    }

    startNewRound() {
        // Reset current card
        this.currentCard = null;
        
        // Start the spin cycle again
        this.isCircleFormed = false;
        this.startCircleSpin();
    }

    speakColor(colorName, emoji) {
        this.speechQueue.push({ colorName, emoji });
        this.processSpeechQueue();
    }

    processSpeechQueue() {
        if (this.isSpeaking || this.speechQueue.length === 0) return;
        
        this.isSpeaking = true;
        const { colorName, emoji } = this.speechQueue.shift();
        
        // Create visual feedback
        const feedback = document.createElement('div');
        feedback.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) scale(0.5);
            font-size: 5rem;
            opacity: 0;
            transition: opacity 0.3s, transform 0.3s;
            z-index: 1000;
            pointer-events: none;
            text-shadow: 0 5px 15px rgba(0,0,0,0.3);
        `;
        feedback.textContent = emoji;
        document.body.appendChild(feedback);
        
        // Animate in
        setTimeout(() => {
            feedback.style.opacity = '1';
            feedback.style.transform = 'translate(-50%, -50%) scale(1.5)';
        }, 10);
        
        // Use Web Speech API
        if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(colorName);
            utterance.rate = 0.9;
            utterance.pitch = 1.1;
            utterance.volume = 1;
            
            // Try to find a child-friendly voice
            const voices = speechSynthesis.getVoices();
            const childVoice = voices.find(voice => 
                voice.name.includes('Google US English') || 
                voice.name.includes('Samantha') ||
                voice.name.includes('Microsoft Zira')
            );
            
            if (childVoice) {
                utterance.voice = childVoice;
            }
            
            utterance.onend = () => {
                // Animate out
                setTimeout(() => {
                    feedback.style.opacity = '0';
                    feedback.style.transform = 'translate(-50%, -50%) scale(0.5)';
                    
                    setTimeout(() => {
                        feedback.remove();
                        this.isSpeaking = false;
                        this.processSpeechQueue();
                    }, 300);
                }, 500);
            };
            
            speechSynthesis.speak(utterance);
        } else {
            // Fallback animation if speech synthesis not available
            setTimeout(() => {
                feedback.style.opacity = '0';
                feedback.style.transform = 'translate(-50%, -50%) scale(0.5)';
                
                setTimeout(() => {
                    feedback.remove();
                    this.isSpeaking = false;
                    this.processSpeechQueue();
                }, 300);
            }, 1500);
        }
    }
}

// Initialize the game when page loads
window.addEventListener('DOMContentLoaded', () => {
    new ColorRoulette();
    
    // Preload voices for speech synthesis
    if ('speechSynthesis' in window) {
        speechSynthesis.getVoices();
        setTimeout(() => speechSynthesis.getVoices(), 100);
    }
});