import { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import axios from 'axios';

function BlueprintViewer({ blueprintId }) {
  const mountRef = useRef(null);
  const [view, setView] = useState('front');
  const [dimensions, setDimensions] = useState(null);
  const [color, setColor] = useState('none');

  useEffect(() => {
    const fetchBlueprint = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(`http://localhost:5000/api/blueprint/${blueprintId}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setDimensions(JSON.parse(response.data.dimensions));
        setColor(response.data.color);
      } catch (err) {
        console.error('Failed to load blueprint:', err);
      }
    };
    fetchBlueprint();

    // Three.js setup
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, 600 / 400, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer();
    renderer.setSize(600, 400);
    mountRef.current.appendChild(renderer.domElement);

    // Simple cube as placeholder 3D model
    const geometry = new THREE.BoxGeometry(10, 20, 30);
    const material = new THREE.MeshBasicMaterial({ color: color === 'none' ? 0x00ff00 : parseInt(color.replace('#', '0x')) });
    const cube = new THREE.Mesh(geometry, material);
    scene.add(cube);

    // Add dimensions text
    if (dimensions) {
      const loader = new THREE.FontLoader();
      loader.load('https://threejs.org/examples/fonts/helvetiker_regular.typeface.json', (font) => {
        const textGeometry = new THREE.TextGeometry(`X: ${dimensions.x} Y: ${dimensions.y} Z: ${dimensions.z}`, {
          font,
          size: 2,
          height: 0.1,
        });
        const textMaterial = new THREE.MeshBasicMaterial({ color: 0xffffff });
        const textMesh = new THREE.Mesh(textGeometry, textMaterial);
        textMesh.position.set(-5, 25, 0);
        scene.add(textMesh);
      });
    }

    // Camera positions for views
    const views = {
      top: [0, 20, 0],
      front: [0, 0, 20],
      right: [20, 0, 0],
      left: [-20, 0, 0],
    };

    camera.position.set(...views[view]);
    camera.lookAt(0, 0, 0);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.autoRotate = true; // Enable 360-degree rotation
    controls.autoRotateSpeed = 2;

    const animate = () => {
      requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    };
    animate();

    return () => {
      if (mountRef.current && renderer.domElement) {
        mountRef.current.removeChild(renderer.domElement);
      }
    };
  }, [blueprintId, view, color, dimensions]);

  return (
    <div className="text-center">
      <div ref={mountRef}></div>
      <div className="mt-4">
        <select
          value={view}
          onChange={(e) => setView(e.target.value)}
          className="border p-2 rounded-lg"
        >
          <option value="top">Top View</option>
          <option value="front">Front View</option>
          <option value="right">Right Side View</option>
          <option value="left">Left Side View</option>
        </select>
      </div>
    </div>
  );
}

export default BlueprintViewer;