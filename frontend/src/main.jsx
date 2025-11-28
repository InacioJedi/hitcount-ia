import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'

// importa nosso fallback e (se quiser) mantenha o index.css
import './index.css'
import './fix.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
