import React, { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import BotImage from "../assets/bot-image.webp";
import Logo from "../assets/microsoft-icon.png"; // Update this to your actual logo path

function ChatbotPage() {
  const userName = localStorage.getItem('username')?? "teman"; // Change to the logged-in user's name
  const [messages, setMessages] = useState([
    { text: `Halo, ${userName}!. Ketik mulai untuk memulai chatbot`, isUser: false },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false); // State for loading animation
  const messagesEndRef = useRef(null); // Ref to the last message element
  const navigate = useNavigate();
  
  // Function to scroll to the bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // Auto scroll when new messages are added or loading state is active
  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  useEffect(()=>{
    if(localStorage.getItem("access_token") === "" )
    {
      navigate('/')
    }

  },[navigate])
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (input.trim() === "") return;

    // Add user message to the chat
    setMessages([...messages, { text: input, isUser: true }]);
    setInput("");
    // Set loading state to true
    setLoading(true);

    // Call the API and wait for the response
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_API}/chatbot`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${localStorage.getItem("access_token")}`
        },
        body: JSON.stringify({ message: input }),
      });
      const data = await response.json();
      if (response.status !== 200)
      {
        localStorage.setItem("access_token","")
        navigate('/')
      }
      // Replace occurrences of **text** with <strong>text</strong>
      const formattedText = data.data.replace(
        /\*\*(.*?)\*\*/g,
        "<strong>$1</strong>"
      );

      // Add the formatted API response to the chat
      setMessages((prevMessages) => [
        ...prevMessages,
        { text: formattedText, isUser: false },
      ]);
    } catch (error) {
      console.error("Error fetching API:", error);
      setMessages((prevMessages) => [
        ...prevMessages,
        {
          text: "Something went wrong, please try again later.",
          isUser: false,
        },
      ]);
    }

    // Set loading state to false
    setLoading(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleLogout = ()=>{
    localStorage.setItem("access_token","");
    navigate("/");
  }

  return (
    <div className="flex flex-col w-full h-screen">
      {/* Navbar */}
      <div className="bg-violet-900">
        <div className="flex items-center m-auto w-full max-w-screen-2xl justify-between px-4 lg:px-16 py-4 text-white">
          <div className="flex items-center space-x-4">
            <img src={Logo} alt="Logo" className="w-32" />
            <span className="text-xl font-semibold"></span>
          </div>
          
          <div className="flex items-center space-x-4">
            <button onClick={()=>navigate('/webchat')}>
                DiplomatAI Chatbot
            </button>
          </div>
          <div className="flex items-center space-x-4">
            <button onClick={()=>navigate('/pdf')}>
                Market Intelligence Report Generator
            </button>
          </div>
          <div className="flex items-center space-x-4">
            <button onClick={()=>handleLogout()}>
              <i className="fa-solid fa-right-from-bracket"></i>
            </button>
          </div>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-grow py-8 px-4 lg:px-16 max-w-screen-2xl bg-gray-50 w-full m-auto overflow-y-auto">
        <div className="space-y-6">
          
          {messages.map((message, index) => (
            <div key={index} className={`space-y-2 ${message.isUser ? "justify-end" : "justify-start"}`}>
              <div className={`flex ${message.isUser ? "justify-end" : "justify-start"}`}>
                {!message.isUser && (
                  <div className="flex-shrink-0">
                    <img src={BotImage} alt="Logo" className="w-10 h-10 rounded-full" />
                  </div>
                )}
                <div className={`flex items-center ${message.isUser ? "ml-auto" : "ml-3"} text-sm text-gray-700 font-semibold`}>
                  {message.isUser ? "You" : "DiplomatAI"}
                </div>
              </div>
              
              <div className={`flex ${message.isUser ? "justify-end" : "justify-start"}`}>
                <div
                  className={`max-w-full shadow-lg rounded-md px-4 py-3 ${message.isUser ? "bg-white text-gray-700": "bg-gray-200 text-gray-700"}`}>
                  {/* Render the message using dangerouslySetInnerHTML */}
                  <pre
                    className="font-sans whitespace-pre-wrap break-words rounded-lg max-w-screen-sm"
                    dangerouslySetInnerHTML={{ __html: message.text }}
                  />
                </div>
              </div>
            </div>
          ))}

          {/* Loading animation while waiting for response */}
          {loading && (
            <div className="flex justify-start">
              <div className="max-w-xs rounded-lg p-2 text-gray-500">
                <div className="animate-pulse">Typing...</div>
              </div>
            </div>
          )}

          {/* Reference for the last message to scroll to */}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <form
        onSubmit={handleSubmit}
        className="p-4 px-4 lg:px-16 max-w-screen-2xl w-full m-auto bg-violet-900 shadow-lg"
      >
        <div className="flex items-center text-black bg-white rounded-full shadow-lg">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            className="flex-grow bg-transparent px-6 focus:outline-none resize-none"
            placeholder="Type your message..."
            disabled={loading}
            rows={1}
          />
          <button
            type="submit"
            className="m-1 py-2 px-3 rounded-full bg-violet-800"
            disabled={loading}
          >
            <i className="fa-regular fa-paper-plane text-white text-xl"></i>
          </button>
        </div>
      </form>
    </div>
  );
}

export default ChatbotPage;
