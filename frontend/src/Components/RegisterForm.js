import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

function RegisterForm({ handleSignIn }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate(); // To navigate to "/webchat"

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_API}/signup`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username: username, password: password }),
      });

      const data = await response.json();

      if (response.ok) {
        // Save access_token and username to localStorage
        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("username", username);

        // Navigate to "/webchat"
        navigate("/pdf");
      } else {
        alert(data.error || "Something went wrong, please try again.");
      }
    } catch (error) {
      console.error("Error fetching API:", error);
      alert("Something went wrong, please try again later.");
    }
  };

  return (
    <form className="w-full max-w-md bg-gray-900 text-white backdrop-blur-sm bg-opacity-70 py-12 px-8 rounded-lg shadow-lg">
      <div className="mb-6 text-left space-y-1">
        <h2 className="text-xl font-semibold">
          Welcome, <label className="font-normal">Please Sign Up!</label>
        </h2>
        <p className="text-xs">Create account to try the ChatBot</p>
      </div>
      <input
        type="text"
        placeholder="Username"
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
        Sign Up
      </button>
      <p className="text-center text-sm text-gray-500 mt-4">
        Already have an account?{" "}
        <button onClick={handleSignIn} className="text-purple-500">
          Sign In
        </button>
      </p>
    </form>
  );
}

export default RegisterForm;
