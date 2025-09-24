import React, { useContext, useState } from "react";
import axios from "axios";
import { AuthContext } from "../context/AuthContext"; // ✅ this works now


const Settings = () => {
  const { user, token, login } = useContext(AuthContext);
  const [name, setName] = useState(user?.name || "");
  const [email, setEmail] = useState(user?.email || "");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  const handleUpdate = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.put(
        `http://localhost:8000/api/users/${user._id}`,
        { name, email, password },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // update context + localStorage
      login(res.data.updatedUser, token);
      setMessage("✅ Profile updated successfully!");
    } catch (err) {
      setMessage("❌ Update failed. Try again.");
      console.error(err);
    }
  };

  return (
    <div className="max-w-md mx-auto mt-10 bg-white p-6 rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">Settings</h2>

      <form onSubmit={handleUpdate} className="flex flex-col gap-4">
        <div>
          <label className="block text-gray-600">Name</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="border w-full px-3 py-2 rounded mt-1"
          />
        </div>

        <div>
          <label className="block text-gray-600">Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="border w-full px-3 py-2 rounded mt-1"
          />
        </div>

        <div>
          <label className="block text-gray-600">Password</label>
          <input
            type="password"
            placeholder="Leave blank to keep current"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="border w-full px-3 py-2 rounded mt-1"
          />
        </div>

        <button
          type="submit"
          className="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700 transition"
        >
          Update Profile
        </button>
      </form>

      {message && <p className="mt-4 text-center text-gray-700">{message}</p>}
    </div>
  );
};

export default Settings;
