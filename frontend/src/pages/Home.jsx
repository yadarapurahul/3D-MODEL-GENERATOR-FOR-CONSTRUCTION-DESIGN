import { Link, useNavigate } from 'react-router-dom';
import { useEffect } from 'react';
import Footer from '../components/Footer';

function Home() {
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      // Redirect to dashboard if token exists
      navigate('/dashboard');
    }
  }, [navigate]);

  return (
    <div className="min-h-screen flex flex-col bg-cover bg-center bg-no-repeat" 
         style={{ backgroundImage: "url('./image2.1.jpg')" }}>
      <div className="flex-grow flex items-center justify-center relative">
        <div className="absolute inset-0 bg-black opacity-50"></div>
        <div className="relative z-10 text-center text-white p-6 max-w-2xl mx-auto">
          <h1 className="text-5xl font-bold mb-4 animate-fade-in">Welcome to 3D Model Generator</h1>
          <p className="text-lg mb-6">Transform your architectural blueprints into stunning 3D models with AI.</p>
          <div className="flex justify-center gap-4">
            <Link to="/login" className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition duration-300">
              Login
            </Link>
            <Link to="/register" className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition duration-300">
              Register
            </Link>
          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
}

export default Home;
