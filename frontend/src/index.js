import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import { initializeApp } from 'firebase/app';
import { getAnalytics } from 'firebase/analytics';
import App from './App';

const firebaseConfig = {
  apiKey: "AIzaSyBJfRXbbwrC8ySG6MMEXoG4F9smCRr8Wzw",
  authDomain: "card-cognition.firebaseapp.com",
  projectId: "card-cognition",
  storageBucket: "card-cognition.appspot.com",
  messagingSenderId: "14506829433",
  appId: "1:14506829433:web:6415d4363e457d066dd6a8",
  measurementId: "G-XHCXZNPREM"
};

const app = initializeApp(firebaseConfig);
export const analytics = getAnalytics(app);

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

