import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../api/axios';

function Dashboard() {
  const [user, setUser] = useState(null);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          navigate('/login');
          return;
        }
        const response = await api.get('/dashboard');
        const dashboardData = response.data;
        if (!dashboardData.email || !dashboardData.role) {
          setError('Invalid user data received');
          return;
        }
        setUser(dashboardData);
      } catch (err) {
        setError('Failed to load dashboard: ' + (err.response?.data?.message || err.message));
        navigate('/login');
      }
    };
    fetchDashboard();
  }, [navigate]);

  return (
    <div className="max-w-4xl mx-auto mt-10 bg-white p-8 rounded-lg shadow-lg">
      <h2 className="text-3xl font-bold mb-6 text-center">Dashboard</h2>
      {error && <p className="text-red-500 mb-4 text-center">{error}</p>}
      {user ? (
        <div className="text-center">
          <p className="text-xl mb-2">Email: {user.email}</p>
          <p className="text-lg mb-6">
            Role: <span className="font-semibold">{user.role}</span>
          </p>
          {user.role === 'admin' ? (
            <div>
              <h3 className="text-2xl font-semibold mb-4">Admin Access</h3>
              <p className="mb-4">You can upload 2D blueprints to convert to 3D models.</p>
              <Link
                to="/upload-blueprint"
                className="inline-block bg-blue-600 text-white p-3 rounded-lg hover:bg-blue-700"
              >
                Upload 2D Blueprint
              </Link>
            </div>
          ) : (
            <div>
              <h3 className="text-2xl font-semibold mb-4">Core User Access</h3>
              <p className="mb-4">
                As a core user, you cannot update, edit, or delete 2D blueprints. To gain admin access for
                uploading blueprints, please{' '}
                <Link to="/update-profile" className="text-blue-600 hover:underline">
                  update your profile
                </Link>
                .
              </p>
            </div>
          )}
        </div>
      ) : (
        <p className="text-center">Loading...</p>
      )}
    </div>
  );
}

export default Dashboard;