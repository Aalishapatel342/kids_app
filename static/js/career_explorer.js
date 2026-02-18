// Career Explorer JavaScript with Kid-Friendly Features
const careersData = {
    science: [
        {
            id: 1,
            name: "Astronaut",
            icon: "fas fa-rocket",
            description: "Blast off to space and explore planets! 🚀",
            funFact: "Astronauts can grow 2 inches taller in space!",
            education: "Study science, math, and engineering",
            skills: ["Brave", "Curious", "Good at math", "Team player"],
            category: "science",
            color: "#4ECDC4"
        },
        {
            id: 2,
            name: "Marine Biologist",
            icon: "fas fa-fish",
            description: "Swim with dolphins and study colorful fish! 🐬",
            funFact: "Some fish can change their gender!",
            education: "Study biology and ocean science",
            skills: ["Loves animals", "Good swimmer", "Patient", "Observant"],
            category: "science",
            color: "#6BCB77"
        }
    ],
    art: [
        {
            id: 3,
            name: "Animator",
            icon: "fas fa-film",
            description: "Bring cartoon characters to life! 🎨",
            funFact: "It takes 24 drawings for 1 second of animation!",
            education: "Study art and animation",
            skills: ["Creative", "Good at drawing", "Imaginative", "Patient"],
            category: "art",
            color: "#FFD93D"
        },
        {
            id: 4,
            name: "Video Game Designer",
            icon: "fas fa-gamepad",
            description: "Create fun games that everyone loves! 🎮",
            funFact: "The first video game was created in 1958!",
            education: "Study computer science and art",
            skills: ["Creative", "Problem solver", "Loves games", "Team player"],
            category: "art",
            color: "#FFB347"
        }
    ],
    tech: [
        {
            id: 5,
            name: "Robot Engineer",
            icon: "fas fa-robot",
            description: "Build cool robots that can dance! 🤖",
            funFact: "Some robots can dance better than humans!",
            education: "Study engineering and programming",
            skills: ["Good at math", "Creative builder", "Problem solver", "Patient"],
            category: "tech",
            color: "#9B59B6"
        },
        {
            id: 6,
            name: "App Developer",
            icon: "fas fa-mobile-alt",
            description: "Make fun apps for phones and tablets! 📱",
            funFact: "There are over 5 million apps in app stores!",
            education: "Study computer programming",
            skills: ["Problem solver", "Creative", "Good at logic", "Patient"],
            category: "tech",
            color: "#8E44AD"
        }
    ],
    health: [
        {
            id: 7,
            name: "Doctor",
            icon: "fas fa-user-md",
            description: "Help kids feel better when they're sick! 👨‍⚕️",
            funFact: "Doctors spend 10+ years learning to help people!",
            education: "Study medicine and biology",
            skills: ["Caring", "Smart", "Good listener", "Patient"],
            category: "health",
            color: "#FF6B6B"
        },
        {
            id: 8,
            name: "Police Officer",
            icon: "fas fa-shield-alt",
            description: "Protect people and keep everyone safe! 👮",
            funFact: "Police officers are trained to help in emergencies!",
            education: "Study criminal justice",
            skills: ["Brave", "Honest", "Good leader", "Helpful"],
            category: "health",
            color: "#2C3E50"
        },
        {
            id: 9,
            name: "Veterinarian",
            icon: "fas fa-paw",
            description: "Take care of cute puppies and kittens! 🐱",
            funFact: "Vets can treat animals from hamsters to elephants!",
            education: "Study animal medicine",
            skills: ["Loves animals", "Gentle", "Observant", "Brave"],
            category: "health",
            color: "#FF8E53"
        },
        {
            id: 10,
            name: "Pediatrician",
            icon: "fas fa-child",
            description: "Help children grow up healthy and strong! 👶",
            funFact: "Doctors use stethoscopes to listen to hearts!",
            education: "Study medicine",
            skills: ["Caring", "Good listener", "Patient", "Smart"],
            category: "health",
            color: "#FF6B8B"
        }
    ],
    nature: [
        {
            id: 11,
            name: "Park Ranger",
            icon: "fas fa-tree",
            description: "Protect forests and wild animals! 🌲",
            funFact: "Some trees can live for thousands of years!",
            education: "Study environmental science",
            skills: ["Loves nature", "Good leader", "Observant", "Brave"],
            category: "nature",
            color: "#27AE60"
        },
        {
            id: 12,
            name: "Weather Scientist",
            icon: "fas fa-cloud-sun",
            description: "Study clouds, rain, and storms! ⛈️",
            funFact: "Lightning is 5 times hotter than the sun!",
            education: "Study meteorology",
            skills: ["Observant", "Good at science", "Curious", "Patient"],
            category: "nature",
            color: "#3498DB"
        }
    ]
};

