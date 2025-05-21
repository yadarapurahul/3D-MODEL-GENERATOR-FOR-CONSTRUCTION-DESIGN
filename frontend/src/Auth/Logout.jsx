import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

function Logout() {
  const navigate = useNavigate();

  useEffect(() => {
    const logout = async () => {
      try {
        const token = localStorage.getItem('token');
        if (token) {
          await axios.post('http://localhost:5000/api/logout', {}, {
            headers: { Authorization: `Bearer ${token}` },
          });
        }
        localStorage.removeItem('token');
        navigate('/');
      } catch (err) {
        console.error('Logout failed:', err);
        localStorage.removeItem('token');
        navigate('/');
      }
    };
    logout();
  }, [navigate]);

  return (
    <div className="max-w-md mx-auto mt-10 bg-white p-8 rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold mb-6 text-center">Logging Out...</h2>
      <p className="text-center">You are being redirected to the Home page.</p>
    </div>
  );
}

export default Logout;