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
    document.getElementById('sendButton').addEventListener('click', function() {
        const instructions = document.getElementById('instructions').value;
        const code = inputCodeEditor.getValue();

        // Here you would typically send the data to your backend
        // For now, we'll just display the input code in the output area
        outputCodeEditor.setValue(code);
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
    
    // Handle Reset button click
    document.getElementById('resetButton').addEventListener('click', function() {
        document.getElementById('instructions').value = '';
        inputCodeEditor.setValue('');
        outputCodeEditor.setValue('');
    });
});