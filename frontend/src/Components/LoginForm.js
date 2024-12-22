import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

function LoginForm({ handleSignUp }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("umkm"); // Default role is UMKM
  const access_token = localStorage.getItem("access_token") || "";
  const [messages, setMessages] = useState("");
  const navigate = useNavigate();
  console.log(access_token, messages);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_API}/signin`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ username: username, password: password, role: role }),
        }
      );
      const data = await response.json();
      if (response.status === 200) {
        // Add the API response to the chat
        alert("Login Success!");
        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("username", username);
        if (role ==="umkm"){
          navigate("/webchat");
        }else if(role ==="diplomat"){
          navigate("/pdf");
        }
          
      } else {
        alert("Login Failed");
      }
    } catch (error) {
      console.error("Error fetching API:", error);
      setMessages("Something went wrong, please try again later.");
    }
  };

  return (
    <div>
      <form className="w-full max-w-sm bg-gray-900 text-white backdrop-blur-sm bg-opacity-70 py-12 px-8 rounded-lg shadow-lg">
        <div className="mb-6 text-left space-y-1">
          <h2 className="text-xl font-semibold">
            Welcome, <label className="font-normal">Please Sign In!</label>
          </h2>
          <p className="text-xs">Sign In to try the ChatBot</p>
        </div>

        <div className="flex justify-between mb-6">
          <button
            type="button"
            className={`w-1/2 py-2 rounded-l-md ${
              role === "umkm" ? "bg-purple-800" : "bg-gray-700"
            } text-white font-semibold transition duration-300`}
            onClick={() => setRole("umkm")}
          >
            UMKM
          </button>
          <button
            type="button"
            className={`w-1/2 py-2 rounded-r-md ${
              role === "diplomat" ? "bg-purple-800" : "bg-gray-700"
            } text-white font-semibold transition duration-300`}
            onClick={() => setRole("diplomat")}
          >
            Diplomat
          </button>
        </div>

        <input
          type="text"
          placeholder="username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="w-full py-2 mb-6 border-b border-white bg-transparent bg-opacity-20 focus:outline-none focus:border-purple-500 transition duration-300"
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full py-2 mb-6 border-b border-white bg-transparent bg-opacity-20 focus:outline-none focus:border-purple-500 transition duration-300"
        />
        <button
          onClick={handleSubmit}
          className="w-full bg-purple-800 rounded-md hover:bg-purple-900 text-white p-2 font-semibold transition duration-300"
        >
          Sign In
        </button>
        <p className="text-center text-sm text-gray-500 mt-4">
          Don't have an account?{" "}
          <button onClick={handleSignUp} className="text-purple-500">
            Sign up
          </button>
        </p>
      </form>
    </div>
  );
}

export default LoginForm;
