import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import LoginForm from "../Components/LoginForm";
import RegisterForm from "../Components/RegisterForm";

const Home = () => {
  const access_token = localStorage.getItem("access_token");
  const navigate = useNavigate();
  if (access_token !== "") {
    navigate("/pdf");
  }
  const [isRegister, setIsRegister] = useState(false);

  const handleSignIn = () => {
    setIsRegister(false); // Mengubah state ke false saat tombol Sign In diklik
  };

  return (
    <div className="bg-login bg-cover bg-blend-multiply bg-gray-700 w-full min-h-screen flex items-center justify-center">
      {/* <div className="max-w-screen-md w-full"> */}
        {isRegister ? (
          <RegisterForm handleSignIn={handleSignIn} />
        ) : (
          <LoginForm handleSignUp={() => setIsRegister(true)} />
        )}
      {/* </div> */}
    </div>
  );
};

export default Home;
