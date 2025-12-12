document.addEventListener('DOMContentLoaded', () => {
    const claimInput = document.getElementById('claimInput');
    const verifyBtn = document.getElementById('verifyBtn');
    const resultSection = document.getElementById('resultSection');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const loadingText = document.getElementById('loadingText');
    const charCount = document.getElementById('charCount');

    // Stats Elements
    const resultLabel = document.getElementById('resultLabel');
    const confidenceScore = document.getElementById('confidenceScore');
    const confidenceCircle = document.getElementById('confidenceCircle');
    const evidenceList = document.getElementById('evidenceList');
    const resultBar = document.getElementById('resultBar');

    // Character Count
    claimInput.addEventListener('input', () => {
        const len = claimInput.value.length;
        charCount.textContent = len;
        if (len > 500) {
            charCount.classList.add('text-red-500');
            verifyBtn.disabled = true;
            verifyBtn.classList.add('opacity-50', 'cursor-not-allowed');
        } else {
            charCount.classList.remove('text-red-500');
            verifyBtn.disabled = false;
            verifyBtn.classList.remove('opacity-50', 'cursor-not-allowed');
        }
    });

    // Verification Logic
    verifyBtn.addEventListener('click', async () => {
        const claim = claimInput.value.trim();
        
        if (!claim) {
            alert('Please enter a claim to verify.');
            return;
        }

        // Show Loading
        loadingOverlay.classList.remove('hidden');
        resultSection.classList.add('hidden');
        
        // Animated Loading Text
        const steps = [
            "Extracting Facutal Claims...",
            "Scanning Knowledge Base...",
            "Retrieving Global Evidence...",
            "Running NLI Models...",
            "Calculating Consensus..."
        ];
        
        let stepIndex = 0;
        const interval = setInterval(() => {
            if(stepIndex < steps.length) {
                loadingText.textContent = steps[stepIndex];
                stepIndex++;
            }
        }, 800);

        try {
            const response = await fetch('/api/verify', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ claim: claim })
            });

            clearInterval(interval);
            const data = await response.json();

            if (data.error) {
                throw new Error(data.error);
            }

            // Update UI with results
            displayResults(data);

        } catch (error) {
            clearInterval(interval);
            alert('Error: ' + error.message);
        } finally {
            loadingOverlay.classList.add('hidden');
        }
    });

    function displayResults(data) {
        resultSection.classList.remove('hidden');
        
        // 1. Label
        resultLabel.textContent = data.label;
        
        // Color coding
        let colorClass = 'text-gray-400';
        let barColor = 'bg-gray-400';
        let strokeColor = 'text-gray-400';
        
        if (data.label.toLowerCase() === 'true') {
            colorClass = 'text-neon-green';
            barColor = 'bg-green-500';
            strokeColor = 'text-green-500';
            resultLabel.style.color = '#4ade80'; // Tailwind green-400
        } else if (data.label.toLowerCase() === 'false') {
            colorClass = 'text-neon-red';
            barColor = 'bg-red-500';
            strokeColor = 'text-red-500';
            resultLabel.style.color = '#f87171'; // Tailwind red-400
        } else {
            resultLabel.style.color = '#fbbf24'; // Tailwind amber-400
            barColor = 'bg-amber-400';
            strokeColor = 'text-amber-400';
        }

        resultBar.className = `absolute top-0 left-0 w-1 h-full ${barColor}`;
        confidenceCircle.setAttribute('class', strokeColor);

        // 2. Confidence
        const percentage = Math.round(data.confidence * 100);
        confidenceScore.textContent = `${percentage}%`;
        
        // Animate Circle
        // C = 2 * pi * r = 2 * 3.14159 * 28 ≈ 175.9
        const circumference = 175.9;
        const offset = circumference - (data.confidence * circumference);
        confidenceCircle.style.strokeDasharray = `${circumference} ${circumference}`;
        confidenceCircle.style.strokeDashoffset = offset;

        // 3. Evidence
        // Format markdown-like evidence summary
        const formattedEvidence = data.evidence
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n/g, '<br>');
        
        evidenceList.innerHTML = formattedEvidence;
        
        // Scroll to results
        resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
});
