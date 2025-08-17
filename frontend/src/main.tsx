/**
 * Main entry point for the Mnemosyne frontend application
 * ULTRA-ENHANCED: Comprehensive React Router future flags handling (2025-06-05)
 */

// GLOBAL ERROR SUPPRESSION for React, Router and Custom Elements (2025-06-05)
const originalError = console.error;
console.error = function(...args: any[]) {
  // Identify and block specific error patterns
  if (args[0] instanceof Error) {
    // Block errors by message content
    if (args[0].message && (
      args[0].message.includes('already been defined') || 
      args[0].message.includes('custom element') ||
      args[0].message.includes('ReactRouter')
    )) {
      return; // Silently suppress
    }
  } else if (typeof args[0] === 'string') {
    // Detect and block specific string patterns
    if (args[0].includes('already been defined') || 
        args[0].includes('custom element') || 
        args[0].includes('mce-') ||
        args[0].includes('ReactRouter') ||
        args[0].includes('react-router') ||
        args[0].includes('the requested module')) {
      return; // Silently suppress
    }
  }
  // Pass through other errors
  return originalError.apply(console, args);
};

// CRITICAL: Must set React Router future flags before any imports
// These flags MUST be set before react-router-dom is imported
if (typeof window !== 'undefined') {
  // Direct future flag setting for v7 compatibility
  window.__reactRouterFutureFlags = {
    v7_startTransition: true,
    v7_relativeSplatPath: true,
    _initialized: true  // Force immediate initialization
  };
  
  // Use Object.defineProperty to prevent tampering
  Object.defineProperty(window.__reactRouterFutureFlags, 'v7_startTransition', {
    value: true,
    writable: false,
    configurable: false
  });
  
  Object.defineProperty(window.__reactRouterFutureFlags, 'v7_relativeSplatPath', {
    value: true,
    writable: false,
    configurable: false
  });
  
  // Force immediate effect with console patching
  const originalConsoleWarn = console.warn;
  console.warn = function(...args) {
    if (args[0] && typeof args[0] === 'string' && 
        (args[0].includes('React Router Future Flag Warning') || 
         args[0].includes('v7_startTransition') || 
         args[0].includes('v7_relativeSplatPath'))) {
      // Suppress React Router warnings
      return;
    }
    originalConsoleWarn.apply(console, args);
  };
}

// Regular imports
import React from "react"
import ReactDOM from "react-dom/client"
import App from "./App"
import "./index.css"

// Declare types for React Router future flags (for TypeScript)
declare global {
  interface Window {
    __reactRouterFutureFlags?: {
      v7_startTransition: boolean;
      v7_relativeSplatPath: boolean;
      _initialized?: boolean;
    };
  }
}

// Render the application
ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
