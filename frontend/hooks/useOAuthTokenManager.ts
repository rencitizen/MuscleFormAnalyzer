import { useEffect, useRef, useState, useCallback } from 'react';
import { OAuthManager, OAuthConfig } from '@/lib/auth/oauthManager';
import { TokenInfo } from '@/lib/auth/oauthErrorHandler';

export interface UseOAuthTokenManagerOptions {
  config: OAuthConfig;
  autoRefresh?: boolean;
  refreshBuffer?: number;
  onTokenRefresh?: (tokens: TokenInfo) => void;
  onTokenExpired?: () => void;
  onError?: (error: Error) => void;
}

export interface UseOAuthTokenManagerReturn {
  token: string | null;
  isValidating: boolean;
  isRefreshing: boolean;
  error: Error | null;
  refreshToken: () => Promise<void>;
  clearTokens: () => void;
  validateToken: () => Promise<boolean>;
}

export function useOAuthTokenManager({
  config,
  autoRefresh = true,
  refreshBuffer = 5 * 60 * 1000,
  onTokenRefresh,
  onTokenExpired,
  onError
}: UseOAuthTokenManagerOptions): UseOAuthTokenManagerReturn {
  const [token, setToken] = useState<string | null>(null);
  const [isValidating, setIsValidating] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  
  const managerRef = useRef<OAuthManager>();
  const refreshTimerRef = useRef<ReturnType<typeof setTimeout>>();

  useEffect(() => {
    managerRef.current = new OAuthManager(config);
    
    const initializeToken = async () => {
      const manager = managerRef.current;
      if (!manager) return;

      try {
        setIsValidating(true);
        const tokens = manager.getStoredTokens();
        
        if (tokens) {
          setToken(tokens.access_token);
          
          if (autoRefresh) {
            scheduleTokenRefresh(tokens.expires_at);
          }
        }
      } catch (err) {
        const error = err instanceof Error ? err : new Error('Token initialization failed');
        setError(error);
        onError?.(error);
      } finally {
        setIsValidating(false);
      }
    };

    initializeToken();

    return () => {
      if (refreshTimerRef.current) {
        clearTimeout(refreshTimerRef.current);
      }
    };
  }, [config, autoRefresh, onError]);

  const scheduleTokenRefresh = useCallback((expiresAt: number) => {
    if (!autoRefresh) return;

    if (refreshTimerRef.current) {
      clearTimeout(refreshTimerRef.current);
    }

    const now = Date.now();
    const timeUntilExpiry = expiresAt - now;
    const refreshTime = timeUntilExpiry - refreshBuffer;

    if (refreshTime > 0) {
      console.log(`Scheduling token refresh in ${Math.floor(refreshTime / 1000 / 60)} minutes`);
      
      refreshTimerRef.current = setTimeout(async () => {
        await refreshToken();
      }, refreshTime);
    } else {
      console.log('Token is expired or expiring soon, refreshing immediately');
      refreshToken();
    }
  }, [autoRefresh, refreshBuffer]);

  const refreshToken = useCallback(async () => {
    const manager = managerRef.current;
    if (!manager || isRefreshing) return;

    try {
      setIsRefreshing(true);
      setError(null);

      const tokens = await manager.authenticate();
      
      if (tokens) {
        setToken(tokens.access_token);
        onTokenRefresh?.(tokens);
        
        const storedTokens = manager.getStoredTokens();
        if (storedTokens && autoRefresh) {
          scheduleTokenRefresh(storedTokens.expires_at);
        }
      }
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Token refresh failed');
      setError(error);
      onError?.(error);
      
      if (error.message.includes('invalid_grant') || 
          error.message.includes('Token refresh failed')) {
        onTokenExpired?.();
        clearTokens();
      }
    } finally {
      setIsRefreshing(false);
    }
  }, [autoRefresh, onTokenRefresh, onTokenExpired, onError, scheduleTokenRefresh]);

  const validateToken = useCallback(async (): Promise<boolean> => {
    const manager = managerRef.current;
    if (!manager) return false;

    try {
      setIsValidating(true);
      setError(null);
      
      const isValid = await manager.validateCurrentToken();
      
      if (!isValid) {
        onTokenExpired?.();
      }
      
      return isValid;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Token validation failed');
      setError(error);
      onError?.(error);
      return false;
    } finally {
      setIsValidating(false);
    }
  }, [onTokenExpired, onError]);

  const clearTokens = useCallback(() => {
    const manager = managerRef.current;
    if (!manager) return;

    manager.clearStoredTokens();
    setToken(null);
    setError(null);
    
    if (refreshTimerRef.current) {
      clearTimeout(refreshTimerRef.current);
    }
  }, []);

  return {
    token,
    isValidating,
    isRefreshing,
    error,
    refreshToken,
    clearTokens,
    validateToken
  };
}