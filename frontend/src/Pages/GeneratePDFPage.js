import { jwtDecode as jwt_decode } from 'jwt-decode';
import React, { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import Logo from "../assets/microsoft-icon.png";
import DocumentGenerator from '../Components/DocumentGenerator';

function GeneratePDFPage() {
  const userName = localStorage.getItem('username') ?? "teman";
  const [messages, setMessages] = useState([
    { text: `Halo, ${userName}!. Ketik mulai untuk memulai chatbot`, isUser: false },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const navigate = useNavigate();

  // Function to scroll to the bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // Auto scroll when new messages are added or loading state is active
  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  // Validasi token dan role
  useEffect(() => {
    const token = localStorage.getItem("access_token");

    if (!token) {
      navigate('/');
      return;
    }

    try {
      const decodedToken = jwt_decode(token);
      console.log("Decoded Token:", decodedToken); // Debugging

      if (decodedToken.sub.role !== "diplomat") {
        alert("Access denied: This page is only for diplomats.");
        navigate('/webchat'); // Arahkan ke halaman lain jika bukan diplomat
      }
    } catch (error) {
      console.error("Invalid token:", error);
      localStorage.setItem("access_token", ""); // Hapus token jika invalid
      navigate('/'); // Arahkan ke halaman login
    }
  }, [navigate]);


  const handleLogout = () => {
    localStorage.setItem("access_token", "");
    navigate("/");
  };

  return (
    <div className="flex flex-col w-full h-screen">
      <div className="bg-violet-900">
        <div className="flex items-center m-auto w-full max-w-screen-2xl justify-between px-4 lg:px-16 py-4 text-white">
          <div className="flex items-center space-x-4">
            <img src={Logo} alt="Logo" className="w-32" />
            <span className="text-xl font-semibold"></span>
          </div>
          
          <div className="flex items-center space-x-4">
            <button onClick={() => navigate('/webchat')}>
                DiplomatAI Chatbot
            </button>
          </div>
          <div className="flex items-center space-x-4">
            <button onClick={() => navigate('/pdf')}>
              Market Intelligence Report Generator
            </button>
          </div>
          <div className="flex items-center space-x-4">
            <button onClick={handleLogout}>
              <i className="fa-solid fa-right-from-bracket"></i>
            </button>
          </div>
        </div>
      </div>

      <div className="flex-grow py-8 px-4 lg:px-16 max-w-screen-2xl bg-gray-50 w-full m-auto overflow-y-auto">
        <div className="space-y-6">
          <DocumentGenerator />
        </div>
      </div>
    </div>
  );
}

export default GeneratePDFPage;
