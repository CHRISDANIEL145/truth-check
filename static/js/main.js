// static/js/main.js - Frontend logic for TruthCheck

document.addEventListener('DOMContentLoaded', () => {
    // Get references to DOM elements
    const claimInput = document.getElementById('claimInput');
    const verifyButton = document.getElementById('verifyButton');
    const buttonText = document.getElementById('buttonText');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const resultContainer = document.getElementById('resultContainer');
    const resultContent = document.getElementById('resultContent');
    const userIdDisplay = document.getElementById('userIdDisplay');
    const exampleTags = document.querySelectorAll('.example-tag'); // Get all example tags

    // Set a placeholder user ID (in a real app, this would come from authentication)
    userIdDisplay.textContent = 'Guest (Not authenticated)'; // Or generate a random one: `crypto.randomUUID()`

    // Add event listener to the Verify button
    verifyButton.addEventListener('click', async () => {
        const claimText = claimInput.value.trim(); // Get text and remove leading/trailing whitespace

        // Basic input validation
        if (!claimText) {
            displayResult('Error', 0.0, 'Please enter a claim to verify.', 'truth-red', '❗'); // Using custom color
            return;
        }

        // Show loading state
        setLoadingState(true);

        try {
            // Make a POST request to your Flask API
            const response = await fetch('/api/verify', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ claim: claimText }), // Send the claim as JSON
            });

            // Check if the response was successful
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }

            // Parse the JSON response
            const data = await response.json();

            // Determine color and emoji based on the label (using custom colors)
            let resultColor = 'truth-blue'; // Default for neutral
            let emoji = '❓';
            if (data.label === 'True') {
                resultColor = 'truth-green';
                emoji = '✅';
            } else if (data.label === 'False') {
                resultColor = 'truth-red';
                emoji = '❌';
            } else if (data.label === 'Low Confidence') {
                resultColor = 'truth-orange';
                emoji = '⚠️';
            } else if (data.label === 'Error') {
                resultColor = 'truth-red';
                emoji = '❗';
            }

            // Display the result
            displayResult(data.label, data.confidence, data.evidence, resultColor, emoji);

        } catch (error) {
            // Handle any errors during the fetch operation
            console.error('Fetch error:', error);
            displayResult('Error', 0.0, `Could not verify claim. ${error.message}`, 'truth-red', '❗'); // Using custom color
        } finally {
            // Hide loading state regardless of success or failure
            setLoadingState(false);
        }
    });

    // Add event listeners for example tags
    exampleTags.forEach(tag => {
        tag.addEventListener('click', () => {
            claimInput.value = tag.dataset.claim; // Set claim input to the tag's data-claim
            verifyButton.click(); // Trigger the verify button click
        });
    });


    /**
     * Sets the loading state of the button and input.
     * @param {boolean} isLoading - True to show loading, false to hide.
     */
    function setLoadingState(isLoading) {
        if (isLoading) {
            buttonText.textContent = 'Verifying...';
            loadingSpinner.classList.remove('hidden');
            verifyButton.disabled = true; // Disable button to prevent multiple clicks
            claimInput.disabled = true; // Disable input during processing
            resultContainer.classList.add('hidden'); // Hide previous results
            verifyButton.classList.add('opacity-75', 'cursor-not-allowed'); // Dim button
        } else {
            buttonText.textContent = 'Verify Claim';
            loadingSpinner.classList.add('hidden');
            verifyButton.disabled = false; // Re-enable button
            claimInput.disabled = false; // Re-enable input
            verifyButton.classList.remove('opacity-75', 'cursor-not-allowed'); // Restore button style
        }
    }

    /**
     * Displays the verification result in the UI.
     * @param {string} label - The verification label (True, False, Low Confidence, Error).
     * @param {number} confidence - The confidence score.
     * @param {string} evidence - The evidence snippet.
     * @param {string} color - Tailwind color class (e.g., 'truth-green', 'truth-red', 'truth-orange').
     * @param {string} emoji - Emoji to display with the label.
     */
    function displayResult(label, confidence, evidence, color, emoji) {
        resultContainer.classList.remove('hidden'); // Show the result container

        // Format confidence as percentage
        const confidencePct = (confidence * 100).toFixed(1) + '%';

        // Construct the HTML for the result content
        resultContent.innerHTML = `
            <div class="p-6 sm:p-8 rounded-lg border-4 border-${color}-500 bg-${color}-50 text-${color}-800 shadow-xl transition-all duration-300 ease-in-out transform hover:scale-[1.005]">
                <h3 class="text-3xl sm:text-4xl font-extrabold mb-4 flex items-center justify-center">
                    ${emoji} <span class="ml-3">${label}</span>
                </h3>
                <p class="text-xl sm:text-2xl font-semibold mb-3">
                    <strong>Confidence:</strong> <span class="text-${color}-700">${confidencePct}</span>
                </p>
                <p class="text-lg sm:text-xl font-medium mb-3"><strong>Evidence:</strong></p>
                <div class="bg-white p-4 sm:p-5 rounded-md shadow-inner border border-gray-200 text-gray-700 whitespace-pre-wrap overflow-auto max-h-64 text-base leading-relaxed">
                    ${evidence}
                </div>
            </div>
        `;
        // Scroll to the result container for better UX on mobile
        resultContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
});
