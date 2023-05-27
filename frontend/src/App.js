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
      <h1>I'm fixing the database issue as fast as I can, hopefully it'll be less than an hour. Message me through the "Contact" tab if you want to know when it's back up</h1>
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
