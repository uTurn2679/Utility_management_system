// --- Presentation Slide Navigation Logic ---
let currentSlide = 1;
const totalSlides = 9;

// Predefined Agent PEAS Data
const agentsData = {
  taxi: {
    title: "Automated Taxi Driver",
    description: "A self-driving vehicle that must transport passengers safely and efficiently through urban traffic.",
    p: [
      "Safe delivery of passenger",
      "Minimized journey time and cost",
      "Legal driving (obey traffic rules)",
      "Comfortable ride experience"
    ],
    e: [
      "Public roads and highways",
      "Other motorists, pedestrians, and cyclists",
      "Weather variations and road hazards",
      "Traffic signals and signs"
    ],
    a: [
      "Steering wheel motor",
      "Accelerator and brake pedals",
      "Turn signals and horn",
      "Display screen / audio alerts for passengers"
    ],
    s: [
      "Cameras & Computer Vision",
      "Lidar / Radar depth sensors",
      "GPS / Inertial navigation units",
      "Odometer and engine tachometers"
    ]
  },
  medical: {
    title: "Medical Diagnosis System",
    description: "An AI advisor used by doctors to analyze patient data, symptoms, and medical history to diagnose diseases.",
    p: [
      "Correct diagnosis of illness",
      "Minimized costs and treatment delays",
      "Patient health maximization",
      "Reduced probability of legal issues"
    ],
    e: [
      "Patient health conditions",
      "Hospital staff and laboratories",
      "Medical databases and records"
    ],
    a: [
      "Screen displays of diagnosis",
      "Suggested treatment plans & prescriptions",
      "Referral recommendations"
    ],
    s: [
      "Keyboard / voice inputs (symptoms, patient history)",
      "Lab test results and imaging reports",
      "Vital sign telemetry feeds"
    ]
  },
  soccer: {
    title: "Robot Soccer Player",
    description: "An autonomous humanoid robot playing a soccer match in cooperation with teammates against an opposing team.",
    p: [
      "Number of goals scored",
      "Number of goals conceded (minimize)",
      "Adherence to game rules (no fouls)",
      "Cooperative passing metrics"
    ],
    e: [
      "Soccer field (grass/turf)",
      "The soccer ball",
      "Teammates and opponent players",
      "Referee decisions"
    ],
    a: [
      "Locomotion (legs/joints or wheels)",
      "Kicker mechanism / arm movement",
      "Communication speaker or wireless transmitter"
    ],
    s: [
      "Stereo visual cameras (ball and player tracking)",
      "Touch / pressure sensors in feet",
      "Inertial measurement unit (balance)",
      "Wireless communicator (teammate positions)"
    ]
  },
  shopping: {
    title: "E-commerce Shopping Agent",
    description: "A digital assistant that autonomously finds, compares, and purchases items based on user preferences.",
    p: [
      "Minimized cost for target items",
      "Item quality/reputation (high reviews)",
      "User satisfaction rating",
      "Transaction security and speed"
    ],
    e: [
      "Internet shopping sites (Amazon, eBay, etc.)",
      "Competitor agent prices",
      "User budget constraints"
    ],
    a: [
      "Web requests (navigation, item selection)",
      "Automated payment transaction calls",
      "User notification interface"
    ],
    s: [
      "Web page HTML parser / API data",
      "User query input (search query, budget limits)",
      "Email receipt parsers"
    ]
  },
  vacuum: {
    title: "Vacuum Cleaner Agent",
    description: "A robotic device designed to clean floors in a home environment while avoiding hazards and returning to its dock.",
    p: [
      "Percentage of dirt/dust removed",
      "Minimized battery power consumed",
      "Minimized structural collisions (no damage)",
      "Clean speed / room coverage percentage"
    ],
    e: [
      "Home floor surfaces (wood, carpet, tile)",
      "Furniture, obstacles, and pets",
      "Stairs (cliff hazard)",
      "Dust and debris distribution"
    ],
    a: [
      "Drive wheels and steering motors",
      "Vacuum suction motor",
      "Rotating sweep brushes",
      "Audio buzzer / indicator LEDs"
    ],
    s: [
      "Infrared bump sensors",
      "Optical dirt sensors",
      "Cliff sensors (floor edge detection)",
      "Battery level gauge"
    ]
  }
};

// Initialize Slide Deck
function initSlides() {
  // Populate dots in the footer
  const dotsContainer = document.getElementById('slideDots');
  dotsContainer.innerHTML = '';
  for (let i = 1; i <= totalSlides; i++) {
    const dot = document.createElement('div');
    dot.className = `dot ${i === 1 ? 'active' : ''}`;
    dot.onclick = () => goToSlide(i);
    dotsContainer.appendChild(dot);
  }
  
  // Initialize Lucide Icons
  lucide.createIcons();
  
  // Set initial progress
  updateProgressBar();
}

