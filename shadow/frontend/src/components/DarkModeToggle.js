import React from 'react';
import { useTheme } from '../contexts/ThemeContext';
import './DarkModeToggle.css';

/**
 * Dark mode toggle component with sun/moon icons
 * Provides a smooth toggle animation and visual feedback
 */
const DarkModeToggle = () => {
  const { isDarkMode, toggleDarkMode } = useTheme();

  return (
    <button
      className={`dark-mode-toggle ${isDarkMode ? 'dark' : 'light'}`}
      onClick={toggleDarkMode}
      aria-label={`Switch to ${isDarkMode ? 'light' : 'dark'} mode`}
      title={`Switch to ${isDarkMode ? 'light' : 'dark'} mode`}
    >
      <div className="toggle-track">
        <div className="toggle-thumb">
          {isDarkMode ? (
            <svg className="icon moon" viewBox="0 0 24 24" fill="currentColor">
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
            </svg>
          ) : (
            <svg className="icon sun" viewBox="0 0 24 24" fill="currentColor">
              <circle cx="12" cy="12" r="5"/>
              <path d="m12 1-1.5 1.5L12 4l1.5-1.5L12 1zM21 11h-3l1.5 1.5L21 11zM12 20l-1.5 1.5L12 23l1.5-1.5L12 20zM4.22 10.22 1.93 7.93l1.41-1.41 2.29 2.29-1.41 1.41zM18.36 16.95l-1.41-1.41 2.29-2.29 1.41 1.41-2.29 2.29zM5.64 7.05l1.41 1.41L4.76 10.75l-1.41-1.41L5.64 7.05zM19.07 16.07l-2.29-2.29 1.41-1.41 2.29 2.29-1.41 1.41z"/>
            </svg>
          )}
        </div>
      </div>
    </button>
  );
};

export default DarkModeToggle;
