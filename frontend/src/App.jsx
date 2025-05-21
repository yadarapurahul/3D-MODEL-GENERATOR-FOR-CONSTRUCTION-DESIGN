import { Routes, Route } from 'react-router-dom';
import Login from './Auth/Login';
import Register from './Auth/Register';
import ForgotPassword from './Auth/ForgotPassword';
import ResetPassword from './Auth/ResetPassword';
import UpdateProfile from './Auth/UpdateProfile';
import Home from './pages/Home';
import Dashboard from './pages/Dashboard';
import Logout from './Auth/Logout';
import BlueprintViewer from './threeD/BlueprintViewer';
import Upload2DBlueprint from './components/Upload2DBlueprint';
function App() {
  return (
    <div className="min-h-screen bg-gray-100">
      <div className="container mx-auto p-4">
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/reset-password" element={<ResetPassword />} />
            <Route path="/update-profile" element={<UpdateProfile />} />
            <Route path="/" element={<Home />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/logout" element={<Logout />} />
            <Route path="/blueprint/:id" element={<BlueprintViewer />} />
            <Route path="/upload-blueprint" element={<Upload2DBlueprint />} />
          </Routes>
      </div>
    </div>
  );
}

export default App;