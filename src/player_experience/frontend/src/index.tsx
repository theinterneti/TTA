import React from 'react';
import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import './index.css';
import App from './App';
import { store } from './store/store';
import reportWebVitals from './reportWebVitals';
import { initializeSecureStorage } from './utils/secureStorage';
import { initializeSessionRestoration } from './utils/sessionRestoration';
import ErrorBoundary from './components/ErrorBoundary';
import { NotificationProvider } from './components/Notifications';

// Initialize secure storage and migrate from localStorage if needed
initializeSecureStorage();

// Initialize session restoration
initializeSessionRestoration();

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <ErrorBoundary>
      <Provider store={store}>
        <NotificationProvider>
          <BrowserRouter>
            <App />
          </BrowserRouter>
        </NotificationProvider>
      </Provider>
    </ErrorBoundary>
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
