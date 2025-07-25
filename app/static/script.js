document.addEventListener('DOMContentLoaded', function() {
    // Set up history panel functionality
    const historyPanel = document.querySelector('.history-panel');
    const historyToggle = document.querySelector('.history-toggle');
    
    // Object to store history data from server
    let historyData = {};
    
    // Object to store model data from server
    let modelData = {
        availableModels: ['Add a model'],
        currentModel: null
    };
    
    // Function to fetch model data from server
    async function fetchModelData() {
        try {
            const response = await fetch('/api/v1/model');
            if (!response.ok) {
                throw new Error(`Server responded with status: ${response.status}`);
            }
            
            const data = await response.json();
            modelData.availableModels = data.available_models || [];
            modelData.currentModel = data.current_model || '';
            
            // Update model selection dropdown
            updateModelSelector();
        } catch (error) {
            console.error('Error fetching model data:', error);
        }
    }
    
    // Function to update the model selector dropdown
    function updateModelSelector() {
        const modelSelect = document.getElementById('modelSelect');

        // Clear existing options
        modelSelect.innerHTML = '';
        
        // Add options for each available model
        modelData.availableModels.forEach(model => {
            const option = document.createElement('option');
            option.value = model;
            option.textContent = model;
            if (model === modelData.currentModel) {
                option.selected = true;
            }
            modelSelect.appendChild(option);
        });
    }
    
    // Function to set the current model
    async function setCurrentModel(modelName) {
        try {
            const response = await fetch('/api/v1/model', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    model: modelName
                })
            });
            
            if (!response.ok) {
                throw new Error(`Server responded with status: ${response.status}`);
            }
            
            const data = await response.json();
            if (data.success) {
                modelData.currentModel = modelName;
                console.log(`Model successfully set to: ${modelName}`);
                    return true; // Return success status
                } else {
                    const errorMsg = data.error || 'Unknown error';
                    console.error(`Failed to set model: ${errorMsg}`);
                    throw new Error(errorMsg);
                }
            } catch (error) {
                console.error('Error setting model:', error);
                throw error; // Re-throw to allow caller to handle
        }
    }
    
    // Add event listener for model selection changes
    document.getElementById('modelSelect').addEventListener('change', function() {
        const selectedModel = this.value;
        if (selectedModel && selectedModel !== modelData.currentModel) {
            setCurrentModel(selectedModel);
        }
    });
    
    // Modal elements
    const addModelModal = document.getElementById('addModelModal');
    const newModelNameInput = document.getElementById('newModelName');
    const modelNameError = document.getElementById('modelNameError');
    const confirmAddModelButton = document.getElementById('confirmAddModel');
    const cancelAddModelButton = document.getElementById('cancelAddModel');
    const closeModalButton = document.getElementById('closeModalButton');
    
    // Function to show the modal
    function showAddModelModal() {
        // Clear any previous input and errors
        newModelNameInput.value = '';
        modelNameError.textContent = '';
        
        // Show the modal
        addModelModal.classList.add('visible');
        
        // Focus the input field
        setTimeout(() => {
            newModelNameInput.focus();
        }, 100);
    }
    
    // Function to hide the modal
    function hideAddModelModal() {
        addModelModal.classList.remove('visible');
    }
    
    // Function to handle model addition
    async function handleAddModel() {
        const modelName = newModelNameInput.value.trim();
        
        // Validate input
        if (!modelName) {
            modelNameError.textContent = 'Please enter a model name';
            return;
        }
        
        // Reset error message
        modelNameError.textContent = '';
        
        // Disable confirm button and show loading state
        confirmAddModelButton.disabled = true;
        const originalButtonText = confirmAddModelButton.innerHTML;
        confirmAddModelButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adding...';
        
        try {
            // Try to set the new model
            await setCurrentModel(modelName);
            
            // If successful, refresh model list and hide modal
            await fetchModelData();
            hideAddModelModal();
            
            // Show success indicator on the add button
            const addButton = document.getElementById('addModelButton');
            addButton.classList.add('activated');
            
            setTimeout(() => {
                addButton.classList.remove('activated');
            }, 1000);
            
        } catch (error) {
            // Show error in modal
            modelNameError.textContent = `Failed to add model: ${error.message || 'Unknown error'}`;
            console.error('Error adding model:', error);
        } finally {
            // Reset button state
            confirmAddModelButton.disabled = false;
            confirmAddModelButton.innerHTML = originalButtonText;
        }
    }
    
    // Add event listener for add model button to show modal
    document.getElementById('addModelButton').addEventListener('click', showAddModelModal);
    
    // Add event listeners for modal buttons
    confirmAddModelButton.addEventListener('click', handleAddModel);
    cancelAddModelButton.addEventListener('click', hideAddModelModal);
    closeModalButton.addEventListener('click', hideAddModelModal);
    
    // Allow pressing Enter in the input field to submit
    newModelNameInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            handleAddModel();
        }
    });
    
    // Close modal when clicking outside
    addModelModal.addEventListener('click', function(e) {
        if (e.target === addModelModal) {
            hideAddModelModal();
        }
    });
    
    // Close modal when pressing Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && addModelModal.classList.contains('visible')) {
            hideAddModelModal();
        }
    });
    
    // Common function for button activation feedback
    function addButtonFeedback(buttonId, activeClass = 'activated', duration = 1000) {
        const button = document.getElementById(buttonId);
        if (button) {
            button.addEventListener('click', function() {
                this.classList.add(activeClass);
                setTimeout(() => {
                    this.classList.remove(activeClass);
                }, duration);
            });
        }
    }
    
    // Apply feedback to multiple buttons at once
    function applyFeedbackToButtons(buttonIds, activeClass = 'activated', duration = 1000) {
        buttonIds.forEach(id => addButtonFeedback(id, activeClass, duration));
    }
    
    // Apply feedback to buttons
    applyFeedbackToButtons(['sendButton', 'resetButton', 'addModelButton', 'copyButton', 'copyToInputButton']);

    // Fill model selector with placeholder
    updateModelSelector();
    
    // Fetch model data when page loads
    fetchModelData();
    
    // Function to fetch history data from server
    async function fetchHistoryData() {
        try {
            const response = await fetch('/api/v1/history');
            if (!response.ok) {
                throw new Error(`Server responded with status: ${response.status}`);
            }
            
            const data = await response.json();
            if (data.success && data.history) {
                // Process history data and format it for our use
                historyData = {};
                data.history.forEach((entry, index) => {
                    historyData[index] = {
                        instructions: entry.instructions,
                        input: entry.code,
                        output: entry.output_code,
                        raw_response: entry.raw_response,
                        timestamp: entry.timestamp
                    };
                });
                
                // Render history entries
                renderHistoryEntries();
            }
        } catch (error) {
            console.error('Error fetching history:', error);
        }
    }
    
    // Function to render history entries in the panel
    function renderHistoryEntries() {
        const historyContainer = document.querySelector('.history-entries');
        
        // Clear existing entries
        historyContainer.innerHTML = '';
        
        // Create entries for each history item
        Object.keys(historyData).reverse().forEach(id => {
            const entry = historyData[id];
            const entryElement = document.createElement('div');
            entryElement.className = 'history-entry';
            entryElement.setAttribute('data-id', id);
            
            // Create truncated instruction text
            const instructionText = entry.instructions.length > 40 
                ? entry.instructions.substring(0, 40) + '...' 
                : entry.instructions;
            
            // Format the timestamp
            const timeString = formatTimestamp(entry.timestamp);
            
            entryElement.innerHTML = `
                <div class="history-entry-time">${timeString}</div>
                <div class="history-entry-title">${instructionText}</div>
                <div class="history-entry-snippet">${getCodeSnippet(entry.input)}</div>
            `;
            
            historyContainer.appendChild(entryElement);
            
            // Add click event listener
            entryElement.addEventListener('click', function() {
                // Remove active class from all entries
                document.querySelectorAll('.history-entry').forEach(e => e.classList.remove('active'));
                
                // Add active class to clicked entry
                this.classList.add('active');
                
                // Get history data for this entry
                const historyId = this.getAttribute('data-id');
                const data = historyData[historyId];
                
                if (data) {
                    // Populate the form with history data
                    document.getElementById('instructions').value = data.instructions;
                    inputCodeEditor.setValue(data.input);
                    
                    // Set response data and update output
                    currentResponseData = {
                        output: data.output,
                        raw_response: data.raw_response
                    };
                    
                    updateOutputDisplay();
                }
            });
        });
    }
    
    // Helper function to get a short code snippet
    function getCodeSnippet(code) {
        if (!code) return '';
        const lines = code.split('\n');
        return lines.length > 0 ? lines[0].substring(0, 30) : '';
    }
    
    // Helper function to format timestamp
    function formatTimestamp(timestamp) {
        if (!timestamp) return '';
        
        const date = new Date(timestamp);
        
        // Check if date is valid
        if (isNaN(date.getTime())) return '';
        
        // Format time as HH:MM
        const hours = date.getHours().toString().padStart(2, '0');
        const minutes = date.getMinutes().toString().padStart(2, '0');
        
        // Format date
        const today = new Date();
        const yesterday = new Date(today);
        yesterday.setDate(yesterday.getDate() - 1);
        
        let dateString;
        
        if (date.toDateString() === today.toDateString()) {
            dateString = 'Today';
        } else if (date.toDateString() === yesterday.toDateString()) {
            dateString = 'Yesterday';
        } else {
            // Format as MM/DD/YYYY for older dates
            const month = (date.getMonth() + 1).toString().padStart(2, '0');
            const day = date.getDate().toString().padStart(2, '0');
            const year = date.getFullYear();
            dateString = `${month}/${day}/${year}`;
        }
        
        return `${dateString} ${hours}:${minutes}`;
    }
    
    // Fetch history data when page loads
    fetchHistoryData();
    
    // Toggle history panel when clicking the toggle button
    historyToggle.addEventListener('click', function() {
        historyPanel.classList.toggle('collapsed');
        refreshEditors(); // Refresh editors when panel state changes
    });

    const commonOptions = {
        mode: 'python',
        theme: 'shadowfox',  // ShadowFox theme
        lineNumbers: true,
        lineWrapping: false,  // Disable line wrapping
        scrollbarStyle: 'simple',  // Use the simple scrollbar style
        indentUnit: 4,
        tabSize: 4,
        viewportMargin: Infinity,
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
            const response = await fetch('/api/v1/instructions', {
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
            
            // Fetch updated history after successful processing
            await fetchHistoryData();
            
            // Refresh model data in case it changed
            await fetchModelData();
            
            // Clear any active history entry selections
            document.querySelectorAll('.history-entry').forEach(entry => {
                entry.classList.remove('active');
            });
        } catch (error) {
            console.error('Error:', error);
            // Display error in the output area
            outputCodeEditor.setValue(`Error: ${error.message || 'Failed to process request'}`);
            markdownOutput.innerHTML = marked.parse(`Error: ${error.message || 'Failed to process request'}`);
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