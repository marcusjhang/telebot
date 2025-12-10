'use client';

import { useEffect, useRef } from 'react';

interface TelegramLoginButtonProps {
  botUsername: string;
  onAuth: (user: TelegramUser) => void;
  buttonSize?: 'large' | 'medium' | 'small';
  cornerRadius?: number;
  requestAccess?: boolean;
}

export interface TelegramUser {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  photo_url?: string;
  auth_date: number;
  hash: string;
}

declare global {
  interface Window {
    TelegramLoginWidget?: {
      dataOnauth?: (user: TelegramUser) => void;
    };
  }
}

export default function TelegramLoginButton({
  botUsername,
  onAuth,
  buttonSize = 'large',
  cornerRadius,
  requestAccess = true,
}: TelegramLoginButtonProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Set up callback
    window.TelegramLoginWidget = {
      dataOnauth: (user: TelegramUser) => {
        onAuth(user);
      },
    };

    // Load Telegram Widget script
    const script = document.createElement('script');
    script.src = 'https://telegram.org/js/telegram-widget.js?22';
    script.setAttribute('data-telegram-login', botUsername);
    script.setAttribute('data-size', buttonSize);
    if (cornerRadius !== undefined) {
      script.setAttribute('data-radius', cornerRadius.toString());
    }
    script.setAttribute('data-onauth', 'TelegramLoginWidget.dataOnauth(user)');
    script.setAttribute('data-request-access', requestAccess ? 'write' : 'read');
    script.async = true;

    if (containerRef.current) {
      containerRef.current.appendChild(script);
    }

    return () => {
      // Cleanup
      if (containerRef.current) {
        containerRef.current.innerHTML = '';
      }
    };
  }, [botUsername, buttonSize, cornerRadius, requestAccess, onAuth]);

  return <div ref={containerRef} className="flex justify-center" />;
}

