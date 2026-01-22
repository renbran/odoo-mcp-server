/** @odoo-module */
/**
 * Global DOM Protection for Odoo 17 v4.0
 *
 * Runs early to guard querySelector recursion loops. This remains an IIFE so it
 * executes on load, but now depends on the module loader being present (keep it
 * ordered after the loader in assets).
 */

(function () {
    'use strict';

    // Skip if cloudpepper protection already initialized (it has the same fix)
    if (window.__cloudpepper_protection_v3__) {
        console.log('[rental_management] CloudPepper v3 protection already active, skipping...');
        return;
    }
    
    // Skip if already initialized (prevent double-loading)
    if (window.__rental_dom_protection_v3__) {
        console.log('[rental_management] DOM protection v3 already initialized, skipping...');
        return;
    }
    window.__rental_dom_protection_v3__ = true;

    console.log('[rental_management] Loading global DOM protection v3.0...');

    // ========================================================================
    // CRITICAL: GET TRUE NATIVE QUERYSELECTOR (before Odoo wraps it)
    // ========================================================================
    
    let NATIVE_DOC_QS, NATIVE_DOC_QSA, NATIVE_EL_QS, NATIVE_EL_QSA;
    
    try {
        // Create a hidden iframe to get pristine native methods
        const iframe = document.createElement('iframe');
        iframe.style.display = 'none';
        document.head.appendChild(iframe);
        
        // Get truly native methods from iframe's document
        NATIVE_DOC_QS = iframe.contentDocument.constructor.prototype.querySelector;
        NATIVE_DOC_QSA = iframe.contentDocument.constructor.prototype.querySelectorAll;
        NATIVE_EL_QS = iframe.contentWindow.Element.prototype.querySelector;
        NATIVE_EL_QSA = iframe.contentWindow.Element.prototype.querySelectorAll;
        
        // Clean up iframe
        document.head.removeChild(iframe);
        
        console.log('[rental_management] Got native querySelector from iframe');
    } catch (e) {
        // Fallback: Store current methods (may already be wrapped)
        console.warn('[rental_management] Could not get native from iframe, using fallback');
        NATIVE_DOC_QS = Document.prototype.querySelector;
        NATIVE_DOC_QSA = Document.prototype.querySelectorAll;
        NATIVE_EL_QS = Element.prototype.querySelector;
        NATIVE_EL_QSA = Element.prototype.querySelectorAll;
    }

    // ========================================================================
    // RECURSION PROTECTION WITH FLAG-BASED DETECTION
    // ========================================================================
    
    // Use a flag instead of counter for more reliable detection
    let isInQuerySelector = false;
    
    Document.prototype.querySelector = function(selector) {
        // If we're already in a querySelector call, return null to break the cycle
        if (isInQuerySelector) {
            return null;
        }
        
        isInQuerySelector = true;
        try {
            if (!selector || typeof selector !== 'string') {
                return null;
            }
            return NATIVE_DOC_QS.call(this, selector);
        } catch (e) {
            if (e.message?.includes('call stack') || e.message?.includes('Maximum')) {
                console.warn('[rental_management] Stack overflow caught in querySelector');
                return null;
            }
            throw e;
        } finally {
            isInQuerySelector = false;
        }
    };
    
    Document.prototype.querySelectorAll = function(selector) {
        if (isInQuerySelector) {
            return document.createDocumentFragment().querySelectorAll('*'); // Empty NodeList
        }
        
        isInQuerySelector = true;
        try {
            if (!selector || typeof selector !== 'string') {
                return [];
            }
            return NATIVE_DOC_QSA.call(this, selector);
        } catch (e) {
            if (e.message?.includes('call stack') || e.message?.includes('Maximum')) {
                return document.createDocumentFragment().querySelectorAll('*');
            }
            throw e;
        } finally {
            isInQuerySelector = false;
        }
    };
    
    // Element querySelector protection
    let isInElementQS = false;
    
    Element.prototype.querySelector = function(selector) {
        if (isInElementQS) return null;
        
        isInElementQS = true;
        try {
            if (!this || this.nodeType !== Node.ELEMENT_NODE) {
                return null;
            }
            return NATIVE_EL_QS.call(this, selector);
        } catch (e) {
            if (e.message?.includes('call stack')) return null;
            throw e;
        } finally {
            isInElementQS = false;
        }
    };
    
    Element.prototype.querySelectorAll = function(selector) {
        if (isInElementQS) return [];
        
        isInElementQS = true;
        try {
            if (!this || this.nodeType !== Node.ELEMENT_NODE) {
                return [];
            }
            return NATIVE_EL_QSA.call(this, selector);
        } catch (e) {
            if (e.message?.includes('call stack')) return [];
            throw e;
        } finally {
            isInElementQS = false;
        }
    };
    
    console.log('[rental_management] querySelector recursion protection active');

    // ========================================================================
    // 3. GLOBAL ERROR HANDLERS
    // ========================================================================

    /**
     * Global error handler for uncaught errors - prevent UI crashes
     */
    window.addEventListener('error', function(event) {
        if (event.error && event.error.message) {
            const message = event.error.message;
            
            // Catch recursion/stack overflow errors
            if (message.includes('Maximum call stack') ||
                message.includes('call stack size exceeded') ||
                message.includes('isEditorContext')) {
                
                console.warn('[rental_management] Caught recursion/stack error:', event.error);
                event.preventDefault();
                return false;
            }
            
            // Catch querySelector errors
            if (message.includes("Cannot read properties of null (reading 'querySelector')") ||
                message.includes("Cannot read property 'querySelector' of null")) {
                
                console.warn('[rental_management] Caught querySelector error:', event.error);
                event.preventDefault();
                return false;
            }
        }
    }, true);

    // Also catch unhandled promise rejections
    window.addEventListener('unhandledrejection', function(event) {
        if (event.reason && event.reason.message) {
            const message = event.reason.message;
            
            if (message.includes('Maximum call stack') ||
                message.includes('call stack size exceeded')) {
                
                console.warn('[rental_management] Caught async recursion error:', event.reason);
                event.preventDefault();
                return false;
            }
        }
    }, true);

    // ========================================================================
    // 4. PROTECT AGAINST NULL PARENT ELEMENTS
    // ========================================================================

    /**
     * Add null safety to common DOM operations
     */
    const originalAppendChild = Element.prototype.appendChild;
    const originalRemoveChild = Element.prototype.removeChild;
    const originalInsertBefore = Element.prototype.insertBefore;

    Element.prototype.appendChild = function(child) {
        try {
            if (!this || !child) {
                console.warn('[rental_management] appendChild: Invalid parent or child');
                return child;
            }
            return originalAppendChild.call(this, child);
        } catch (error) {
            console.error('[rental_management] appendChild error:', error);
            return child;
        }
    };

    Element.prototype.removeChild = function(child) {
        try {
            if (!this || !child) {
                console.warn('[rental_management] removeChild: Invalid parent or child');
                return child;
            }
            return originalRemoveChild.call(this, child);
        } catch (error) {
            console.error('[rental_management] removeChild error:', error);
            return child;
        }
    };

    Element.prototype.insertBefore = function(newNode, referenceNode) {
        try {
            if (!this || !newNode) {
                console.warn('[rental_management] insertBefore: Invalid parent or node');
                return newNode;
            }
            return originalInsertBefore.call(this, newNode, referenceNode);
        } catch (error) {
            console.error('[rental_management] insertBefore error:', error);
            return newNode;
        }
    };

    // ========================================================================
    // 5. PROTECT OWL COMPONENT REFERENCES
    // ========================================================================

    /**
     * Add safe access helper for OWL refs
     */
    window.__rental_safe_ref_access__ = function(ref, defaultValue = null) {
        try {
            if (!ref) return defaultValue;
            if (!ref.el) return defaultValue;
            return ref.el;
        } catch (error) {
            console.error('[rental_management] Safe ref access error:', error);
            return defaultValue;
        }
    };

    // ========================================================================
    // 6. MONITOR CONSOLE FOR SPECIFIC ERRORS
    // ========================================================================

    /**
     * Enhanced error logging for debugging
     */
    const originalConsoleError = console.error;
    console.error = function(...args) {
        // Check for querySelector errors
        const errorString = args.join(' ');
        if (errorString.includes('querySelector') || 
            errorString.includes('ListRenderer') ||
            errorString.includes('Cannot read properties of null')) {
            
            // Add stack trace for debugging
            console.warn('[rental_management] Intercepted error:', ...args);
            console.trace('[rental_management] Error trace:');
        }
        
        // Call original console.error
        originalConsoleError.apply(console, args);
    };

    // ========================================================================
    // 7. SAFE DOM READY HELPER
    // ========================================================================

    /**
     * Ensure DOM is ready before executing code
     */
    window.__rental_dom_ready__ = function(callback) {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', callback);
        } else {
            callback();
        }
    };

    // ========================================================================
    // 8. DEBOUNCE HELPER FOR EVENT HANDLERS
    // ========================================================================

    /**
     * Debounce function to prevent rapid event firing
     */
    window.__rental_debounce__ = function(func, wait = 100) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    };

    // ========================================================================
    // INITIALIZATION COMPLETE
    // ========================================================================

    console.log('[rental_management] Global DOM protection loaded successfully');
    console.log('[rental_management] Protected methods: querySelector, appendChild, removeChild, insertBefore');
    console.log('[rental_management] Helper functions: __rental_safe_ref_access__, __rental_dom_ready__, __rental_debounce__');

})();
