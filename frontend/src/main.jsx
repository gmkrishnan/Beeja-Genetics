import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import Workbench from './design_1/Workbench'
import './index.css'

// Zero-Dependency Routing to prevent Vite resolution crashes
const path = window.location.pathname;

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <Workbench />
  </React.StrictMode>,
)
