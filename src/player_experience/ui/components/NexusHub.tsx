/**
 * Nexus Hub Component
 *
 * The central hub interface for The Nexus Codex, displaying story spheres
 * and providing navigation to different therapeutic worlds.
 */

import React, { useState, useEffect, useRef } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, Sphere, Text, Html } from '@react-three/drei';
import * as THREE from 'three';
import { motion, AnimatePresence } from 'framer-motion';
import { useNexusState } from '../hooks/useNexusState';
import { useStorySpheres } from '../hooks/useStorySpheres';
import { WorldCard } from './WorldCard';
import { LoadingSpinner } from './LoadingSpinner';
import { ErrorBoundary } from './ErrorBoundary';

interface StorySphereProps {
  sphere: {
    sphere_id: string;
    world_id: string;
    world_title: string;
    visual_state: string;
    pulse_frequency: number;
    position: { x: number; y: number; z: number };
    color_primary: string;
    color_secondary: string;
    size_scale: number;
    world_genre: string;
    world_rating: number;
  };
  onSphereClick: (worldId: string) => void;
  onSphereHover: (sphere: any) => void;
}

const StorySphere: React.FC<StorySphereProps> = ({ sphere, onSphereClick, onSphereHover }) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);

  useFrame((state) => {
    if (meshRef.current) {
      // Pulsing animation based on sphere's pulse frequency
      const pulse = Math.sin(state.clock.elapsedTime * sphere.pulse_frequency * 2) * 0.1 + 1;
      meshRef.current.scale.setScalar(sphere.size_scale * pulse);

      // Gentle rotation
      meshRef.current.rotation.y += 0.005;

      // Visual state effects
      if (sphere.visual_state === 'bright_glow') {
        meshRef.current.rotation.y += 0.01;
      } else if (sphere.visual_state === 'dim_flicker') {
        const flicker = Math.random() > 0.8 ? 0.5 : 1.0;
        meshRef.current.material.opacity = flicker;
      }
    }
  });

  const getSphereColor = () => {
    switch (sphere.visual_state) {
      case 'bright_glow':
        return sphere.color_primary;
      case 'gentle_pulse':
        return sphere.color_primary;
      case 'dim_flicker':
        return '#666666';
      case 'dark_void':
        return '#333333';
      default:
        return sphere.color_primary;
    }
  };

  const getEmissiveIntensity = () => {
    switch (sphere.visual_state) {
      case 'bright_glow':
        return 0.5;
      case 'gentle_pulse':
        return 0.2;
      case 'dim_flicker':
        return 0.1;
      case 'dark_void':
        return 0.0;
      default:
        return 0.2;
    }
  };

  return (
    <group position={[sphere.position.x / 10, sphere.position.y / 10, sphere.position.z / 10]}>
      <Sphere
        ref={meshRef}
        args={[1, 32, 32]}
        onClick={() => onSphereClick(sphere.world_id)}
        onPointerOver={(e) => {
          e.stopPropagation();
          setHovered(true);
          onSphereHover(sphere);
        }}
        onPointerOut={() => setHovered(false)}
      >
        <meshStandardMaterial
          color={getSphereColor()}
          emissive={getSphereColor()}
          emissiveIntensity={getEmissiveIntensity()}
          transparent
          opacity={sphere.visual_state === 'dark_void' ? 0.3 : 0.8}
        />
      </Sphere>

      {hovered && (
        <Html distanceFactor={10}>
          <div className="bg-white/90 backdrop-blur-sm rounded-lg p-3 shadow-lg max-w-xs">
            <h3 className="font-semibold text-gray-900">{sphere.world_title}</h3>
            <p className="text-sm text-gray-600 capitalize">{sphere.world_genre}</p>
            <div className="flex items-center mt-1">
              <div className="flex text-yellow-400">
                {[...Array(5)].map((_, i) => (
                  <span key={i} className={i < Math.floor(sphere.world_rating) ? 'text-yellow-400' : 'text-gray-300'}>
                    ★
                  </span>
                ))}
              </div>
              <span className="ml-2 text-sm text-gray-600">{sphere.world_rating.toFixed(1)}</span>
            </div>
          </div>
        </Html>
      )}
    </group>
  );
};

const NexusTree: React.FC = () => {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.1) * 0.1;
    }
  });

  return (
    <group position={[0, 0, 0]}>
      {/* Central crystalline tree structure */}
      <mesh ref={meshRef}>
        <cylinderGeometry args={[0.2, 0.5, 4, 8]} />
        <meshStandardMaterial
          color="#2E86AB"
          emissive="#2E86AB"
          emissiveIntensity={0.3}
          transparent
          opacity={0.7}
        />
      </mesh>

      {/* Tree branches */}
      {[...Array(6)].map((_, i) => (
        <mesh key={i} position={[Math.cos(i) * 1.5, 1 + i * 0.3, Math.sin(i) * 1.5]}>
          <cylinderGeometry args={[0.05, 0.1, 1, 6]} />
          <meshStandardMaterial
            color="#F18F01"
            emissive="#F18F01"
            emissiveIntensity={0.2}
            transparent
            opacity={0.6}
          />
        </mesh>
      ))}

      <Text
        position={[0, -3, 0]}
        fontSize={0.5}
        color="#2E86AB"
        anchorX="center"
        anchorY="middle"
      >
        The Nexus Codex
      </Text>
    </group>
  );
};

