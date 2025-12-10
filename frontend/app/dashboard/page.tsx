'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { apiClient, type TodayProgress } from '@/lib/api';
import { authLib } from '@/lib/auth';
import TodayCard from '@/components/dashboard/TodayCard';
import StreakBadge from '@/components/dashboard/StreakBadge';
import { Button } from '@/components/ui/button';
import { Settings, TrendingUp, Target } from 'lucide-react';

export default function DashboardPage() {
  const router = useRouter();
  const [progress, setProgress] = useState<TodayProgress | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Check authentication
    if (!authLib.isAuthenticated()) {
      router.push('/');
      return;
    }

    async function fetchProgress() {
      try {
        const { data } = await apiClient.getTodayProgress();
        setProgress(data);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to fetch progress');
      } finally {
        setLoading(false);
      }
    }

    fetchProgress();
  }, [router]);

  const handleLogout = () => {
    authLib.removeToken();
    router.push('/');
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your progress...</p>
        </div>
      </div>
    );
  }

  if (error || !progress) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error || 'Failed to load data'}</p>
          <Button onClick={() => window.location.reload()}>Retry</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-900">💧 Health Tracker</h1>
            <div className="flex items-center gap-2">
              <Link href="/goals">
                <Button variant="outline" size="sm">
                  <Target className="h-4 w-4 mr-2" />
                  Goals
                </Button>
              </Link>
              <Link href="/settings">
                <Button variant="outline" size="sm">
                  <Settings className="h-4 w-4 mr-2" />
                  Settings
                </Button>
              </Link>
              <Button variant="outline" size="sm" onClick={handleLogout}>
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-1">
            Today's Progress
          </h2>
          <p className="text-sm text-gray-600">{progress.date}</p>
        </div>

        {/* Today's Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <TodayCard
            title="Water"
            current={progress.water.current}
            goal={progress.water.goal}
            emoji="💧"
            achieved={progress.water.achieved}
          />
          <TodayCard
            title="Carbs"
            current={progress.carbs.current}
            goal={progress.carbs.goal}
            emoji="🍽️"
            achieved={progress.carbs.within_limit}
            isLimit={true}
          />
          <TodayCard
            title="Exercise (This Week)"
            current={progress.exercise.weekly_total}
            goal={progress.exercise.weekly_goal}
            emoji="🏃"
          />
        </div>

        {/* Streaks */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            🔥 Your Streaks
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <StreakBadge
              label="Water Streak"
              streak={progress.streaks.water_streak}
              emoji="💧"
            />
            <StreakBadge
              label="Carbs Streak"
              streak={progress.streaks.carbs_streak}
              emoji="🍽️"
            />
            <StreakBadge
              label="Exercise Streak"
              streak={progress.streaks.exercise_streak}
              emoji="🏃"
            />
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="font-semibold text-blue-900 mb-2">
            📱 Use the Telegram Bot
          </h3>
          <p className="text-sm text-blue-800">
            Log your water, carbs, and exercise sessions quickly using the Telegram bot.
            Just open Telegram and start chatting with your bot!
          </p>
        </div>
      </main>
    </div>
  );
}

