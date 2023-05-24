import './App.css';
import Navbar from './components/Navbar';
import HeroSection from './components/HeroSection';
import DeckOptimizer from './components/DeckOptimizer';
import Footer from './components/Footer';

function App() {
  return (
    <div className="App">
      <Navbar />
      <HeroSection />
      <DeckOptimizer />
      <Footer />
    </div>
  );
}

export default App;
