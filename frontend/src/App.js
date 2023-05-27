import './App.css';
import Navbar from './components/Navbar';
import HeroSection from './components/HeroSection';
import DeckOptimizer from './components/DeckOptimizer';
import DevDocs from './components/DevDocs';
import ContactForm from './components/ContactForm';
import Footer from './components/Footer';
import { HashRouter, Routes, Route } from "react-router-dom";

function App() {
  return (
    <div className="App">
      <HashRouter>
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
      </HashRouter>
      <Footer />
    </div>
  );
}

export default App;
