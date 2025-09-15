import React from "react";
import { Provider } from "react-redux";
import { store } from "./store/store";
import { DebugToolsPanel } from "./components/debug/DebugToolsPanel";

// Simple dashboard component for testing
const Dashboard = () => (
  <div className="p-8">
    <h1 className="text-3xl font-bold text-gray-900 mb-6">
      TTA Developer Interface
    </h1>
    <p className="text-gray-600 mb-4">
      Welcome to the enhanced TTA Developer Interface with comprehensive
      debugging tools.
    </p>
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
      <h2 className="text-lg font-semibold text-blue-900 mb-2">
        Enhanced Debug Tools Available
      </h2>
      <ul className="text-blue-800 space-y-1">
        <li>• Real-time WebSocket monitoring</li>
        <li>• Performance baseline recording</li>
        <li>• Custom event system</li>
        <li>• Collaborative debugging</li>
        <li>• React DevTools integration</li>
        <li>• CI/CD pipeline integration</li>
      </ul>
    </div>
  </div>
);

const App = () => {
  return (
    <Provider store={store}>
      <div className="min-h-screen bg-gray-100">
        <Dashboard />
        <DebugToolsPanel />
      </div>
    </Provider>
  );
};

export default App;
