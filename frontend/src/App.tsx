import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import Dashboard from './pages/Dashboard'
import Calculate from './pages/Calculate'
import Results from './pages/Results'
import About from './pages/About'
import EspnLogin from './pages/EspnLogin'
import Nav from './components/Nav'

export default function App() {
  return (
    <BrowserRouter>
      <Nav />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/espn-login" element={<EspnLogin />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/calculate" element={<Calculate />} />
        <Route path="/results/:id" element={<Results />} />
        <Route path="/about" element={<About />} />
      </Routes>
    </BrowserRouter>
  )
}