export const NexusHub: React.FC = () => {
  const { nexusState, loading: nexusLoading, error: nexusError } = useNexusState();
  const { spheres, loading: spheresLoading, error: spheresError } = useStorySpheres();
  const [selectedSphere, setSelectedSphere] = useState<any>(null);
  const [showWorldDetails, setShowWorldDetails] = useState(false);
  const [cameraPosition, setCameraPosition] = useState<[number, number, number]>([0, 0, 10]);

  const handleSphereClick = (worldId: string) => {
    const sphere = spheres.find(s => s.world_id === worldId);
    if (sphere) {
      setSelectedSphere(sphere);
      setShowWorldDetails(true);
    }
  };

  const handleSphereHover = (sphere: any) => {
    // Could add hover effects or preview information
  };

  const handleEnterWorld = (worldId: string) => {
    // Navigate to world entry
    window.location.href = `/worlds/${worldId}/enter`;
  };

  if (nexusLoading || spheresLoading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900">
        <LoadingSpinner size="large" message="Loading the Nexus Codex..." />
      </div>
    );
  }

  if (nexusError || spheresError) {
    return (
      <div className="flex items-center justify-center h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900">
        <div className="text-center text-white">
          <h2 className="text-2xl font-bold mb-4">Connection to the Nexus Lost</h2>
          <p className="text-gray-300 mb-6">
            {nexusError || spheresError || 'Unable to connect to the Nexus Codex'}
          </p>
          <button
            onClick={() => window.location.reload()}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold transition-colors"
          >
            Reconnect to Nexus
          </button>
        </div>
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <div className="h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 relative overflow-hidden">
        {/* 3D Nexus Visualization */}
        <Canvas
          camera={{ position: cameraPosition, fov: 75 }}
          className="absolute inset-0"
        >
          <ambientLight intensity={0.4} />
          <pointLight position={[10, 10, 10]} intensity={1} />
          <pointLight position={[-10, -10, -10]} intensity={0.5} color="#F18F01" />

          <NexusTree />

          {spheres.map((sphere) => (
            <StorySphere
              key={sphere.sphere_id}
              sphere={sphere}
              onSphereClick={handleSphereClick}
              onSphereHover={handleSphereHover}
            />
          ))}

          <OrbitControls
            enablePan={true}
            enableZoom={true}
            enableRotate={true}
            minDistance={5}
            maxDistance={50}
            autoRotate={true}
            autoRotateSpeed={0.5}
          />
        </Canvas>

        {/* UI Overlay */}
        <div className="absolute inset-0 pointer-events-none">
          {/* Top Bar */}
          <div className="absolute top-0 left-0 right-0 p-6 pointer-events-auto">
            <div className="flex justify-between items-center">
              <div className="text-white">
                <h1 className="text-3xl font-bold">The Nexus Codex</h1>
                <p className="text-blue-200">
                  {nexusState?.total_worlds} worlds • {nexusState?.active_story_weavers} active weavers
                </p>
              </div>

              <div className="flex space-x-4">
                <button className="px-4 py-2 bg-white/20 backdrop-blur-sm rounded-lg text-white hover:bg-white/30 transition-colors">
                  Create World
                </button>
                <button className="px-4 py-2 bg-white/20 backdrop-blur-sm rounded-lg text-white hover:bg-white/30 transition-colors">
                  My Profile
                </button>
              </div>
            </div>
          </div>

          {/* Threat Level Indicator */}
          {nexusState && (
            <div className="absolute top-6 right-6 pointer-events-auto">
              <div className="bg-black/50 backdrop-blur-sm rounded-lg p-4 text-white">
                <h3 className="font-semibold mb-2">Nexus Status</h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Narrative Strength:</span>
                    <span className="text-green-400">{(nexusState.narrative_strength * 100).toFixed(0)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Silence Threat:</span>
                    <span className={nexusState.silence_threat_level > 0.5 ? 'text-red-400' : 'text-yellow-400'}>
                      {(nexusState.silence_threat_level * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Instructions */}
          <div className="absolute bottom-6 left-6 pointer-events-auto">
            <div className="bg-black/50 backdrop-blur-sm rounded-lg p-4 text-white max-w-sm">
              <h3 className="font-semibold mb-2">Navigation</h3>
              <ul className="text-sm space-y-1 text-gray-300">
                <li>• Click and drag to rotate view</li>
                <li>• Scroll to zoom in/out</li>
                <li>• Click story spheres to enter worlds</li>
                <li>• Hover for world information</li>
              </ul>
            </div>
          </div>
        </div>

        {/* World Details Modal */}
        <AnimatePresence>
          {showWorldDetails && selectedSphere && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center pointer-events-auto"
              onClick={() => setShowWorldDetails(false)}
            >
              <motion.div
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.8, opacity: 0 }}
                className="bg-white rounded-xl p-6 max-w-md w-full mx-4"
                onClick={(e) => e.stopPropagation()}
              >
                <WorldCard
                  world={{
                    world_id: selectedSphere.world_id,
                    title: selectedSphere.world_title,
                    genre: selectedSphere.world_genre,
                    rating: selectedSphere.world_rating,
                    // Add more world details as needed
                  }}
                  onEnter={() => handleEnterWorld(selectedSphere.world_id)}
                  onClose={() => setShowWorldDetails(false)}
                />
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </ErrorBoundary>
  );
};
