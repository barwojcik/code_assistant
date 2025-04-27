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

    // Ensure proper horizontal scrolling
    function refreshEditors() {
        inputCodeEditor.refresh();
        outputCodeEditor.refresh();
    }
    
    // Refresh after initialization and on window resize
    setTimeout(refreshEditors, 100);
    window.addEventListener('resize', refreshEditors);

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
    
            const data = await response.json();
            
            // Display the processed code from the backend
            outputCodeEditor.setValue(data.output);
        } catch (error) {
            console.error('Error:', error);
            // Display error in the output area
            outputCodeEditor.setValue(`Error: ${error.message || 'Failed to process request'}`);
        } finally {
            // Reset button state
            const sendButton = document.getElementById('sendButton');
            sendButton.textContent = 'Send';
            sendButton.disabled = false;
        }
    });

    // Handle Copy button click
    document.getElementById('copyButton').addEventListener('click', function() {
        const outputCode = outputCodeEditor.getValue();
        
        // Copy to clipboard
        navigator.clipboard.writeText(outputCode).then(function() {
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
        const outputCode = outputCodeEditor.getValue();
        
        // Copy to input editor
        inputCodeEditor.setValue(outputCode);
        
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
        document.getElementById('instructions').value = '';
        inputCodeEditor.setValue('');
        outputCodeEditor.setValue('');
    });
});