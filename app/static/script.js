document.addEventListener('DOMContentLoaded', function() {
    const commonOptions = {
        mode: 'python',
        theme: 'shadowfox',  // ShadowFox theme
        lineNumbers: true,
        lineWrapping: false,  // Disable line wrapping
        scrollbarStyle: 'simple',  // Use the simple scrollbar style
        indentUnit: 4,
        tabSize: 4,
        viewportMargin: Infinity,
        extraKeys: {
            "Ctrl-/": "toggleComment",
            "Ctrl-Space": "autocomplete"
        }
    };

    const inputCodeEditor = CodeMirror.fromTextArea(document.getElementById('codeInput'), {
        ...commonOptions,
        autoCloseBrackets: true
    });

    const outputCodeEditor = CodeMirror.fromTextArea(document.getElementById('codeOutput'), {
        ...commonOptions,
        readOnly: true
    });

    // Current response data storage
    let currentResponseData = null;
    let displayMode = 'code'; // Default to code mode
    const markdownOutput = document.getElementById('markdownOutput');
    
    // Ensure proper horizontal scrolling
    function refreshEditors() {
        inputCodeEditor.refresh();
        outputCodeEditor.refresh();
    }
    
    // Refresh after initialization and on window resize
    setTimeout(refreshEditors, 100);
    window.addEventListener('resize', refreshEditors);
    
    // Initialize marked with options
    marked.setOptions({
        breaks: true,
        gfm: true,
        headerIds: false
    });
    
    // Handle display mode toggle
    document.getElementById('displayModeToggle').addEventListener('change', function() {
        const isRawMode = this.checked;
        displayMode = isRawMode ? 'raw' : 'code';
        
        // Update toggle labels
        document.querySelectorAll('.toggle-label').forEach(label => {
            if (label.dataset.mode === displayMode) {
                label.classList.add('active');
            } else {
                label.classList.remove('active');
            }
        });
        
        // Toggle visibility of code editor and markdown container
        if (displayMode === 'raw') {
            outputCodeEditor.getWrapperElement().style.display = 'none';
            markdownOutput.style.display = 'block';
        } else {
            outputCodeEditor.getWrapperElement().style.display = 'block';
            markdownOutput.style.display = 'none';
        }
        
        // Update display if we have data
        if (currentResponseData) {
            updateOutputDisplay();
        }
    });
    
    // Handle toggle label clicks
    document.querySelectorAll('.toggle-label').forEach(label => {
        label.addEventListener('click', function() {
            const mode = this.dataset.mode;
            const toggle = document.getElementById('displayModeToggle');
            
            if (mode === 'raw') {
                toggle.checked = true;
            } else {
                toggle.checked = false;
            }
            
            // Trigger the change event
            const event = new Event('change');
            toggle.dispatchEvent(event);
        });
    });
    
    // Function to update the output display based on the current mode
    function updateOutputDisplay() {
        if (!currentResponseData) return;
        
        if (displayMode === 'raw') {
            // Render markdown for raw response
            const rawContent = currentResponseData.raw_response || 'No raw response available';
            markdownOutput.innerHTML = marked.parse(rawContent);
        } else {
            // Update code editor
            outputCodeEditor.setValue(currentResponseData.output);
        }
    }

    // Handle Send button click
    document.getElementById('sendButton').addEventListener('click', async function() {
        const instructions = document.getElementById('instructions').value;
        const code = inputCodeEditor.getValue();
    
        try {
            // Show loading state
            const sendButton = document.getElementById('sendButton');
            sendButton.textContent = 'Processing...';
            sendButton.disabled = true;
            
            // Send data to the backend
            const response = await fetch('/process-instruction', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    userInstruction: instructions,
                    userCode: code
                })
            });
    
            if (!response.ok) {
                throw new Error(`Server responded with status: ${response.status}`);
            }
    
            currentResponseData = await response.json();
            
            // Display the processed output based on current mode
            updateOutputDisplay();
        } catch (error) {
            console.error('Error:', error);
            // Display error in the output area
            outputCodeEditor.setValue(`Error: ${error.message || 'Failed to process request'}`);
            currentResponseData = null;
        } finally {
            // Reset button state
            const sendButton = document.getElementById('sendButton');
            sendButton.textContent = 'Send';
            sendButton.disabled = false;
        }
    });

    // Handle Copy button click
    document.getElementById('copyButton').addEventListener('click', function() {
        // Get content based on current display mode
        let contentToCopy;
        
        if (displayMode === 'raw' && currentResponseData) {
            contentToCopy = currentResponseData.raw_response || '';
        } else {
            contentToCopy = outputCodeEditor.getValue();
        }
        
        // Copy to clipboard
        navigator.clipboard.writeText(contentToCopy).then(function() {
            // Provide visual feedback
            const copyButton = document.getElementById('copyButton');
            copyButton.textContent = 'Copied!';
            copyButton.classList.add('copied');
            
            // Reset button text after 2 seconds
            setTimeout(function() {
                copyButton.textContent = 'Copy';
                copyButton.classList.remove('copied');
            }, 2000);
        }).catch(function(err) {
            console.error('Failed to copy text: ', err);
        });
    });
    
    // Handle Copy to Input button click
    document.getElementById('copyToInputButton').addEventListener('click', function() {
        // Always copy the code content (not raw) to input
        const contentToCopy = currentResponseData ? currentResponseData.output : outputCodeEditor.getValue();
        
        // Copy to input editor
        inputCodeEditor.setValue(contentToCopy);
        
        // Provide visual feedback
        const copyToInputButton = document.getElementById('copyToInputButton');
        copyToInputButton.textContent = '✓';
        copyToInputButton.classList.add('copied');
        
        // Reset button text after 2 seconds
        setTimeout(function() {
            copyToInputButton.textContent = '<';
            copyToInputButton.classList.remove('copied');
        }, 2000);
    });
    
    // Handle Reset button click
    document.getElementById('resetButton').addEventListener('click', function() {
        // Reset all inputs and outputs
        document.getElementById('instructions').value = '';
        inputCodeEditor.setValue('');
        
        // Reset both output displays regardless of which is visible
        outputCodeEditor.setValue('');
        markdownOutput.innerHTML = '';
        
        // Clear the stored response data
        currentResponseData = null;
    
        // Force a refresh of the CodeMirror instance
        outputCodeEditor.refresh();
    });
});