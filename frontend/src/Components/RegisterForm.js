import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

function RegisterForm({ handleSignIn }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("umkm");
  const [additionalInfo, setAdditionalInfo] = useState({});
  const [provinces, setProvinces] = useState([]);
  const [cities, setCities] = useState([]);
  const [districts, setDistricts] = useState([]);
  const [villages, setVillages] = useState([]);
  const [selectedProvince, setSelectedProvince] = useState("");
  const [selectedCity, setSelectedCity] = useState("");
  const [selectedDistrict, setSelectedDistrict] = useState("");
  const [permissions, setPermissions] = useState([
    "SIUP",
    "TDP",
    "Izin Usaha Mikro",
  ]);
  const [legalEntities, setLegalEntities] = useState([
    "PT",
    "CV",
    "Koperasi",
  ]);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchLocations = async () => {
      try {
        const response = await fetch(`${process.env.REACT_APP_BACKEND_API}/locations`);
        const data = await response.json();
        setProvinces(data);
      } catch (error) {
        console.error("Error fetching locations:", error);
      }
    };
  
    fetchLocations();
  }, []);
  
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setAdditionalInfo({ ...additionalInfo, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
  
    const payload = {
      email,
      password,
      role,
      additional_info: {},
    };
  
    if (role === "umkm") {
      payload.additional_info = {
        npwp: additionalInfo.npwp,
        business_entity_legality: additionalInfo.bentuk_badan_hukum,
        business_field_licensing: additionalInfo.perizinan,
        province: selectedProvince,
        city: selectedCity,
        district: selectedDistrict,
        village: additionalInfo.village,
      };
    } else if (role === "diplomat") {
      payload.additional_info = {
        nip: additionalInfo.nip,
      };
    }
  
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_API}/signup`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });
  
      const data = await response.json();
  
      if (response.ok) {
        // Save access_token and email to localStorage
        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("email", email);
  
        // Navigate to "/pdf"
        if (role ==="umkm"){
          navigate("/webchat");
        }else if(role ==="diplomat"){
          navigate("/pdf");
        }
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
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        className="w-full py-2 mb-6 border-b border-white bg-transparent bg-opacity-20 focus:outline-none focus:border-purple-500 transition duration-300"
      />

      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        className="w-full py-2 mb-6 border-b border-white bg-transparent bg-opacity-20 focus:outline-none focus:border-purple-500 transition duration-300"
      />

      {role === "umkm" && (
        <div>
          <input
            type="text"
            name="npwp"
            placeholder="NPWP"
            onChange={handleInputChange}
            className="w-full py-2 mb-4 border-b border-white bg-transparent bg-opacity-20 focus:outline-none focus:border-purple-500 transition duration-300"
          />

          <select
            onChange={(e) => setSelectedProvince(e.target.value)}
            className="w-full py-2 mb-4 border-b border-white bg-transparent bg-opacity-20 focus:outline-none focus:border-purple-500 transition duration-300"
          >
            <option value="">Pilih Provinsi</option>
            {provinces.map((prov) => (
              <option key={prov.id} value={prov.id} style={{ color: "black" }}>
                {prov.name}
              </option>
            ))}
          </select>

          {selectedProvince && (
            <select
              onChange={(e) => setSelectedCity(e.target.value)}
              className="w-full py-2 mb-4 border-b border-white bg-transparent bg-opacity-20 focus:outline-none focus:border-purple-500 transition duration-300"
            >
              <option value="">Pilih Kota/Kabupaten</option>
              {provinces
                .find((prov) => prov.id === selectedProvince)
                ?.cities.map((city) => (
                  <option key={city.id} value={city.id} style={{ color: "black" }}>
                    {city.name}
                  </option>
                ))}
            </select>
          )}

          {selectedCity && (
            <select
              onChange={(e) => setSelectedDistrict(e.target.value)}
              className="w-full py-2 mb-4 border-b border-white bg-transparent bg-opacity-20 focus:outline-none focus:border-purple-500 transition duration-300"
            >
              <option value="">Pilih Kecamatan</option>
              {provinces
                .find((prov) => prov.id === selectedProvince)
                ?.cities.find((city) => city.id === selectedCity)
                ?.districts.map((district) => (
                  <option key={district.id} value={district.id} style={{ color: "black" }}>
                    {district.name}
                  </option>
                ))}
            </select>
          )}

          {selectedDistrict && (
            <select
              name="village"
              onChange={(e) => setAdditionalInfo({ ...additionalInfo, village: e.target.value })}
              className="w-full py-2 mb-4 border-b border-white bg-transparent bg-opacity-20 focus:outline-none focus:border-purple-500 transition duration-300"
            >
              <option value="">Pilih Desa</option>
              {provinces
                .find((prov) => prov.id === selectedProvince)
                ?.cities.find((city) => city.id === selectedCity)
                ?.districts.find((district) => district.id === selectedDistrict)
                ?.villages.map((village) => (
                  <option key={village.id} value={village.id} style={{ color: "black" }}>
                    {village.name}
                  </option>
                ))}
            </select>
          )}


          <select
            name="perizinan"
            onChange={handleInputChange}
            className="w-full py-2 mb-4 border-b border-white bg-transparent bg-opacity-20 focus:outline-none focus:border-purple-500 transition duration-300"
          >
            <option value="">Pilih Perizinan</option>
            {permissions.map((perm, index) => (
              <option key={index} value={perm} style={{"color":"black"}}>{perm}</option>
            ))}
          </select>

          <select
            name="bentuk_badan_hukum"
            onChange={handleInputChange}
            className="w-full py-2 mb-4 border-b border-white bg-transparent bg-opacity-20 focus:outline-none focus:border-purple-500 transition duration-300"
          >
            <option value="">Pilih Bentuk Badan Hukum</option>
            {legalEntities.map((entity, index) => (
              <option key={index} value={entity}  style={{"color":"black"}}>{entity}</option>
            ))}
          </select>
        </div>
      )}

      {role === "diplomat" && (
        <input
          type="text"
          name="nip"
          placeholder="NIP"
          onChange={handleInputChange}
          className="w-full py-2 mb-4 border-b border-white bg-transparent bg-opacity-20 focus:outline-none focus:border-purple-500 transition duration-300"
        />
      )}

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