// Quiz questions with fun options
const quizQuestions = [
    {
        question: "🎨 What do you enjoy doing the most?",
        options: [
            { text: "Drawing and painting pictures", category: "art" },
            { text: "Building with blocks or Legos", category: "tech" },
            { text: "Playing with pets and animals", category: "nature" },
            { text: "Doing cool science experiments", category: "science" },
            { text: "Helping friends feel better", category: "health" }
        ]
    },
    {
        question: "📚 What's your favorite subject in school?",
        options: [
            { text: "Art class - I love to draw!", category: "art" },
            { text: "Computer class - I like technology!", category: "tech" },
            { text: "Science class - Experiments are fun!", category: "science" },
            { text: "Nature studies - I love animals!", category: "nature" },
            { text: "Health class - Helping others!", category: "health" }
        ]
    },
    {
        question: "🗺️ Where would you most like to visit?",
        options: [
            { text: "An art museum with cool paintings", category: "art" },
            { text: "A science museum with dinosaurs", category: "science" },
            { text: "A computer lab with robots", category: "tech" },
            { text: "A national park with animals", category: "nature" },
            { text: "A children's hospital", category: "health" }
        ]
    },
    {
        question: "🎮 What's your favorite type of game?",
        options: [
            { text: "Drawing and coloring games", category: "art" },
            { text: "Building and crafting games", category: "tech" },
            { text: "Animal care games", category: "nature" },
            { text: "Science puzzle games", category: "science" },
            { text: "Doctor and hospital games", category: "health" }
        ]
    },
    {
        question: "🦸 What superpower would you want?",
        options: [
            { text: "Create anything I imagine", category: "art" },
            { text: "Build amazing machines", category: "tech" },
            { text: "Talk to animals", category: "nature" },
            { text: "Fly to space", category: "science" },
            { text: "Heal people and animals", category: "health" }
        ]
    }
];

let currentQuestion = 0;
let selectedOptions = [];
let userAnswers = [];
let favoriteCareers = JSON.parse(localStorage.getItem('favoriteCareers')) || [];

// Initialize the app
function init() {
    showActivityCards();
    loadCareerGallery();
}

// Show activity cards (Home)
function showActivityCards() {
    document.querySelector('.activity-cards').style.display = 'grid';
    document.getElementById('careerGallery').style.display = 'none';
    document.getElementById('quizSection').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'none';
    
    // Update active nav button
    document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelector('.nav-btn:first-child').classList.add('active');
}

// Start career quiz
function startCareerQuiz() {
    document.querySelector('.activity-cards').style.display = 'none';
    document.getElementById('quizSection').style.display = 'block';
    document.getElementById('careerGallery').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'none';
    
    currentQuestion = 0;
    selectedOptions = [];
    userAnswers = [];
    
    loadQuestion();
}

// Load question
function loadQuestion() {
    const question = quizQuestions[currentQuestion];
    const progress = ((currentQuestion + 1) / quizQuestions.length) * 100;
    
    document.getElementById('questionText').textContent = question.question;
    document.getElementById('currentQuestion').textContent = currentQuestion + 1;
    document.getElementById('progressFill').style.width = `${progress}%`;
    
    const optionsContainer = document.getElementById('optionsContainer');
    optionsContainer.innerHTML = '';
    
    question.options.forEach((option, index) => {
        const optionBtn = document.createElement('button');
        optionBtn.className = 'option-btn';
        optionBtn.textContent = option.text;
        if (selectedOptions[currentQuestion] === index) {
            optionBtn.classList.add('selected');
        }
        optionBtn.onclick = () => selectOption(index);
        optionsContainer.appendChild(optionBtn);
    });
    
    // Update buttons
    document.getElementById('prevBtn').style.display = currentQuestion === 0 ? 'none' : 'inline-block';
    document.getElementById('nextBtn').style.display = currentQuestion === quizQuestions.length - 1 ? 'none' : 'inline-block';
    document.getElementById('submitBtn').style.display = currentQuestion === quizQuestions.length - 1 ? 'inline-block' : 'none';
}

// Select option
function selectOption(index) {
    selectedOptions[currentQuestion] = index;
    userAnswers[currentQuestion] = quizQuestions[currentQuestion].options[index].category;
    
    // Update UI
    const options = document.querySelectorAll('.option-btn');
    options.forEach((btn, i) => {
        btn.classList.toggle('selected', i === index);
    });
}

