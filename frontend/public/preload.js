// This script runs before any modules are loaded

// React Router Future Flags
window.__reactRouterFutureFlags = {
  v7_startTransition: true,
  v7_relativeSplatPath: true
};

// Custom Element Definitions
if (typeof window.customElements !== 'undefined') {
  // Store original define method
  const originalDefine = window.customElements.define;
  
  // Create a safer version that prevents errors with specific elements
  window.customElements.define = function(name, constructor, options) {
    // Skip registration for problematic elements
    if (name === 'autosize-textarea' || name.includes('chakra-autosize')) {
      console.log('Blocked registration of', name);
      return;
    }
    
    // For other elements, first check if already registered
    try {
      return originalDefine.call(this, name, constructor, options);
    } catch (error) {
      console.log('Element already registered:', name);
    }
  };
  
  // Pre-register problematic elements
  class DummyElement extends HTMLElement {}
  try {
    originalDefine.call(window.customElements, 'autosize-textarea', DummyElement);
    console.log('Pre-registered: autosize-textarea');
  } catch (e) {
    console.log('Note: autosize-textarea registration error (expected)');
  }
}

// Mock APIs for development
window.MOCK_HEALTH_CHECK = {
  status: 'healthy',
  service: 'mnemosyne-api',
  version: 'dev',
  environment: 'development'
};
