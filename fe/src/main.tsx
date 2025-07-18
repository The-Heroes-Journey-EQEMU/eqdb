//import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './styles/base.css'
import './styles/globals.css'

// Apply dark theme by default
document.documentElement.classList.add('dark')

ReactDOM.createRoot(document.getElementById('root')!).render(
  <App />
)
