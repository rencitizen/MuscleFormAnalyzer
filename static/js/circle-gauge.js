/**
 * Circle Gauge Component
 * Animated circular progress gauge for form score visualization
 */

class CircleGauge {
  constructor(element, options = {}) {
    this.element = element;
    this.options = Object.assign({
      radius: 85,
      strokeWidth: 15,
      duration: 1000,
      color: {
        bad: 'var(--danger-color)',
        average: 'var(--warning-color)',
        good: 'var(--success-color)',
        default: 'var(--primary-color)'
      },
      thresholds: {
        bad: 50,
        average: 80
      },
      showText: true,
      label: 'Score'
    }, options);
    
    this.score = 0;
    this.targetScore = 0;
    this.animationStartTime = 0;
    this.animationStartScore = 0;
    this.initialized = false;
    
    this.init();
  }
  
  init() {
    // Create SVG elements
    this.createSvg();
    
    // Set initial state
    this.setScore(0, false); // No animation on init
    
    this.initialized = true;
  }
  
  createSvg() {
    // Clear existing content
    this.element.innerHTML = '';
    
    // Create SVG element
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('viewBox', '0 0 200 200');
    svg.setAttribute('width', '100%');
    svg.setAttribute('height', '100%');
    
    // Background circle
    const bgCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    bgCircle.classList.add('gauge-bg');
    bgCircle.setAttribute('cx', '100');
    bgCircle.setAttribute('cy', '100');
    bgCircle.setAttribute('r', this.options.radius.toString());
    bgCircle.setAttribute('stroke-width', this.options.strokeWidth.toString());
    
    // Foreground circle (progress)
    const fgCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    fgCircle.classList.add('gauge-fill');
    fgCircle.setAttribute('cx', '100');
    fgCircle.setAttribute('cy', '100');
    fgCircle.setAttribute('r', this.options.radius.toString());
    fgCircle.setAttribute('stroke-width', this.options.strokeWidth.toString());
    this.fgCircle = fgCircle;
    
    svg.appendChild(bgCircle);
    svg.appendChild(fgCircle);
    
    // Add text if needed
    if (this.options.showText) {
      // Score text
      const scoreText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      scoreText.classList.add('gauge-text');
      scoreText.setAttribute('x', '100');
      scoreText.setAttribute('y', '100');
      scoreText.textContent = '0';
      this.scoreText = scoreText;
      
      // Label text
      const labelText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      labelText.classList.add('gauge-label');
      labelText.setAttribute('x', '100');
      labelText.setAttribute('y', '125');
      labelText.textContent = this.options.label;
      
      svg.appendChild(scoreText);
      svg.appendChild(labelText);
    }
    
    this.element.appendChild(svg);
  }
  
  setScore(score, animate = true) {
    // Clamp score between 0 and 100
    score = Math.max(0, Math.min(100, score));
    
    this.targetScore = score;
    
    if (!animate || !this.initialized) {
      // Update immediately without animation
      this.score = score;
      this.updateGauge();
    } else {
      // Start animation
      this.animationStartTime = performance.now();
      this.animationStartScore = this.score;
      requestAnimationFrame(() => this.animateGauge());
    }
  }
  
  animateGauge() {
    const now = performance.now();
    const elapsed = now - this.animationStartTime;
    const progress = Math.min(1, elapsed / this.options.duration);
    
    // Ease function (cubic ease out)
    const easeProgress = 1 - Math.pow(1 - progress, 3);
    
    // Calculate current score based on animation progress
    this.score = this.animationStartScore + 
                (this.targetScore - this.animationStartScore) * easeProgress;
    
    // Update gauge display
    this.updateGauge();
    
    // Continue animation if not finished
    if (progress < 1) {
      requestAnimationFrame(() => this.animateGauge());
    }
  }
  
  updateGauge() {
    // Calculate circle properties
    const circumference = 2 * Math.PI * this.options.radius;
    const offset = circumference - (this.score / 100) * circumference;
    
    // Update stroke-dasharray and stroke-dashoffset
    this.fgCircle.style.strokeDasharray = circumference.toString();
    this.fgCircle.style.strokeDashoffset = offset.toString();
    
    // Update color based on score
    if (this.score < this.options.thresholds.bad) {
      this.fgCircle.style.stroke = this.options.color.bad;
    } else if (this.score < this.options.thresholds.average) {
      this.fgCircle.style.stroke = this.options.color.average;
    } else {
      this.fgCircle.style.stroke = this.options.color.good;
    }
    
    // Update text if needed
    if (this.options.showText && this.scoreText) {
      this.scoreText.textContent = Math.round(this.score).toString();
    }
  }
}

// Usage:
// const gauge = new CircleGauge(document.querySelector('.gauge-container'));
// gauge.setScore(75); // Animates to 75%