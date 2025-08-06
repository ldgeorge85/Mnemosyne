import React from 'react';
import ReactDOM from 'react-dom/client';
import './styles/App.css';
import App from './App';

/**
 * Entry point for the Shadow AI React frontend.
 * 
 * This file initializes the React application and renders it to the DOM.
 */

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
