/**
 * Global Type Declarations
 * 
 * This file contains global type declarations for the application
 */

// Extend the Window interface to include our custom ENV property
interface Window {
  ENV: {
    IS_IN_SHADOW_DOM: boolean;
    [key: string]: any;
  };
}
