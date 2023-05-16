import './App.css';
import Navbar from './components/Navbar';
import HeroSection from './components/HeroSection';
import DeckOptimizer from './components/DeckOptimizer';

function App() {
  return (
    <div className="App">
      <Navbar />
      <HeroSection />
      <DeckOptimizer />
    </div>
  );
}

export default App;
