import { useState } from 'react';
import axios from 'axios';
import BlueprintViewer from '../threeD/BlueprintViewer';

function BlueprintManager({ blueprints }) {
  const [error, setError] = useState('');
  const [color, setColor] = useState('');

  const handleDelete = async (blueprintId) => {
    if (!window.confirm('Are you sure you want to delete this blueprint?')) return;
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`http://localhost:5000/api/blueprint/${blueprintId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      alert('Blueprint deleted successfully');
      window.location.reload(); // Refresh to update blueprint list
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to delete blueprint');
    }
  };

  const handleColorUpdate = async (blueprintId) => {
    if (!color) {
      setError('Please select a color');
      return;
    }
    try {
      const token = localStorage.getItem('token');
      await axios.put(
        `http://localhost:5000/api/blueprint/${blueprintId}/color`,
        { color },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert('Blueprint color updated successfully');
      setColor('');
      window.location.reload(); // Refresh to update blueprint
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to update color');
    }
  };

  const handleExport = async (blueprintId, format) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`http://localhost:5000/api/blueprint/${blueprintId}/export?format=${format}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      // Trigger file download
      const filePath = response.data.file_path;
      const link = document.createElement('a');
      link.href = `http://localhost:5000/${filePath}`; // Adjust based on your server setup
      link.download = `blueprint_${blueprintId}.${format}`;
      link.click();
      alert('Blueprint exported successfully');
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to export blueprint');
    }
  };

  return (
    <div className="mt-6">
      <h3 className="text-2xl font-semibold mb-4">Your Blueprints</h3>
      {error && <p className="text-red-500 mb-4">{error}</p>}
      {blueprints.length === 0 ? (
        <p>No blueprints available.</p>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {blueprints.map((blueprint) => (
            <div key={blueprint.id} className="border p-4 rounded-lg">
              <p><strong>Filename:</strong> {blueprint.filename}</p>
              <p><strong>Dimensions:</strong> {blueprint.dimensions}</p>
              <p><strong>Color:</strong> {blueprint.color}</p>
              <BlueprintViewer blueprintId={blueprint.id} />
              <div className="mt-4 flex gap-2">
                <input
                  type="color"
                  value={color || blueprint.color}
                  onChange={(e) => setColor(e.target.value)}
                  className="p-1 border rounded"
                />
                <button
                  onClick={() => handleColorUpdate(blueprint.id)}
                  className="bg-yellow-600 text-white px-4 py-2 rounded-lg hover:bg-yellow-700"
                >
                  Update Color
                </button>
                <button
                  onClick={() => handleDelete(blueprint.id)}
                  className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700"
                >
                  Delete
                </button>
                <button
                  onClick={() => handleExport(blueprint.id, 'obj')}
                  className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700"
                >
                  Export OBJ
                </button>
                <button
                  onClick={() => handleExport(blueprint.id, 'stl')}
                  className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700"
                >
                  Export STL
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default BlueprintManager;