// Navigate to specific slide
function goToSlide(slideNum) {
  if (slideNum < 1 || slideNum > totalSlides) return;
  
  // Remove active class from current slide
  document.getElementById(`slide-${currentSlide}`).classList.remove('active');
  
  // Update slide index
  currentSlide = slideNum;
  
  // Add active class to new slide
  const targetSlide = document.getElementById(`slide-${currentSlide}`);
  targetSlide.classList.add('active');
  
  // Focus slide top if scrollable
  targetSlide.scrollTop = 0;
  
  // Update control bar UI
  document.getElementById('slideIndicator').textContent = `Slide ${currentSlide} / ${totalSlides}`;
  
  // Enable/Disable buttons
  document.getElementById('prevBtn').disabled = currentSlide === 1;
  document.getElementById('nextBtn').disabled = currentSlide === totalSlides;
  
  // Update dots
  const dots = document.querySelectorAll('.slide-dots .dot');
  dots.forEach((dot, index) => {
    if (index + 1 === currentSlide) {
      dot.classList.add('active');
    } else {
      dot.classList.remove('active');
    }
  });
  
  updateProgressBar();
}

function nextSlide() {
  if (currentSlide < totalSlides) {
    goToSlide(currentSlide + 1);
  }
}

function prevSlide() {
  if (currentSlide > 1) {
    goToSlide(currentSlide - 1);
  }
}

function updateProgressBar() {
  const percentage = ((currentSlide - 1) / (totalSlides - 1)) * 100;
  document.getElementById('progressBar').style.width = `${percentage}%`;
}

// Fullscreen API Integration
function toggleFullscreen() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen().catch(err => {
      console.error(`Error attempting to enable full-screen mode: ${err.message}`);
    });
  } else {
    document.exitFullscreen();
  }
}

// Keyboard Navigation Listeners
document.addEventListener('keydown', (e) => {
  // If user is typing in the sandbox fields, don't trigger slide change
  if (document.activeElement.tagName === 'INPUT' || document.activeElement.tagName === 'TEXTAREA') {
    return;
  }
  
  if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') {
    nextSlide();
  } else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
    prevSlide();
  }
});

// --- PEAS Showcase Logic ---
const selectorButtons = document.querySelectorAll('.selector-btn');
selectorButtons.forEach(btn => {
  btn.addEventListener('click', (e) => {
    // Set active button
    selectorButtons.forEach(b => b.classList.remove('active'));
    const target = e.currentTarget;
    target.classList.add('active');
    
    // Get agent data key
    const agentKey = target.getAttribute('data-agent');
    const data = agentsData[agentKey];
    
    if (data) {
      // Update showcase details
      document.getElementById('showcase-agent-title').textContent = data.title;
      document.getElementById('showcase-agent-desc').textContent = data.description;
      
      // Update Lists
      updateShowcaseList('showcase-p-list', data.p);
      updateShowcaseList('showcase-e-list', data.e);
      updateShowcaseList('showcase-a-list', data.a);
      updateShowcaseList('showcase-s-list', data.s);
      
      // Trigger card updates micro-animations
      const cards = document.querySelectorAll('.showcase-card');
      cards.forEach(card => {
        card.classList.remove('active-change');
        void card.offsetWidth; // Trigger reflow to restart animation
        card.classList.add('active-change');
      });
    }
  });
});

function updateShowcaseList(elementId, items) {
  const container = document.getElementById(elementId);
  container.innerHTML = '';
  items.forEach(item => {
    const li = document.createElement('li');
    li.textContent = item;
    container.appendChild(li);
  });
}

// --- PEAS Sandbox Logic ---
function generateSandboxCard() {
  const name = document.getElementById('agent-name').value || "Unnamed Agent";
  const p = document.getElementById('agent-p').value || "No performance measure specified.";
  const e = document.getElementById('agent-e').value || "No environment specified.";
  const a = document.getElementById('agent-a').value || "No actuators specified.";
  const s = document.getElementById('agent-s').value || "No sensors specified.";
  
  // Update Preview UI
  document.getElementById('preview-title').textContent = name;
  document.getElementById('preview-p').textContent = p;
  document.getElementById('preview-e').textContent = e;
  document.getElementById('preview-a').textContent = a;
  document.getElementById('preview-s').textContent = s;
  
  // Add subtle glow animation trigger to sandbox card
  const card = document.getElementById('sandboxCard');
  card.style.transform = 'scale(1.03) translateY(-5px)';
  card.style.borderColor = 'var(--accent-purple)';
  setTimeout(() => {
    card.style.transform = '';
    card.style.borderColor = 'rgba(99, 102, 241, 0.2)';
  }, 500);
}

function downloadSpecAsText() {
  const name = document.getElementById('preview-title').textContent;
  const p = document.getElementById('preview-p').textContent;
  const e = document.getElementById('preview-e').textContent;
  const a = document.getElementById('preview-a').textContent;
  const s = document.getElementById('preview-s').textContent;
  
  const textSpec = 
`=========================================
PEAS TASK ENVIRONMENT SPECIFICATION
=========================================
Agent: ${name}

P - Performance Measure:
  ${p}

E - Environment:
  ${e}

A - Actuators:
  ${a}

S - Sensors:
  ${s}
=========================================`;

  navigator.clipboard.writeText(textSpec).then(() => {
    // Dynamic feedback on button
    const btn = document.querySelector('.card-footer .btn-text');
    const originalHTML = btn.innerHTML;
    btn.innerHTML = `<i data-lucide="check" class="text-emerald-400"></i><span class="text-emerald-400">Copied!</span>`;
    lucide.createIcons();
    setTimeout(() => {
      btn.innerHTML = originalHTML;
      lucide.createIcons();
    }, 2000);
  }).catch(err => {
    console.error('Failed to copy text: ', err);
  });
}

// On Load Run
window.addEventListener('DOMContentLoaded', initSlides);
