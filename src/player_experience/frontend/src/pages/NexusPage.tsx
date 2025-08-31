import React from "react";
import NexusHub from "../components/3D/NexusHub";
import {
  ErrorBoundary,
  ThreeDErrorBoundary,
} from "../components/ErrorBoundary";

const NexusPage: React.FC = () => {
  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gray-900">
        <ThreeDErrorBoundary>
          <NexusHub />
        </ThreeDErrorBoundary>
      </div>
    </ErrorBoundary>
  );
};

export default NexusPage;
