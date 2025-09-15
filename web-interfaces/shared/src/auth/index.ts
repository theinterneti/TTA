/**
 * Unified Authentication Exports
 *
 * This file provides both the new unified authentication system and backward
 * compatibility with existing authentication implementations.
 */

// Primary exports - New Unified Authentication System
export {
  UnifiedAuthProvider,
  useUnifiedAuth,
  UserRole,
  InterfaceType,
  Permission
} from './UnifiedAuthProvider';

export type {
  UnifiedUser,
  UserProfile,
  AuthTokens,
  LoginCredentials,
  SessionInfo,
  UnifiedAuthContextType
} from './UnifiedAuthProvider';

// Backward compatibility exports
export { AuthProvider } from './AuthProvider';
export type { User, AuthContextType } from './AuthProvider';

// Recommended usage for new implementations:
// import { UnifiedAuthProvider as AuthProvider, useUnifiedAuth as useAuth } from '@tta/shared-components';

// For existing implementations during migration:
// import { AuthProvider, useAuth } from '@tta/shared-components';

// Migration helper - Use this to gradually migrate to unified auth
export const createUnifiedAuthProvider = (interfaceType: string) => {
  const mapInterfaceType = (type: string) => {
    switch (type) {
      case 'patient': return InterfaceType.PATIENT;
      case 'clinical': return InterfaceType.CLINICAL;
      case 'admin': return InterfaceType.ADMIN;
      case 'public': return InterfaceType.PUBLIC;
      case 'stakeholder': return InterfaceType.STAKEHOLDER;
      case 'developer': return InterfaceType.DEVELOPER;
      default: return InterfaceType.PATIENT;
    }
  };

  return {
    interfaceType: mapInterfaceType(interfaceType),
    Provider: UnifiedAuthProvider,
    useAuth: useUnifiedAuth
  };
};
