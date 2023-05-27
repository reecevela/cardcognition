import './App.css';
import Navbar from './components/Navbar';
import HeroSection from './components/HeroSection';
import DeckOptimizer from './components/DeckOptimizer';
import DevDocs from './components/DevDocs';
import ContactForm from './components/ContactForm';
import Footer from './components/Footer';
import { BrowserRouter, Routes, Route } from "react-router-dom";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
      <Navbar />
        <Routes>
          <Route path="/" element={(
            <>
              <HeroSection />
              <DeckOptimizer />
            </>
          )} />
          <Route path="/docs" element={<DevDocs />} />
          <Route path="/contact" element={<ContactForm />} />
        </Routes>
      </BrowserRouter>
      <Footer />
    </div>
  );
}

export default App;
