import { useState, useEffect, useCallback } from 'react';
import { useAppDispatch } from '../store/store';
import { addConsoleLog, addErrorEvent } from '../store/slices/debugSlice';
import { webSocketManager, BuildStatusData, LiveReloadData } from '../services/WebSocketManager';

interface LiveReloadStatus {
  isConnected: boolean;
  lastReload: string | null;
  buildStatus: 'idle' | 'building' | 'success' | 'error';
  buildTime: number;
  errors: string[];
  warnings: string[];
  reloadCount: number;
}

export const useLiveReload = () => {
  const dispatch = useAppDispatch();
  const [status, setStatus] = useState<LiveReloadStatus>({
    isConnected: false,
    lastReload: null,
    buildStatus: 'idle',
    buildTime: 0,
    errors: [],
    warnings: [],
    reloadCount: 0,
  });

  const [interfaceStatuses, setInterfaceStatuses] = useState<{
    [interfaceId: string]: LiveReloadStatus;
  }>({});

  useEffect(() => {
    const handleBuildStatus = (buildData: BuildStatusData) => {
      const newStatus: LiveReloadStatus = {
        ...status,
        buildStatus: buildData.status,
        buildTime: buildData.buildTime,
        errors: buildData.errors,
        warnings: buildData.warnings,
      };

      setStatus(newStatus);
      setInterfaceStatuses(prev => ({
        ...prev,
        [buildData.interfaceId]: newStatus,
      }));

      // Log build events
      dispatch(addConsoleLog({
        level: buildData.status === 'error' ? 'error' : 'info',
        message: `Build ${buildData.status} for ${buildData.interfaceId} (${buildData.buildTime}ms)`,
        timestamp: buildData.timestamp,
        source: buildData.interfaceId,
      }));

      // Log build errors
      buildData.errors.forEach(error => {
        dispatch(addErrorEvent({
          message: error,
          context: `Build Error - ${buildData.interfaceId}`,
          timestamp: buildData.timestamp,
          severity: 'high',
        }));
      });

      // Log build warnings
      buildData.warnings.forEach(warning => {
        dispatch(addConsoleLog({
          level: 'warn',
          message: warning,
          timestamp: buildData.timestamp,
          source: buildData.interfaceId,
        }));
      });
    };

    const handleLiveReload = (reloadData: LiveReloadData) => {
      const newStatus: LiveReloadStatus = {
        ...status,
        lastReload: reloadData.timestamp,
        reloadCount: status.reloadCount + 1,
        buildTime: reloadData.buildTime || 0,
      };

      setStatus(newStatus);
      setInterfaceStatuses(prev => ({
        ...prev,
        [reloadData.interfaceId]: {
          ...prev[reloadData.interfaceId],
          lastReload: reloadData.timestamp,
          reloadCount: (prev[reloadData.interfaceId]?.reloadCount || 0) + 1,
        },
      }));

      // Log reload events
      dispatch(addConsoleLog({
        level: reloadData.status === 'failed' ? 'error' : 'info',
        message: `Live reload ${reloadData.status} for ${reloadData.interfaceId}${
          reloadData.changes ? ` (${reloadData.changes.length} changes)` : ''
        }`,
        timestamp: reloadData.timestamp,
        source: reloadData.interfaceId,
      }));

      // Show changes if available
      if (reloadData.changes && reloadData.changes.length > 0) {
        dispatch(addConsoleLog({
          level: 'info',
          message: `Changes detected: ${reloadData.changes.join(', ')}`,
          timestamp: reloadData.timestamp,
          source: reloadData.interfaceId,
        }));
      }
    };

    const handleConnectionStatus = ({ serviceId, status: connectionStatus }: {
      serviceId: string;
      status: string;
    }) => {
      setStatus(prev => ({
        ...prev,
        isConnected: connectionStatus === 'connected',
      }));

      dispatch(addConsoleLog({
        level: connectionStatus === 'connected' ? 'info' : 'warn',
        message: `WebSocket ${connectionStatus} for ${serviceId}`,
        timestamp: new Date().toISOString(),
        source: 'WebSocket Manager',
      }));
    };

    // Subscribe to WebSocket events
    webSocketManager.on('build_status', handleBuildStatus);
    webSocketManager.on('live_reload', handleLiveReload);
    webSocketManager.on('connection_status', handleConnectionStatus);

    // Initial connection status
    setStatus(prev => ({
      ...prev,
      isConnected: webSocketManager.isConnected(),
    }));

    return () => {
      webSocketManager.off('build_status', handleBuildStatus);
      webSocketManager.off('live_reload', handleLiveReload);
      webSocketManager.off('connection_status', handleConnectionStatus);
    };
  }, [dispatch, status]);

  const requestBuildStatus = useCallback(() => {
    webSocketManager.requestBuildStatus();
  }, []);

  const getInterfaceStatus = useCallback((interfaceId: string): LiveReloadStatus => {
    return interfaceStatuses[interfaceId] || {
      isConnected: false,
      lastReload: null,
      buildStatus: 'idle',
      buildTime: 0,
      errors: [],
      warnings: [],
      reloadCount: 0,
    };
  }, [interfaceStatuses]);

  const getAllInterfaceStatuses = useCallback(() => {
    return interfaceStatuses;
  }, [interfaceStatuses]);

  const getOverallStatus = useCallback(() => {
    const statuses = Object.values(interfaceStatuses);
    if (statuses.length === 0) return status;

    const hasErrors = statuses.some(s => s.buildStatus === 'error' || s.errors.length > 0);
    const isBuilding = statuses.some(s => s.buildStatus === 'building');
    const totalReloads = statuses.reduce((sum, s) => sum + s.reloadCount, 0);
    const avgBuildTime = statuses.length > 0
      ? statuses.reduce((sum, s) => sum + s.buildTime, 0) / statuses.length
      : 0;

    return {
      isConnected: status.isConnected,
      lastReload: Math.max(...statuses.map(s => new Date(s.lastReload || 0).getTime())) > 0
        ? new Date(Math.max(...statuses.map(s => new Date(s.lastReload || 0).getTime()))).toISOString()
        : null,
      buildStatus: hasErrors ? 'error' as const : isBuilding ? 'building' as const : 'success' as const,
      buildTime: avgBuildTime,
      errors: statuses.flatMap(s => s.errors),
      warnings: statuses.flatMap(s => s.warnings),
      reloadCount: totalReloads,
    };
  }, [status, interfaceStatuses]);

  return {
    status,
    interfaceStatuses,
    requestBuildStatus,
    getInterfaceStatus,
    getAllInterfaceStatuses,
    getOverallStatus,
    isConnected: status.isConnected,
    hasErrors: status.errors.length > 0 || status.buildStatus === 'error',
    hasWarnings: status.warnings.length > 0,
    isBuilding: status.buildStatus === 'building',
  };
};
