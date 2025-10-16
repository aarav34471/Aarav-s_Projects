import 'bootstrap/dist/css/bootstrap.min.css';
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import {QueryClientProvider, QueryClient} from "@tanstack/react-query"
import { BrowserRouter as Router } from 'react-router-dom';
import "./index.css";
import { AuthProvider } from './context/AuthContext';


const root = ReactDOM.createRoot(document.getElementById('root'));
const queryClient = new QueryClient();
root.render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <Router>
        <AuthProvider>
          <App />
        </AuthProvider> 
      </Router>
    </QueryClientProvider>
  </React.StrictMode>
);

