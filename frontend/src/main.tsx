import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';
import './costs.css';
import App from './App';
import { Provider } from 'react-redux';
import { costsStore } from './store/costsStore';

ReactDOM.createRoot(document.getElementById('root')!).render(<React.StrictMode><Provider store={costsStore}><BrowserRouter><App /></BrowserRouter></Provider></React.StrictMode>);