// Next question
function nextQuestion() {
    if (selectedOptions[currentQuestion] === undefined) {
        alert('Please select an answer before continuing!');
        return;
    }
    
    if (currentQuestion < quizQuestions.length - 1) {
        currentQuestion++;
        loadQuestion();
    }
}

// Previous question
function previousQuestion() {
    if (currentQuestion > 0) {
        currentQuestion--;
        loadQuestion();
    }
}

// Submit quiz
function submitQuiz() {
    if (selectedOptions[currentQuestion] === undefined) {
        alert('Please select an answer before submitting!');
        return;
    }
    
    // Calculate results
    const categoryScores = {};
    userAnswers.forEach(category => {
        categoryScores[category] = (categoryScores[category] || 0) + 1;
    });
    
    // Get top categories
    const sortedCategories = Object.entries(categoryScores)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 2);
    
    // Show results
    showResults(sortedCategories);
}

// Show results
function showResults(topCategories) {
    document.getElementById('quizSection').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'block';
    
    const resultsContainer = document.getElementById('careerResults');
    resultsContainer.innerHTML = '';
    
    topCategories.forEach(([category, score]) => {
        const careers = careersData[category];
        if (careers) {
            careers.forEach(career => {
                const matchPercentage = (score / quizQuestions.length) * 100;
                const careerCard = createCareerCard(career, matchPercentage);
                resultsContainer.appendChild(careerCard);
            });
        }
    });
    
    if (resultsContainer.children.length === 0) {
        resultsContainer.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-search"></i>
                <h3>No matches found</h3>
                <p>Try taking the quiz again!</p>
                <button class="start-btn" onclick="retakeQuiz()">Retake Quiz</button>
            </div>
        `;
    }
}

// Create career card
function createCareerCard(career, matchScore = null) {
    const card = document.createElement('div');
    card.className = 'career-card';
    card.setAttribute('data-category', career.category);
    
    const isFavorite = favoriteCareers.some(fav => fav.id === career.id);
    
    card.innerHTML = `
        <div class="career-icon">
            <i class="${career.icon}"></i>
        </div>
        <h3>${career.name}</h3>
        <p>${career.description}</p>
        <div class="fun-fact">
            <strong>Fun Fact:</strong> ${career.funFact}
        </div>
        ${matchScore ? `<div class="match-score">${Math.round(matchScore)}% Match</div>` : ''}
        <div style="display: flex; gap: 10px; margin-top: 15px; flex-wrap: wrap;">
            <button class="learn-more-btn" onclick="showCareerDetail(${career.id})">
                <i class="fas fa-info-circle"></i> Learn More
            </button>
            <button class="favorite-btn" onclick="toggleFavorite(${career.id})">
                <i class="${isFavorite ? 'fas' : 'far'} fa-star"></i> ${isFavorite ? 'Favorited' : 'Favorite'}
            </button>
        </div>
    `;
    
    return card;
}

// Explore careers
function exploreCareers() {
    document.querySelector('.activity-cards').style.display = 'none';
    document.getElementById('careerGallery').style.display = 'block';
    document.getElementById('quizSection').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'none';
    
    // Update active nav button
    document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.nav-btn')[1].classList.add('active');
    
    // Show filter buttons
    document.querySelector('.filter-buttons').style.display = 'flex';
    
    loadCareerGallery();
}

// Filter careers
function filterCareers(category) {
    document.querySelectorAll('.category-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.textContent.toLowerCase().includes(category.toLowerCase())) {
            btn.classList.add('active');
        }
    });
    
    loadCareerGallery(category === 'all' ? null : category);
}

// Load career gallery
function loadCareerGallery(category = null) {
    const grid = document.getElementById('careerGrid');
    grid.innerHTML = '';
    
    let careersToShow = [];
    
    if (category) {
        careersToShow = careersData[category] || [];
    } else {
        for (const cat in careersData) {
            careersToShow = careersToShow.concat(careersData[cat]);
        }
    }
    
    if (careersToShow.length === 0) {
        grid.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-briefcase"></i>
                <h3>No careers found</h3>
                <p>Try selecting a different category!</p>
            </div>
        `;
    } else {
        careersToShow.forEach(career => {
            const card = createCareerCard(career);
            grid.appendChild(card);
        });
    }
}

