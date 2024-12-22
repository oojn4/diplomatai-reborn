import React, {  useState } from "react";

const Modal = ({message}) =>{
    const [isOpen,setIsOpen] = useState(true);
    // useEffect(()=>{
        if (isOpen === true){
            setInterval(() => {
                setIsOpen(false)
            }, 2000);
        }

    // })
    return (
        <div className="z-50">
        {
            isOpen &&(
                <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
                <div className="bg-white p-6 rounded-lg shadow-lg">
                  <h2 className="text-lg font-semibold">{message}</h2>
                  
                </div>
              </div>
        )}
        </div>
    )
}

export default Modal