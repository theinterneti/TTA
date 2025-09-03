import React, { useState } from "react";
import {
  BugAntIcon,
  XMarkIcon,
  GlobeAltIcon,
  ExclamationTriangleIcon,
  CommandLineIcon,
  ChartBarIcon,
  CpuChipIcon,
  PlayIcon,
  PauseIcon,
  TrashIcon,
  CubeIcon,
  ArrowTrendingUpIcon,
  UsersIcon,
} from "@heroicons/react/24/outline";

export const DebugToolsPanel: React.FC = () => {
  const [isOpen, setIsOpen] = useState(true);
  const [activeTab, setActiveTab] = useState("network");
  const [isRecording, setIsRecording] = useState(true);

  const tabs = [
    { id: "network", name: "Network", icon: GlobeAltIcon, count: 12 },
    { id: "errors", name: "Errors", icon: ExclamationTriangleIcon, count: 3 },
    { id: "console", name: "Console", icon: CommandLineIcon, count: 45 },
    { id: "performance", name: "Performance", icon: ChartBarIcon, count: 8 },
    { id: "components", name: "Components", icon: CpuChipIcon, count: 0 },
    { id: "events", name: "Events", icon: CubeIcon, count: 15 },
    { id: "baselines", name: "Baselines", icon: ArrowTrendingUpIcon, count: 7 },
    { id: "collaborate", name: "Collaborate", icon: UsersIcon, count: 2 },
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case "network":
        return (
          <div className="p-4">
            <h3 className="text-lg font-semibold mb-4">Network Monitor</h3>
            <div className="space-y-2">
              <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">WebSocket Status</span>
                  <span className="text-green-600 text-sm">3 connected</span>
                </div>
                <div className="text-xs text-gray-600 mt-1">
                  Player Experience API, API Gateway, Agent Orchestration
                </div>
              </div>
              <div className="bg-white border rounded-lg p-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm">GET /api/health</span>
                  <span className="text-green-600 text-sm">200 OK (45ms)</span>
                </div>
              </div>
            </div>
          </div>
        );
      case "errors":
        return (
          <div className="p-4">
            <h3 className="text-lg font-semibold mb-4">Error Tracker</h3>
            <div className="space-y-2">
              <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                <div className="text-sm font-medium text-red-800">
                  TypeError: Cannot read property 'id' of undefined
                </div>
                <div className="text-xs text-red-600 mt-1">
                  ComponentTreeViewer.tsx:125
                </div>
              </div>
            </div>
          </div>
        );
      case "console":
        return (
          <div className="p-4">
            <h3 className="text-lg font-semibold mb-4">Console Aggregator</h3>
            <div className="bg-gray-900 text-green-400 p-3 rounded-lg font-mono text-sm">
              <div>[INFO] Debug tools initialized</div>
              <div>[DEBUG] WebSocket connected to ws://localhost:8080</div>
              <div>
                [WARN] Performance baseline not found for patient interface
              </div>
            </div>
          </div>
        );
      case "performance":
        return (
          <div className="p-4">
            <h3 className="text-lg font-semibold mb-4">Performance Profiler</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                <div className="text-sm font-medium">Load Time</div>
                <div className="text-2xl font-bold text-blue-600">1.2s</div>
              </div>
              <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                <div className="text-sm font-medium">Memory Usage</div>
                <div className="text-2xl font-bold text-green-600">45MB</div>
              </div>
            </div>
          </div>
        );
      case "components":
        return (
          <div className="p-4">
            <h3 className="text-lg font-semibold mb-4">
              Component Tree Viewer
            </h3>
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm text-gray-600">
                  React DevTools: Connected
                </span>
                <span className="text-xs text-gray-500">(4 capabilities)</span>
              </div>
              <div className="space-y-1 text-sm">
                <div className="flex items-center space-x-2">
                  <span>📁 App</span>
                  <span className="text-gray-500">(1 render)</span>
                </div>
                <div className="flex items-center space-x-2 ml-4">
                  <span>📄 DebugToolsPanel</span>
                  <span className="text-gray-500">(5 renders)</span>
                </div>
              </div>
            </div>
          </div>
        );
      case "events":
        return (
          <div className="p-4">
            <h3 className="text-lg font-semibold mb-4">Custom Events</h3>
            <div className="space-y-2">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">
                    patient_session_start
                  </span>
                  <span className="text-xs text-gray-500">2 min ago</span>
                </div>
                <div className="text-xs text-blue-600">Patient Interface</div>
              </div>
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">
                    clinical_alert_triggered
                  </span>
                  <span className="text-xs text-gray-500">5 min ago</span>
                </div>
                <div className="text-xs text-yellow-600">
                  Clinical Dashboard
                </div>
              </div>
            </div>
          </div>
        );
      case "baselines":
        return (
          <div className="p-4">
            <h3 className="text-lg font-semibold mb-4">
              Performance Baselines
            </h3>
            <div className="space-y-2">
              <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Patient Interface</span>
                  <span className="text-green-600 text-sm">✓ Healthy</span>
                </div>
                <div className="text-xs text-gray-600">
                  Load time: 150ms (baseline: 145ms)
                </div>
              </div>
              <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">
                    Clinical Dashboard
                  </span>
                  <span className="text-red-600 text-sm">⚠ Regression</span>
                </div>
                <div className="text-xs text-gray-600">
                  Load time: 320ms (baseline: 200ms, +60%)
                </div>
              </div>
            </div>
          </div>
        );
      case "collaborate":
        return (
          <div className="p-4">
            <h3 className="text-lg font-semibold mb-4">Collaborative Debug</h3>
            <div className="text-center py-8">
              <UsersIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 mb-4">No active debug sessions</p>
              <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
                Create Debug Session
              </button>
            </div>
          </div>
        );
      default:
        return (
          <div className="p-4">Select a tab to view debug information</div>
        );
    }
  };

  if (!isOpen) {
    return (
      <div className="fixed bottom-4 right-4 z-50">
        <button
          onClick={() => setIsOpen(true)}
          className="bg-blue-600 text-white p-3 rounded-full shadow-lg hover:bg-blue-700 transition-colors"
        >
          <BugAntIcon className="h-6 w-6" />
        </button>
      </div>
    );
  }

  return (
    <div className="fixed bottom-0 right-0 w-full max-w-4xl h-96 bg-white border-t border-l border-gray-200 shadow-lg z-40">
      {/* Header */}
      <div className="flex items-center justify-between p-3 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center space-x-2">
          <BugAntIcon className="h-5 w-5 text-blue-600" />
          <span className="font-semibold text-gray-900">
            Enhanced Debug Tools
          </span>
          <div className="flex items-center space-x-1">
            <div
              className={`w-2 h-2 rounded-full ${isRecording ? "bg-red-500" : "bg-gray-400"}`}
            />
            <span className="text-xs text-gray-600">
              {isRecording ? "Recording" : "Paused"}
            </span>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => setIsRecording(!isRecording)}
            className="p-1 text-gray-600 hover:text-gray-900"
            title={isRecording ? "Pause recording" : "Start recording"}
          >
            {isRecording ? (
              <PauseIcon className="h-4 w-4" />
            ) : (
              <PlayIcon className="h-4 w-4" />
            )}
          </button>

          <button
            className="p-1 text-gray-600 hover:text-gray-900"
            title="Clear all data"
          >
            <TrashIcon className="h-4 w-4" />
          </button>

          <button
            onClick={() => setIsOpen(false)}
            className="p-1 text-gray-600 hover:text-gray-900"
          >
            <XMarkIcon className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200 bg-gray-50 overflow-x-auto">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center space-x-2 px-4 py-2 text-sm font-medium whitespace-nowrap ${
              activeTab === tab.id
                ? "border-b-2 border-blue-500 text-blue-600 bg-white"
                : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
            }`}
          >
            <tab.icon className="h-4 w-4" />
            <span>{tab.name}</span>
            {tab.count > 0 && (
              <span className="bg-gray-200 text-gray-700 text-xs px-2 py-0.5 rounded-full">
                {tab.count}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto">{renderTabContent()}</div>
    </div>
  );
};
