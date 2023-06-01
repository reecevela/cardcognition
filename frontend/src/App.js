import './App.css';
import Navbar from './components/Navbar';
import HeroSection from './components/HeroSection';
import DeckOptimizer from './components/DeckOptimizer';
import DevDocs from './components/DevDocs';
import ContactForm from './components/ContactForm';
import BackToTopButton from './components/BackToTopButton';
import Footer from './components/Footer';
import { HashRouter, Routes, Route } from "react-router-dom";
import PageViewLogger from './components/PageViewLogger';

function App() {
  return (
    <div className="App">
      <HashRouter>
      <Navbar />
      <PageViewLogger />
        <Routes>
          <Route path="/" element={(
            <>
              <HeroSection />
              <DeckOptimizer />
            </>
          )} />
          <Route path="/commander/:name" element={<DeckOptimizer />} />
          <Route path="/docs" element={<DevDocs />} />
          <Route path="/contact" element={<ContactForm />} />
        </Routes>
      </HashRouter>
      <BackToTopButton />
      <Footer />
    </div>
  );
}

export default App;