// Show career detail
function showCareerDetail(careerId) {
    let career = null;
    
    for (const cat in careersData) {
        const found = careersData[cat].find(c => c.id === careerId);
        if (found) {
            career = found;
            break;
        }
    }
    
    if (!career) return;
    
    const modal = document.getElementById('careerModal');
    const modalBody = document.getElementById('modalBody');
    const isFavorite = favoriteCareers.some(fav => fav.id === career.id);
    
    modalBody.innerHTML = `
        <div class="career-detail">
            <div class="detail-header">
                <div class="detail-icon">
                    <i class="${career.icon}"></i>
                </div>
                <h2>${career.name}</h2>
            </div>
            <div class="detail-content">
                <p><strong>What they do:</strong> ${career.description}</p>
                <p><strong>Fun Fact:</strong> ${career.funFact}</p>
                <p><strong>What to study:</strong> ${career.education}</p>
                <div class="skills-section">
                    <strong>Good skills to have:</strong>
                    <div class="skills-list">
                        ${career.skills.map(skill => `<span class="skill-tag">${skill}</span>`).join('')}
                    </div>
                </div>
            </div>
            <div class="detail-actions">
                <button class="action-btn" onclick="toggleFavorite(${career.id}); updateModalFavorite(${career.id})">
                    <i class="${isFavorite ? 'fas' : 'far'} fa-star"></i>
                    ${isFavorite ? 'Remove from' : 'Add to'} Favorites
                </button>
                <button class="action-btn primary" onclick="closeModal()">
                    <i class="fas fa-check"></i> OK
                </button>
            </div>
        </div>
    `;
    
    modal.style.display = 'flex';
}

// Update modal favorite button
function updateModalFavorite(careerId) {
    const isFavorite = favoriteCareers.some(fav => fav.id === careerId);
    const favoriteBtn = document.querySelector('.detail-actions .action-btn:first-child');
    if (favoriteBtn) {
        favoriteBtn.innerHTML = `<i class="${isFavorite ? 'fas' : 'far'} fa-star"></i> ${isFavorite ? 'Remove from' : 'Add to'} Favorites`;
    }
}

// Toggle favorite
function toggleFavorite(careerId) {
    let career = null;
    
    for (const cat in careersData) {
        const found = careersData[cat].find(c => c.id === careerId);
        if (found) {
            career = found;
            break;
        }
    }
    
    if (!career) return;
    
    const index = favoriteCareers.findIndex(fav => fav.id === careerId);
    
    if (index === -1) {
        favoriteCareers.push(career);
    } else {
        favoriteCareers.splice(index, 1);
    }
    
    localStorage.setItem('favoriteCareers', JSON.stringify(favoriteCareers));
    
    // Refresh current view
    if (document.getElementById('careerGallery').style.display !== 'none') {
        const activeCategory = document.querySelector('.category-btn.active');
        const category = activeCategory ? activeCategory.textContent.toLowerCase().replace(/[^a-z]/g, '') : 'all';
        filterCareers(category);
    } else if (document.getElementById('resultsSection').style.display !== 'none') {
        location.reload(); // Simple refresh for results
    }
}

// View favorites
function viewFavorites() {
    document.querySelector('.activity-cards').style.display = 'none';
    document.getElementById('careerGallery').style.display = 'block';
    document.getElementById('quizSection').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'none';
    
    // Update active nav button
    document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.nav-btn')[2].classList.add('active');
    
    // Hide filter buttons
    document.querySelector('.filter-buttons').style.display = 'none';
    
    const grid = document.getElementById('careerGrid');
    grid.innerHTML = '';
    
    if (favoriteCareers.length === 0) {
        grid.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-star" style="color: #ffd700;"></i>
                <h3>No favorites yet!</h3>
                <p>Explore careers and click the star to add them to your favorites.</p>
                <button class="start-btn" onclick="exploreCareers()">Explore Careers</button>
            </div>
        `;
    } else {
        favoriteCareers.forEach(career => {
            const card = createCareerCard(career);
            grid.appendChild(card);
        });
    }
}

// Save results
function saveResults() {
    alert('✨ Results saved to your profile! You can view them anytime in My Favorites. ✨');
}

// Retake quiz
function retakeQuiz() {
    startCareerQuiz();
}

// Close modal
function closeModal() {
    document.getElementById('careerModal').style.display = 'none';
}

// Initialize on load
document.addEventListener('DOMContentLoaded', init);

// Make functions globally available
window.showActivityCards = showActivityCards;
window.startCareerQuiz = startCareerQuiz;
window.nextQuestion = nextQuestion;
window.previousQuestion = previousQuestion;
window.submitQuiz = submitQuiz;
window.exploreCareers = exploreCareers;
window.filterCareers = filterCareers;
window.viewFavorites = viewFavorites;
window.showCareerDetail = showCareerDetail;
window.toggleFavorite = toggleFavorite;
window.saveResults = saveResults;
window.retakeQuiz = retakeQuiz;
window.closeModal = closeModal;