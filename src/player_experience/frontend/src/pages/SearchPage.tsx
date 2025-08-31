import React, { useState } from "react";
import { motion } from "framer-motion";
import { WorldSearch } from "../components/Search";
import { WorldDetailsModal } from "../components/World";
import { useAuthGuard } from "../hooks/useAuthGuard";

const SearchPage: React.FC = () => {
  const { isAuthenticated, user } = useAuthGuard({ autoRedirect: true });
  const [selectedWorldId, setSelectedWorldId] = useState<string | null>(null);
  const [showWorldDetails, setShowWorldDetails] = useState(false);

  const handleWorldSelect = (worldId: string) => {
    setSelectedWorldId(worldId);
    setShowWorldDetails(true);
  };

  const handleCloseWorldDetails = () => {
    setShowWorldDetails(false);
    setSelectedWorldId(null);
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="py-6">
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <h1 className="text-3xl font-bold text-gray-900">
                Discover Worlds
              </h1>
              <p className="mt-2 text-gray-600">
                Search and explore therapeutic text adventure worlds tailored to
                your needs
              </p>
            </motion.div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <WorldSearch onWorldSelect={handleWorldSelect} className="w-full" />
        </motion.div>

        {/* Quick Search Suggestions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="mt-8"
        >
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Popular Searches
            </h2>
            <div className="flex flex-wrap gap-2">
              {[
                "Anxiety Management",
                "Fantasy Adventure",
                "Beginner Friendly",
                "Social Skills",
                "Mystery Solving",
                "Emotional Regulation",
                "Short Sessions",
                "Group Therapy",
              ].map((tag) => (
                <button
                  key={tag}
                  className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm hover:bg-blue-200 transition-colors"
                  onClick={() => {
                    // This would trigger a search with the tag
                    console.log("Search for:", tag);
                  }}
                >
                  {tag}
                </button>
              ))}
            </div>
          </div>
        </motion.div>

        {/* Search Tips */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.6 }}
          className="mt-8"
        >
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Search Tips
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-700">
              <div className="flex items-start space-x-2">
                <div className="text-blue-600 mt-0.5">💡</div>
                <div>
                  <strong>Use specific keywords:</strong> Try searching for
                  therapeutic goals like "anxiety", "depression", or "social
                  skills"
                </div>
              </div>
              <div className="flex items-start space-x-2">
                <div className="text-blue-600 mt-0.5">🎯</div>
                <div>
                  <strong>Filter by difficulty:</strong> Choose beginner,
                  intermediate, or advanced based on your comfort level
                </div>
              </div>
              <div className="flex items-start space-x-2">
                <div className="text-blue-600 mt-0.5">⏱️</div>
                <div>
                  <strong>Set time limits:</strong> Use the duration filter to
                  find worlds that fit your available time
                </div>
              </div>
              <div className="flex items-start space-x-2">
                <div className="text-blue-600 mt-0.5">🌟</div>
                <div>
                  <strong>Check ratings:</strong> Higher-rated worlds often
                  provide better therapeutic experiences
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>

      {/* World Details Modal */}
      {showWorldDetails && selectedWorldId && (
        <WorldDetailsModal
          worldId={selectedWorldId}
          isOpen={showWorldDetails}
          onClose={handleCloseWorldDetails}
          onCustomize={() => {
            console.log("Customizing world:", selectedWorldId);
            // Handle world customization logic here
          }}
        />
      )}
    </div>
  );
};

export default SearchPage;
