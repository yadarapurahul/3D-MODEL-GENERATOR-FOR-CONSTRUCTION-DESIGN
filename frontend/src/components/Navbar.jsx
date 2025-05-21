import { Link, useNavigate } from 'react-router-dom';

function Navbar() {
  const navigate = useNavigate();
  
  const handleLogout = () => {
    // Clear token or session data
    localStorage.removeItem('token');
    navigate('/login');
  };

  return (
    <nav className="bg-blue-600 p-4">
      <div className="container mx-auto flex justify-between items-center">
        <div className="space-x-4">
          <Link to="/logout" className="text-white hover:text-blue-200">Login</Link>
          <Link to="/home" className="text-white hover:text-blue-200">Home</Link>
          <Link to="/update-profile" className="text-white hover:text-blue-200">Profile</Link>
          <button onClick={handleLogout} className="text-white hover:text-blue-200">Logout</button>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;