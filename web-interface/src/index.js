import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import reportWebVitals from './reportWebVitals';

import {
    BrowserRouter,
    Routes,
    Route,
} from 'react-router-dom';

import Navigation from './components/Navbar';
import UploadView from './components/UploadView';
import JobView from './components/JobView';

import 'bootstrap/dist/css/bootstrap.min.css';

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
    <React.StrictMode>
        <BrowserRouter>
            <Navigation />
            <Routes>
                <Route path="/" element={<UploadView />} />
                <Route path="/jobs" element={<JobView />} />
            </Routes>
        </BrowserRouter>
    </React.StrictMode>,
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
