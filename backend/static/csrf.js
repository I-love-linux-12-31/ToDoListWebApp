/**
 * CSRF Protection script for ToDo List Web App
 * Adds CSRF tokens to all forms and AJAX requests
 */
document.addEventListener('DOMContentLoaded', function() {
    // Get the CSRF token from the meta tag
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    
    // Add CSRF token to all AJAX requests using fetch
    const originalFetch = window.fetch;
    window.fetch = function(url, options) {
        options = options || {};
        options.headers = options.headers || {};
        
        // Only add the CSRF token to same-origin requests
        const sameOrigin = url.startsWith('/') || url.startsWith(window.location.origin);
        if (sameOrigin && !options.headers['X-CSRFToken']) {
            options.headers['X-CSRFToken'] = csrfToken;
        }
        
        return originalFetch(url, options);
    };
    
    // Add CSRF token to all AJAX requests using XMLHttpRequest
    const originalXhrOpen = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function() {
        const xhrInstance = this;
        originalXhrOpen.apply(this, arguments);
        
        const method = arguments[0].toUpperCase();
        if (method !== 'GET' && method !== 'HEAD') {
            xhrInstance.setRequestHeader('X-CSRFToken', csrfToken);
        }
    };
    
    // Add CSRF token to all forms on the page
    const addTokenToForm = function(form) {
        if (!form.querySelector('input[name="csrf_token"]')) {
            const csrfInput = document.createElement('input');
            csrfInput.type = 'hidden';
            csrfInput.name = 'csrf_token';
            csrfInput.value = csrfToken;
            form.appendChild(csrfInput);
        }
    };
    
    // Add to existing forms
    document.querySelectorAll('form').forEach(addTokenToForm);
    
    // Monitor for dynamically added forms using MutationObserver
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            mutation.addedNodes.forEach(function(node) {
                if (node.nodeName === 'FORM') {
                    addTokenToForm(node);
                } else if (node.querySelectorAll) {
                    node.querySelectorAll('form').forEach(addTokenToForm);
                }
            });
        });
    });
    
    observer.observe(document.body, { childList: true, subtree: true });
});
