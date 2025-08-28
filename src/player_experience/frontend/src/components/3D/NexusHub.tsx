/**
 * Nexus Hub Component
 *
 * The central hub interface for The Nexus Codex, displaying story spheres
 * and providing navigation to different therapeutic worlds.
 *
 * Updated for integration with the Nexus Codex API backend.
 */

import { OrbitControls, Sphere, Text } from "@react-three/drei";
import { Canvas, useFrame } from "@react-three/fiber";
import { AnimatePresence, motion } from "framer-motion";
import React, { Suspense, useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { useAuthGuard } from "../../hooks/useAuthGuard";
import { useNexusState } from "../../hooks/useNexusState";
import { StorySphereData, useStorySpheres } from "../../hooks/useStorySpheres";
import { nexusAPI } from "../../services/api";
import GenreFilter from "../UI/GenreFilter";
import { WorldEntryModal } from "../World";
import { useWorldEntry } from "../../hooks/useWorldEntry";
import { NexusStateDisplay } from "../Nexus";
import { ThreeDErrorBoundary } from "../ErrorBoundary";

// Error Boundary for 3D Canvas
class Canvas3DErrorBoundary extends React.Component<
  { children: React.ReactNode; onError?: (error: Error) => void },
  { hasError: boolean; error: Error | null }
> {
  constructor(props: any) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: any) {
    console.error("3D Canvas Error:", error, errorInfo);
    this.props.onError?.(error);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex items-center justify-center h-full bg-gray-900 rounded-lg">
          <div className="text-center p-8">
            <div className="text-yellow-500 text-2xl mb-4">🎮</div>
            <h3 className="text-white text-lg mb-2">3D Rendering Error</h3>
            <p className="text-gray-400 text-sm mb-4">
              Unable to render 3D visualization. This might be due to:
            </p>
            <ul className="text-gray-400 text-xs text-left mb-4 space-y-1">
              <li>• WebGL not supported by your browser</li>
              <li>• Graphics driver issues</li>
              <li>• Hardware acceleration disabled</li>
            </ul>
            <button
              onClick={() => this.setState({ hasError: false, error: null })}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
            >
              Try Again
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

interface StorySphereProps {
  sphere: StorySphereData;
  onSphereClick: (worldId: string) => void;
  onSphereHover: (sphere: StorySphereData | null) => void;
  isSelected?: boolean;
  isHovered?: boolean;
}

const StorySphere: React.FC<StorySphereProps> = ({
  sphere,
  onSphereClick,
  onSphereHover,
  isSelected = false,
  isHovered = false,
}) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const [localHovered, setLocalHovered] = useState(false);

  const hovered = isHovered || localHovered;

  useFrame((state) => {
    if (meshRef.current) {
      // Pulsing animation based on sphere's pulse frequency
      const pulse =
        Math.sin(state.clock.elapsedTime * sphere.pulse_frequency * 2) * 0.1 +
        1;
      meshRef.current.scale.setScalar(sphere.size_scale * pulse);

      // Gentle rotation
      meshRef.current.rotation.y += 0.005;

      // Visual state effects
      if (sphere.visual_state === "active") {
        meshRef.current.rotation.x += 0.01;
      }
    }
  });

  const handleClick = () => {
    onSphereClick(sphere.world_id);
  };

  const handlePointerOver = () => {
    setLocalHovered(true);
    onSphereHover(sphere);
    document.body.style.cursor = "pointer";
  };

  const handlePointerOut = () => {
    setLocalHovered(false);
    onSphereHover(null);
    document.body.style.cursor = "auto";
  };

  return (
    <group position={[sphere.position.x, sphere.position.y, sphere.position.z]}>
      <Sphere
        ref={meshRef}
        args={[1, 32, 32]}
        onClick={handleClick}
        onPointerOver={handlePointerOver}
        onPointerOut={handlePointerOut}
      >
        <meshStandardMaterial
          color={
            isSelected
              ? "#ffffff"
              : hovered
              ? sphere.color_secondary
              : sphere.color_primary
          }
          emissive={
            isSelected
              ? sphere.color_primary
              : hovered
              ? sphere.color_primary
              : "#000000"
          }
          emissiveIntensity={isSelected ? 0.5 : hovered ? 0.3 : 0.1}
          transparent
          opacity={isSelected ? 1.0 : 0.8}
        />
      </Sphere>

      {/* World title text */}
      <Text
        position={[0, -1.5, 0]}
        fontSize={0.3}
        color="white"
        anchorX="center"
        anchorY="middle"
      >
        {sphere.world_title}
      </Text>

      {/* Genre indicator */}
      <Text
        position={[0, -2, 0]}
        fontSize={0.2}
        color="#888"
        anchorX="center"
        anchorY="middle"
      >
        {sphere.world_genre}
      </Text>
    </group>
  );
};

interface NexusHubProps {
  onWorldSelect?: (worldId: string) => void;
  genreFilter?: string;
  threatLevelFilter?: string;
}

const NexusHub: React.FC<NexusHubProps> = ({
  onWorldSelect,
  genreFilter: initialGenreFilter,
  threatLevelFilter: initialThreatLevelFilter,
}) => {
  const { isAuthenticated } = useAuthGuard({ autoRedirect: false });
  const [hoveredSphere, setHoveredSphere] = useState<StorySphereData | null>(
    null
  );
  const [selectedSphere, setSelectedSphere] = useState<StorySphereData | null>(
    null
  );
  const [genreFilter, setGenreFilter] = useState<string | undefined>(
    initialGenreFilter
  );
  const [threatLevelFilter, setThreatLevelFilter] = useState<
    string | undefined
  >(initialThreatLevelFilter);
  const [isFilterOpen, setIsFilterOpen] = useState(false);
  const [showEntryModal, setShowEntryModal] = useState(false);
  const [entryWorldId, setEntryWorldId] = useState<string | null>(null);

  const {
    enterWorld,
    entering,
    error: entryError,
  } = useWorldEntry({
    onSuccess: (response) => {
      console.log("Successfully entered world:", response);
      // Handle successful world entry - could navigate to game session
    },
    onError: (error) => {
      console.error("Failed to enter world:", error);
    },
  });

  // Use custom hooks for data management
  const {
    spheres,
    loading: spheresLoading,
    error: spheresError,
    refetch: refetchSpheres,
    updateFilters,
    clearError: clearSpheresError,
  } = useStorySpheres({
    filters: {
      genre: genreFilter,
      threat_level: threatLevelFilter,
    },
    autoRefresh: true,
    refreshInterval: 30000,
    onError: (error) => {
      console.error("StorySpheres error:", error);
    },
  });

  const {
    state: nexusState,
    loading: nexusLoading,
    error: nexusError,
    refetch: refetchNexusState,
    clearError: clearNexusError,
  } = useNexusState({
    requireAuth: isAuthenticated,
    autoRefresh: true,
    refreshInterval: 15000,
    onError: (error) => {
      console.error("NexusState error:", error);
    },
  });

  // Update filters when props change
  useEffect(() => {
    updateFilters({
      genre: genreFilter,
      threat_level: threatLevelFilter,
    });
  }, [genreFilter, threatLevelFilter, updateFilters]);

  const loading = spheresLoading || nexusLoading;
  const error = spheresError || nexusError;

  const handleSphereClick = async (worldId: string) => {
    // Find and select the clicked sphere
    const clickedSphere = spheres.find((s) => s.world_id === worldId);
    if (clickedSphere) {
      setSelectedSphere(clickedSphere);
    }

    // Set up world entry modal
    setEntryWorldId(worldId);
    setShowEntryModal(true);

    if (onWorldSelect) {
      onWorldSelect(worldId);
    }
  };

  const handleSphereHover = (sphere: StorySphereData | null) => {
    setHoveredSphere(sphere);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-black">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-white">Loading Nexus Hub...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen bg-black">
        <div className="text-center max-w-md">
          <div className="text-red-500 text-xl mb-4">⚠️</div>
          <p className="text-white mb-4">Failed to load Nexus Hub</p>
          <p className="text-gray-400 text-sm mb-6">{error}</p>
          <div className="space-y-3">
            <button
              onClick={() => {
                clearSpheresError();
                clearNexusError();
                refetchSpheres();
                refetchNexusState();
              }}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
            >
              Retry Connection
            </button>
            <button
              onClick={() => window.location.reload()}
              className="w-full px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors"
            >
              Reload Page
            </button>
          </div>
          {spheresError && nexusError && (
            <div className="mt-4 p-3 bg-red-900 bg-opacity-50 rounded text-xs text-red-200">
              <p className="font-semibold">Multiple errors detected:</p>
              <p>Spheres: {spheresError}</p>
              <p>Nexus: {nexusError}</p>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="relative w-full h-screen bg-black overflow-hidden">
      {/* 3D Canvas with Error Boundary */}
      <Canvas3DErrorBoundary
        onError={(error) => {
          console.error("Canvas rendering failed:", error);
        }}
      >
        <Canvas
          camera={{ position: [0, 0, 15], fov: 75 }}
          gl={{
            antialias: true,
            alpha: true,
            powerPreference: "high-performance",
            failIfMajorPerformanceCaveat: false,
          }}
          onCreated={({ gl }) => {
            // Enable WebGL extensions for better performance
            gl.setPixelRatio(Math.min(window.devicePixelRatio, 2));
          }}
        >
          <Suspense fallback={null}>
            {/* Lighting */}
            <ambientLight intensity={0.4} />
            <pointLight position={[10, 10, 10]} intensity={1} />
            <pointLight
              position={[-10, -10, -10]}
              intensity={0.5}
              color="#4a90e2"
            />

            {/* Story Spheres */}
            {spheres.map((sphere) => (
              <StorySphere
                key={sphere.sphere_id}
                sphere={sphere}
                onSphereClick={handleSphereClick}
                onSphereHover={handleSphereHover}
                isSelected={selectedSphere?.sphere_id === sphere.sphere_id}
                isHovered={hoveredSphere?.sphere_id === sphere.sphere_id}
              />
            ))}

            {/* Camera Controls */}
            <OrbitControls
              enablePan={true}
              enableZoom={true}
              enableRotate={true}
              minDistance={5}
              maxDistance={50}
              maxPolarAngle={Math.PI}
              minPolarAngle={0}
            />
          </Suspense>
        </Canvas>
      </Canvas3DErrorBoundary>

      {/* UI Overlay */}
      <div className="absolute top-4 left-4 z-10 space-y-4">
        {/* Hub Info */}
        <div className="bg-black bg-opacity-50 rounded-lg p-4 text-white space-y-3">
          <div>
            <h1 className="text-2xl font-bold mb-2">The Nexus Codex</h1>
            <p className="text-sm text-gray-300">
              {spheres.length} story worlds available
            </p>
          </div>

          {/* Real-time Nexus State Display */}
          <NexusStateDisplay
            variant="compact"
            className="text-white"
            showLastUpdated={false}
            autoRefresh={true}
            refreshInterval={15000}
          />
        </div>

        {/* Genre Filter */}
        <GenreFilter
          selectedGenre={genreFilter}
          selectedThreatLevel={threatLevelFilter}
          onGenreChange={setGenreFilter}
          onThreatLevelChange={setThreatLevelFilter}
          isOpen={isFilterOpen}
          onToggle={() => setIsFilterOpen(!isFilterOpen)}
        />
      </div>

      {/* Sphere Info Panel */}
      <AnimatePresence>
        {(hoveredSphere || selectedSphere) && (
          <motion.div
            initial={{ opacity: 0, x: 300 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 300 }}
            className={`absolute top-4 right-4 z-10 rounded-lg p-4 text-white max-w-sm ${
              selectedSphere
                ? "bg-blue-900 bg-opacity-90 border-2 border-blue-400"
                : "bg-black bg-opacity-80"
            }`}
          >
            {(() => {
              const displaySphere = selectedSphere || hoveredSphere;
              if (!displaySphere) return null;

              return (
                <>
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-lg font-bold">
                      {displaySphere.world_title}
                    </h3>
                    {selectedSphere && (
                      <button
                        onClick={() => setSelectedSphere(null)}
                        className="text-gray-400 hover:text-white text-xl"
                        title="Deselect"
                      >
                        ×
                      </button>
                    )}
                  </div>

                  <div className="space-y-2 mb-4">
                    <div className="flex items-center space-x-2">
                      <span className="text-xs bg-gray-700 px-2 py-1 rounded">
                        {displaySphere.world_genre}
                      </span>
                      {displaySphere.threat_level && (
                        <span
                          className={`text-xs px-2 py-1 rounded ${
                            displaySphere.threat_level === "Low"
                              ? "bg-green-600"
                              : displaySphere.threat_level === "Medium"
                              ? "bg-yellow-600"
                              : displaySphere.threat_level === "High"
                              ? "bg-orange-600"
                              : "bg-red-600"
                          }`}
                        >
                          {displaySphere.threat_level}
                        </span>
                      )}
                    </div>

                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div>
                        <span className="text-gray-400">Rating:</span>
                        <div className="flex items-center">
                          {[...Array(5)].map((_, i) => (
                            <span
                              key={i}
                              className={`text-xs ${
                                i < displaySphere.world_rating
                                  ? "text-yellow-400"
                                  : "text-gray-600"
                              }`}
                            >
                              ★
                            </span>
                          ))}
                          <span className="ml-1 text-gray-300">
                            {displaySphere.world_rating}/5
                          </span>
                        </div>
                      </div>

                      {displaySphere.narrative_strength && (
                        <div>
                          <span className="text-gray-400">Narrative:</span>
                          <div className="text-blue-300">
                            {displaySphere.narrative_strength}%
                          </div>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="space-y-2">
                    <button
                      onClick={() => handleSphereClick(displaySphere.world_id)}
                      className="w-full px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm transition-colors"
                    >
                      Enter World
                    </button>

                    {selectedSphere && (
                      <button
                        onClick={() => {
                          console.log(
                            "Add to favorites:",
                            displaySphere.world_id
                          );
                        }}
                        className="w-full px-3 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 text-sm transition-colors"
                      >
                        Add to Favorites
                      </button>
                    )}
                  </div>
                </>
              );
            })()}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Controls Help */}
      <div className="absolute bottom-4 left-4 z-10">
        <div className="bg-black bg-opacity-50 rounded-lg p-3 text-white text-xs">
          <p>🖱️ Click and drag to rotate</p>
          <p>🔍 Scroll to zoom</p>
          <p>✨ Click spheres to enter worlds</p>
        </div>
      </div>

      {/* World Entry Modal */}
      {showEntryModal && entryWorldId && (
        <WorldEntryModal
          worldId={entryWorldId}
          isOpen={showEntryModal}
          onClose={() => {
            setShowEntryModal(false);
            setEntryWorldId(null);
          }}
          onEntrySuccess={(response) => {
            console.log("World entry successful:", response);
            setShowEntryModal(false);
            setEntryWorldId(null);
            // Handle successful entry - could navigate to game session
          }}
          onEntryError={(error) => {
            console.error("World entry failed:", error);
            // Error is handled by the modal itself
          }}
        />
      )}
    </div>
  );
};

export default NexusHub;
