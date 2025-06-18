import { describe, it, expect, vi, beforeEach } from 'vitest';
import { OAuthError, handleOAuthError, createErrorResponse } from '@/lib/auth/oauthErrorHandler';

// Mock console methods
const mockConsoleError = vi.spyOn(console, 'error').mockImplementation(() => {});
const mockConsoleWarn = vi.spyOn(console, 'warn').mockImplementation(() => {});

describe('OAuthErrorHandler', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('OAuthError', () => {
    it('should create an error with correct properties', () => {
      const error = new OAuthError('invalid_request', 'Invalid request parameters');
      
      expect(error).toBeInstanceOf(Error);
      expect(error).toBeInstanceOf(OAuthError);
      expect(error.code).toBe('invalid_request');
      expect(error.message).toBe('Invalid request parameters');
      expect(error.name).toBe('OAuthError');
    });

    it('should include details if provided', () => {
      const details = { param: 'client_id', value: null };
      const error = new OAuthError('invalid_request', 'Missing client_id', details);
      
      expect(error.details).toEqual(details);
    });
  });

  describe('handleOAuthError', () => {
    it('should handle OAuthError instances', () => {
      const oauthError = new OAuthError('access_denied', 'User denied access');
      const result = handleOAuthError(oauthError);

      expect(result).toEqual({
        error: 'access_denied',
        error_description: 'User denied access',
        details: undefined
      });
      expect(mockConsoleError).toHaveBeenCalledWith('[OAuth Error]', expect.any(Object));
    });

    it('should handle standard Error instances', () => {
      const standardError = new Error('Network error');
      const result = handleOAuthError(standardError);

      expect(result).toEqual({
        error: 'unknown_error',
        error_description: 'Network error'
      });
      expect(mockConsoleError).toHaveBeenCalledWith('[OAuth Error]', expect.any(Object));
    });

    it('should handle non-Error objects', () => {
      const result = handleOAuthError('String error');

      expect(result).toEqual({
        error: 'unknown_error',
        error_description: 'An unknown error occurred'
      });
      expect(mockConsoleError).toHaveBeenCalledWith('[OAuth Error]', expect.any(Object));
    });

    it('should handle null/undefined errors', () => {
      const result = handleOAuthError(null);

      expect(result).toEqual({
        error: 'unknown_error',
        error_description: 'An unknown error occurred'
      });
    });

    it('should handle specific error codes with appropriate messages', () => {
      const testCases = [
        { code: 'invalid_request', expectedLog: true },
        { code: 'unauthorized_client', expectedLog: true },
        { code: 'access_denied', expectedLog: false }, // User action, less severe
        { code: 'server_error', expectedLog: true },
        { code: 'temporarily_unavailable', expectedLog: false } // Temporary, less severe
      ];

      testCases.forEach(({ code, expectedLog }) => {
        vi.clearAllMocks();
        const error = new OAuthError(code, `Error: ${code}`);
        handleOAuthError(error);

        if (expectedLog) {
          expect(mockConsoleError).toHaveBeenCalled();
        } else {
          expect(mockConsoleWarn).toHaveBeenCalled();
        }
      });
    });
  });

  describe('createErrorResponse', () => {
    it('should create error response with all fields', () => {
      const response = createErrorResponse(
        'invalid_grant',
        'The provided authorization code is invalid',
        'https://example.com/error'
      );

      expect(response).toEqual({
        error: 'invalid_grant',
        error_description: 'The provided authorization code is invalid',
        error_uri: 'https://example.com/error'
      });
    });

    it('should create error response without optional fields', () => {
      const response = createErrorResponse('invalid_request');

      expect(response).toEqual({
        error: 'invalid_request'
      });
    });

    it('should filter out undefined values', () => {
      const response = createErrorResponse('server_error', undefined, undefined);

      expect(response).toEqual({
        error: 'server_error'
      });
      expect(response).not.toHaveProperty('error_description');
      expect(response).not.toHaveProperty('error_uri');
    });
  });

  describe('Error recovery suggestions', () => {
    it('should provide recovery suggestions for known errors', () => {
      const errorCodes = [
        'invalid_request',
        'invalid_client',
        'invalid_grant',
        'unauthorized_client',
        'unsupported_response_type',
        'invalid_scope',
        'server_error',
        'temporarily_unavailable'
      ];

      errorCodes.forEach(code => {
        const error = new OAuthError(code, 'Test error');
        const result = handleOAuthError(error);
        
        // Verify that error is handled without throwing
        expect(result).toHaveProperty('error', code);
        expect(result).toHaveProperty('error_description');
      });
    });
  });
});