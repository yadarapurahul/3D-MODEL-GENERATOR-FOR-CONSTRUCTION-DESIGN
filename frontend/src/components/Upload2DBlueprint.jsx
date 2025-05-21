import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

function Upload2DBlueprint() {
  const [user, setUser] = useState(null);
  const [error, setError] = useState('');
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const checkUser = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          navigate('/login');
          return;
        }
        const response = await axios.get('http://localhost:5000/api/dashboard', {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (response.data.role !== 'admin') {
          setError('Admin access required');
          navigate('/dashboard');
          return;
        }
        setUser(response.data);
      } catch (err) {
        setError('Failed to verify user');
        navigate('/login');
      }
    };
    checkUser();
  }, [navigate]);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a blueprint to upload');
      return;
    }
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('blueprint', file);
      const token = localStorage.getItem('token');
      await axios.post('http://localhost:5000/api/blueprint/upload', formData, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data',
        },
      });
      setError('');
      alert('Blueprint uploaded successfully! Conversion in progress.');
      setFile(null);
    } catch (err) {
      setError('Failed to upload blueprint');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto mt-10 bg-white p-8 rounded-lg shadow-lg">
      <h2 className="text-3xl font-bold mb-6 text-center">Upload 2D Blueprint</h2>
      {error && <p className="text-red-500 mb-4 text-center">{error}</p>}
      {user ? (
        <div className="text-center">
          <p className="text-xl mb-4">Welcome, {user.email}!</p>
          <div className="mb-6">
            <label className="block text-lg font-semibold mb-2">Upload 2D Blueprint</label>
            <input
              type="file"
              accept="image/*,.pdf"
              onChange={handleFileChange}
              className="mb-4 p-2 border border-gray-300 rounded-lg w-full"
            />
            <button
              onClick={handleUpload}
              disabled={uploading}
              className={`w-full bg-blue-600 text-white p-3 rounded-lg hover:bg-blue-700 ${
                uploading ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            >
              {uploading ? 'Uploading...' : 'Convert to 3D Model'}
            </button>
          </div>
        </div>
      ) : (
        <p className="text-center">Loading...</p>
      )}
    </div>
  );
}

export default Upload2DBlueprint;