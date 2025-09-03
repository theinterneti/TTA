import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  ChevronRightIcon,
  ChevronDownIcon,
  CpuChipIcon,
  ClockIcon,
  EyeIcon,
  InformationCircleIcon,
  WrenchScrewdriverIcon,
  LinkIcon
} from '@heroicons/react/24/outline';
import { useAppSelector } from '../../store/store';
import { reactDevToolsBridge } from '../../services/ReactDevToolsBridge';

interface ComponentNode {
  id: string;
  name: string;
  type: 'component' | 'hook' | 'context';
  children: ComponentNode[];
  props?: any;
  state?: any;
  renderCount: number;
  averageRenderTime: number;
  lastRenderTime: string;
  isExpanded?: boolean;
}

export const ComponentTreeViewer: React.FC = () => {
  const { componentRenderInfo } = useAppSelector(state => state.debug);
  const [selectedComponent, setSelectedComponent] = useState<string | null>(null);
  const [componentTree, setComponentTree] = useState<ComponentNode[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [isDevToolsConnected, setIsDevToolsConnected] = useState(false);
  const [devToolsCapabilities, setDevToolsCapabilities] = useState<string[]>([]);
  const [useDevToolsData, setUseDevToolsData] = useState(false);

  // Initialize React DevTools integration
  useEffect(() => {
    // Check DevTools connection status
    setIsDevToolsConnected(reactDevToolsBridge.isDevToolsConnected());
    setDevToolsCapabilities(reactDevToolsBridge.getDevToolsCapabilities());

    // Set up DevTools event listeners
    const handleDevToolsConnected = () => {
      setIsDevToolsConnected(true);
      setDevToolsCapabilities(reactDevToolsBridge.getDevToolsCapabilities());
    };

    const handleComponentTreeUpdated = (data: any) => {
      if (useDevToolsData) {
        const devToolsTree = convertDevToolsTreeToComponentNodes(data.tree);
        setComponentTree(devToolsTree);
      }
    };

    const handleComponentSelected = (data: any) => {
      setSelectedComponent(data.componentId);
    };

    reactDevToolsBridge.on('devtools_connected', handleDevToolsConnected);
    reactDevToolsBridge.on('component_tree_updated', handleComponentTreeUpdated);
    reactDevToolsBridge.on('component_selected', handleComponentSelected);

    // Initial tree setup
    if (useDevToolsData && isDevToolsConnected) {
      const devToolsTree = reactDevToolsBridge.getComponentTree();
      if (devToolsTree.length > 0) {
        setComponentTree(convertDevToolsTreeToComponentNodes(devToolsTree));
      } else {
        // Fallback to mock data
        setComponentTree(getMockComponentTree());
      }
    } else {
      setComponentTree(getMockComponentTree());
    }

    return () => {
      reactDevToolsBridge.off('devtools_connected', handleDevToolsConnected);
      reactDevToolsBridge.off('component_tree_updated', handleComponentTreeUpdated);
      reactDevToolsBridge.off('component_selected', handleComponentSelected);
    };
  }, [useDevToolsData, isDevToolsConnected]);

  const convertDevToolsTreeToComponentNodes = (devToolsNodes: any[]): ComponentNode[] => {
    return devToolsNodes.map(node => ({
      id: node.id,
      name: node.displayName,
      type: 'component',
      renderCount: node.renderCount,
      averageRenderTime: node.actualDuration || 0,
      lastRenderTime: new Date(node.lastRenderTime).toISOString(),
      isExpanded: true,
      children: convertDevToolsTreeToComponentNodes(node.children || [])
    }));
  };

  const getMockComponentTree = (): ComponentNode[] => [
      {
        id: 'app',
        name: 'App',
        type: 'component',
        renderCount: 1,
        averageRenderTime: 15.2,
        lastRenderTime: new Date().toISOString(),
        isExpanded: true,
        children: [
          {
            id: 'router',
            name: 'BrowserRouter',
            type: 'component',
            renderCount: 1,
            averageRenderTime: 2.1,
            lastRenderTime: new Date().toISOString(),
            isExpanded: true,
            children: [
              {
                id: 'layout',
                name: 'DeveloperLayout',
                type: 'component',
                renderCount: 3,
                averageRenderTime: 8.7,
                lastRenderTime: new Date().toISOString(),
                isExpanded: true,
                children: [
                  {
                    id: 'dashboard',
                    name: 'Dashboard',
                    type: 'component',
                    renderCount: 5,
                    averageRenderTime: 12.3,
                    lastRenderTime: new Date().toISOString(),
                    children: [],
                  },
                  {
                    id: 'interface-hub',
                    name: 'InterfaceHub',
                    type: 'component',
                    renderCount: 2,
                    averageRenderTime: 18.9,
                    lastRenderTime: new Date().toISOString(),
                    children: [
                      {
                        id: 'interface-card',
                        name: 'InterfaceCard',
                        type: 'component',
                        renderCount: 14,
                        averageRenderTime: 3.2,
                        lastRenderTime: new Date().toISOString(),
                        children: [],
                      },
                    ],
                  },
                ],
              },
            ],
          },
          {
            id: 'debug-panel',
            name: 'DebugToolsPanel',
            type: 'component',
            renderCount: 8,
            averageRenderTime: 6.4,
            lastRenderTime: new Date().toISOString(),
            isExpanded: true,
            children: [
              {
                id: 'network-monitor',
                name: 'NetworkMonitor',
                type: 'component',
                renderCount: 12,
                averageRenderTime: 4.1,
                lastRenderTime: new Date().toISOString(),
                children: [],
              },
              {
                id: 'component-tree',
                name: 'ComponentTreeViewer',
                type: 'component',
                renderCount: 6,
                averageRenderTime: 2.8,
                lastRenderTime: new Date().toISOString(),
                children: [],
              },
            ],
          },
        ],
      },
    ];

    return mockTree;
  };

  const toggleExpanded = (nodeId: string) => {
    const updateNode = (nodes: ComponentNode[]): ComponentNode[] => {
      return nodes.map(node => {
        if (node.id === nodeId) {
          return { ...node, isExpanded: !node.isExpanded };
        }
        if (node.children.length > 0) {
          return { ...node, children: updateNode(node.children) };
        }
        return node;
      });
    };

    setComponentTree(updateNode(componentTree));
  };

  const renderComponentNode = (node: ComponentNode, depth: number = 0) => {
    const hasChildren = node.children.length > 0;
    const isSelected = selectedComponent === node.id;
    const matchesSearch = !searchTerm || node.name.toLowerCase().includes(searchTerm.toLowerCase());

    if (!matchesSearch) return null;

    return (
      <div key={node.id}>
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className={`flex items-center space-x-2 py-1 px-2 hover:bg-gray-100 cursor-pointer ${
            isSelected ? 'bg-blue-50 border-l-2 border-blue-500' : ''
          }`}
          style={{ paddingLeft: `${depth * 20 + 8}px` }}
          onClick={() => setSelectedComponent(node.id)}
        >
          {hasChildren ? (
            <button
              onClick={(e) => {
                e.stopPropagation();
                toggleExpanded(node.id);
              }}
              className="p-0.5 hover:bg-gray-200 rounded"
            >
              {node.isExpanded ? (
                <ChevronDownIcon className="h-3 w-3 text-gray-500" />
              ) : (
                <ChevronRightIcon className="h-3 w-3 text-gray-500" />
              )}
            </button>
          ) : (
            <div className="w-4" />
          )}

          <div className={`p-1 rounded ${
            node.type === 'component' ? 'bg-blue-100' :
            node.type === 'hook' ? 'bg-green-100' :
            'bg-purple-100'
          }`}>
            <CpuChipIcon className={`h-3 w-3 ${
              node.type === 'component' ? 'text-blue-600' :
              node.type === 'hook' ? 'text-green-600' :
              'text-purple-600'
            }`} />
          </div>

          <span className="text-sm font-mono text-gray-900">{node.name}</span>

          <div className="flex items-center space-x-2 text-xs text-gray-500">
            <span>{node.renderCount} renders</span>
            <span>•</span>
            <span>{node.averageRenderTime.toFixed(1)}ms avg</span>
          </div>
        </motion.div>

        {hasChildren && node.isExpanded && (
          <div>
            {node.children.map(child => renderComponentNode(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  const selectedNode = componentTree.find(node => findNodeById(node, selectedComponent));

  function findNodeById(node: ComponentNode, id: string | null): ComponentNode | null {
    if (node.id === id) return node;
    for (const child of node.children) {
      const found = findNodeById(child, id);
      if (found) return found;
    }
    return null;
  }

  const selectedComponentData = selectedComponent ? findNodeById(componentTree[0], selectedComponent) : null;

  return (
    <div className="h-full flex">
      {/* Component Tree */}
      <div className="flex-1 flex flex-col">
        {/* Search and DevTools Integration */}
        <div className="p-4 border-b border-gray-200 bg-gray-50">
          <div className="flex items-center space-x-4 mb-3">
            <div className="flex-1 relative">
              <input
                type="text"
                placeholder="Search components..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <EyeIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            </div>

            {/* DevTools Integration Toggle */}
            <div className="flex items-center space-x-2">
              <label className="flex items-center space-x-2 text-sm">
                <input
                  type="checkbox"
                  checked={useDevToolsData}
                  onChange={(e) => setUseDevToolsData(e.target.checked)}
                  disabled={!isDevToolsConnected}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className={isDevToolsConnected ? 'text-gray-700' : 'text-gray-400'}>
                  Use DevTools Data
                </span>
              </label>
            </div>
          </div>

          {/* DevTools Status */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 text-sm">
              <div className={`w-2 h-2 rounded-full ${isDevToolsConnected ? 'bg-green-500' : 'bg-red-500'}`} />
              <span className="text-gray-600">
                React DevTools: {isDevToolsConnected ? 'Connected' : 'Not Available'}
              </span>
              {isDevToolsConnected && (
                <span className="text-xs text-gray-500">
                  ({devToolsCapabilities.length} capabilities)
                </span>
              )}
            </div>

            {isDevToolsConnected && (
              <button
                onClick={() => {
                  const devToolsTree = reactDevToolsBridge.getComponentTree();
                  if (devToolsTree.length > 0) {
                    setComponentTree(convertDevToolsTreeToComponentNodes(devToolsTree));
                  }
                }}
                className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors"
              >
                Refresh from DevTools
              </button>
            )}
          </div>
        </div>

        {/* Tree View */}
        <div className="flex-1 overflow-auto">
          {componentTree.map(node => renderComponentNode(node))}
        </div>
      </div>

      {/* Component Details */}
      {selectedComponentData && (
        <div className="w-96 border-l border-gray-200 bg-gray-50 overflow-auto">
          <div className="p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-900">Component Details</h3>
              <button
                onClick={() => setSelectedComponent(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ×
              </button>
            </div>

            <div className="space-y-4">
              {/* Basic Info */}
              <div>
                <h4 className="font-medium text-gray-700 mb-2">General</h4>
                <div className="space-y-1 text-sm">
                  <div><span className="text-gray-600">Name:</span> {selectedComponentData.name}</div>
                  <div><span className="text-gray-600">Type:</span> {selectedComponentData.type}</div>
                  <div><span className="text-gray-600">Render Count:</span> {selectedComponentData.renderCount}</div>
                  <div><span className="text-gray-600">Average Render Time:</span> {selectedComponentData.averageRenderTime.toFixed(1)}ms</div>
                  <div><span className="text-gray-600">Last Render:</span> {new Date(selectedComponentData.lastRenderTime).toLocaleString()}</div>
                </div>
              </div>

              {/* Performance Metrics */}
              <div>
                <h4 className="font-medium text-gray-700 mb-2">Performance</h4>
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Render Frequency</span>
                    <span className={`font-medium ${
                      selectedComponentData.renderCount > 10 ? 'text-red-600' :
                      selectedComponentData.renderCount > 5 ? 'text-yellow-600' :
                      'text-green-600'
                    }`}>
                      {selectedComponentData.renderCount > 10 ? 'High' :
                       selectedComponentData.renderCount > 5 ? 'Medium' : 'Low'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Render Performance</span>
                    <span className={`font-medium ${
                      selectedComponentData.averageRenderTime > 15 ? 'text-red-600' :
                      selectedComponentData.averageRenderTime > 8 ? 'text-yellow-600' :
                      'text-green-600'
                    }`}>
                      {selectedComponentData.averageRenderTime > 15 ? 'Slow' :
                       selectedComponentData.averageRenderTime > 8 ? 'Medium' : 'Fast'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Props */}
              {selectedComponentData.props && (
                <div>
                  <h4 className="font-medium text-gray-700 mb-2">Props</h4>
                  <pre className="text-xs bg-white p-2 rounded border overflow-auto max-h-32">
                    {JSON.stringify(selectedComponentData.props, null, 2)}
                  </pre>
                </div>
              )}

              {/* State */}
              {selectedComponentData.state && (
                <div>
                  <h4 className="font-medium text-gray-700 mb-2">State</h4>
                  <pre className="text-xs bg-white p-2 rounded border overflow-auto max-h-32">
                    {JSON.stringify(selectedComponentData.state, null, 2)}
                  </pre>
                </div>
              )}

              {/* Children Info */}
              {selectedComponentData.children.length > 0 && (
                <div>
                  <h4 className="font-medium text-gray-700 mb-2">Children ({selectedComponentData.children.length})</h4>
                  <div className="space-y-1">
                    {selectedComponentData.children.map(child => (
                      <div
                        key={child.id}
                        className="flex items-center space-x-2 text-sm p-2 bg-white rounded border cursor-pointer hover:bg-gray-50"
                        onClick={() => setSelectedComponent(child.id)}
                      >
                        <CpuChipIcon className="h-3 w-3 text-blue-600" />
                        <span>{child.name}</span>
                        <span className="text-gray-500">({child.renderCount} renders)</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Optimization Suggestions */}
              <div>
                <h4 className="font-medium text-gray-700 mb-2">Optimization Suggestions</h4>
                <div className="space-y-2">
                  {selectedComponentData.renderCount > 10 && (
                    <div className="flex items-start space-x-2 p-2 bg-yellow-50 rounded border border-yellow-200">
                      <InformationCircleIcon className="h-4 w-4 text-yellow-600 mt-0.5" />
                      <div className="text-sm">
                        <div className="font-medium text-yellow-800">High Render Count</div>
                        <div className="text-yellow-700">Consider using React.memo() or useMemo() to prevent unnecessary re-renders.</div>
                      </div>
                    </div>
                  )}
                  {selectedComponentData.averageRenderTime > 15 && (
                    <div className="flex items-start space-x-2 p-2 bg-red-50 rounded border border-red-200">
                      <ClockIcon className="h-4 w-4 text-red-600 mt-0.5" />
                      <div className="text-sm">
                        <div className="font-medium text-red-800">Slow Render Time</div>
                        <div className="text-red-700">This component takes longer than average to render. Consider optimizing heavy computations.</div>
                      </div>
                    </div>
                  )}
                  {selectedComponentData.renderCount <= 5 && selectedComponentData.averageRenderTime <= 8 && (
                    <div className="flex items-start space-x-2 p-2 bg-green-50 rounded border border-green-200">
                      <InformationCircleIcon className="h-4 w-4 text-green-600 mt-0.5" />
                      <div className="text-sm">
                        <div className="font-medium text-green-800">Well Optimized</div>
                        <div className="text-green-700">This component has good performance characteristics.</div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
