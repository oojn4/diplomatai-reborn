import { Route, BrowserRouter as Router, Routes } from 'react-router-dom';
import './App.css';
import Home from './Pages';
import ChatbotPage from './Pages/ChatbotPage';
import GeneratePDFPage from './Pages/GeneratePDFPage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/pdf" element={<GeneratePDFPage />} />
        <Route path="/webchat" element={<ChatbotPage />} />
        <Route path="/" element={<Home />} />
        <Route path="*" element={<h1>Not Found</h1>} />
      </Routes>
    </Router>
  );
}

export default App;
