import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

function UpdateProfile() {
  const [user, setUser] = useState(null);
  const [error, setError] = useState('');
  const [role, setRole] = useState('core');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          navigate('/login');
          return;
        }
        const response = await axios.get('http://localhost:5000/api/profile', {
          headers: { Authorization: `Bearer ${token}` },
        });
        setUser(response.data);
        setRole(response.data.role);
      } catch (err) {
        setError('Failed to load profile');
        navigate('/login');
      }
    };
    fetchProfile();
  }, [navigate]);

  const handleUpdate = async () => {
    try {
      const token = localStorage.getItem('token');
      await axios.put(
        'http://localhost:5000/api/profile',
        { role, password: password || undefined },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert('Profile updated successfully! Please log in again.');
      localStorage.removeItem('token');
      navigate('/login');
    } catch (err) {
      setError('Failed to update profile');
    }
  };

  return (
    <div className="max-w-4xl mx-auto mt-10 bg-white p-8 rounded-lg shadow-lg">
      <h2 className="text-3xl font-bold mb-6 text-center">Update Profile</h2>
      {error && <p className="text-red-500 mb-4 text-center">{error}</p>}
      {user ? (
        <div className="text-center">
          <p className="text-xl mb-4">Email: {user.email}</p>
          <div className="mb-6">
            <label className="block text-lg font-semibold mb-2">Role</label>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="mb-4 p-2 border border-gray-300 rounded-lg w-full"
            >
              <option value="core">Core</option>
              <option value="admin">Admin</option>
            </select>
            <label className="block text-lg font-semibold mb-2">New Password (optional)</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mb-4 p-2 border border-gray-300 rounded-lg w-full"
              placeholder="Enter new password"
            />
            <button
              onClick={handleUpdate}
              className="w-full bg-blue-600 text-white p-3 rounded-lg hover:bg-blue-700"
            >
              Update Profile
            </button>
          </div>
        </div>
      ) : (
        <p className="text-center">Loading...</p>
      )}
    </div>
  );
}

export default UpdateProfile;