import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import Dashboard from './pages/Dashboard'
import Calculate from './pages/Calculate'
import Results from './pages/Results'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/calculate" element={<Calculate />} />
        <Route path="/results/:id" element={<Results />} />
      </Routes>
    </BrowserRouter>
  )
}
