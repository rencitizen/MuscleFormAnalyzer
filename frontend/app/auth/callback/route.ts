import { NextRequest, NextResponse } from 'next/server';
import { OAuthManager } from '@/lib/auth/oauthManager';
import { OAuthErrorHandler } from '@/lib/auth/oauthErrorHandler';

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const code = searchParams.get('code');
  const state = searchParams.get('state');
  const error = searchParams.get('error');
  const errorDescription = searchParams.get('error_description');

  if (error) {
    const errorInfo = OAuthErrorHandler.handleError({
      error,
      error_description: errorDescription || undefined
    });

    console.error('OAuth callback error:', errorInfo);

    const redirectUrl = new URL('/login', request.url);
    redirectUrl.searchParams.set('error', error);
    if (errorDescription) {
      redirectUrl.searchParams.set('error_description', errorDescription);
    }

    return NextResponse.redirect(redirectUrl);
  }

  if (!code) {
    const redirectUrl = new URL('/login', request.url);
    redirectUrl.searchParams.set('error', 'invalid_request');
    redirectUrl.searchParams.set('error_description', 'Authorization code is missing');
    return NextResponse.redirect(redirectUrl);
  }

  try {
    const clientId = process.env.GOOGLE_CLIENT_ID;
    const clientSecret = process.env.GOOGLE_CLIENT_SECRET;
    const nextAuthUrl = process.env.NEXTAUTH_URL;

    if (!clientId || !clientSecret || !nextAuthUrl) {
      throw new Error('Missing required environment variables');
    }

    const oauthManager = new OAuthManager({
      clientId,
      clientSecret,
      redirectUri: `${nextAuthUrl}/auth/callback`,
      scope: 'openid email profile'
    });

    const tokens = await oauthManager.exchangeCodeForTokens(code, state || undefined);

    const response = NextResponse.redirect(new URL('/dashboard', request.url));
    
    response.cookies.set('oauth_access_token', tokens.access_token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: tokens.expires_in
    });

    if (tokens.refresh_token) {
      response.cookies.set('oauth_refresh_token', tokens.refresh_token, {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax',
        maxAge: 60 * 60 * 24 * 30
      });
    }

    return response;
  } catch (error) {
    console.error('Token exchange error:', error);

    const redirectUrl = new URL('/login', request.url);
    redirectUrl.searchParams.set('error', 'token_exchange_failed');
    redirectUrl.searchParams.set('error_description', error instanceof Error ? error.message : 'Unknown error');

    return NextResponse.redirect(redirectUrl);
  }
}