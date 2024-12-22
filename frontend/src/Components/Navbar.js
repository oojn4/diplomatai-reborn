import React from "react";
import MicrosoftLogo from "../assets/microsoft-icon.png";

const Navbar = () => {
    return (
        <div className="w-full ">
        <div className="flex top-10 max-w-screen-2xl mx-auto  items-center py-4 justify-between px-4 lg:px-16">
          <div>
            <img src={MicrosoftLogo} className="w-32" alt="Logo Microsoft"/>
          </div>
          <div>
            <ul className="flex space-x-4 text-md">
              <li className="text-white border-b-2 border-transparent hover:border-b-2 hover:border-white ease-in-out duration-300">
                <a href="/">Home</a>
              </li>

              <li className="text-white border-b-2 border-transparent hover:border-b-2 hover:border-white ease-in-out duration-300">
                <a href="/">Instruction</a>
              </li>

              <li className="text-white border-b-2 border-transparent hover:border-b-2 hover:border-white ease-in-out duration-300">
                <a href="/">About</a>
              </li>
            </ul>
          </div>
        </div>
      
      </div>
    );
}

export default Navbar;