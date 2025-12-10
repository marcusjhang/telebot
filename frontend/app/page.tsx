'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import TelegramLoginButton, { type TelegramUser } from '@/components/auth/TelegramLoginButton';
import { authLib } from '@/lib/auth';
import api from '@/lib/api';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // If already authenticated, redirect to dashboard
    if (authLib.isAuthenticated()) {
      router.push('/dashboard');
    }
  }, [router]);

  const handleTelegramAuth = async (user: TelegramUser) => {
    try {
      // Send Telegram auth data to backend
      const response = await api.post('/api/v1/auth/telegram', user);
      const { access_token } = response.data;

      // Store JWT token
      authLib.setToken(access_token);

      // Redirect to dashboard
      router.push('/dashboard');
    } catch (error) {
      console.error('Authentication failed:', error);
      alert('Authentication failed. Please try again.');
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <main className="flex flex-col items-center justify-center p-8 bg-white rounded-2xl shadow-xl max-w-md w-full mx-4">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            💧 Health Tracker
          </h1>
          <p className="text-gray-600">
            Track your water, carbs, and exercise goals
          </p>
        </div>

        <div className="w-full space-y-6">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h2 className="font-semibold text-blue-900 mb-2">Features:</h2>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>💧 Track daily water intake</li>
              <li>🍽️ Monitor carb consumption</li>
              <li>🏃 Log exercise sessions</li>
              <li>📊 View progress and streaks</li>
              <li>🔔 Get daily recap notifications</li>
            </ul>
          </div>

          <div className="text-center">
            <p className="text-sm text-gray-600 mb-4">
              Sign in with Telegram to get started
            </p>
            <TelegramLoginButton
              botUsername={process.env.NEXT_PUBLIC_BOT_USERNAME || 'your_bot'}
              onAuth={handleTelegramAuth}
              buttonSize="large"
            />
          </div>

          <p className="text-xs text-gray-500 text-center">
            By signing in, you agree to use this service for tracking your health goals.
          </p>
        </div>
      </main>
    </div>
  );
}
