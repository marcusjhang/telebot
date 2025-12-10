'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { apiClient, type GoalResponse } from '@/lib/api';
import { authLib } from '@/lib/auth';
import GoalForm from '@/components/goals/GoalForm';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { formatDate } from '@/lib/utils';

export default function GoalsPage() {
  const router = useRouter();
  const [currentGoal, setCurrentGoal] = useState<GoalResponse | null>(null);
  const [goalHistory, setGoalHistory] = useState<GoalResponse[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check authentication
    if (!authLib.isAuthenticated()) {
      router.push('/');
      return;
    }

    fetchGoals();
  }, [router]);

  const fetchGoals = async () => {
    try {
      const [currentRes, historyRes] = await Promise.all([
        apiClient.getCurrentGoal(),
        apiClient.getGoalHistory(),
      ]);
      setCurrentGoal(currentRes.data);
      setGoalHistory(historyRes.data);
    } catch (error) {
      console.error('Failed to fetch goals:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading goals...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center gap-4">
            <Link href="/dashboard">
              <Button variant="outline" size="sm">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back
              </Button>
            </Link>
            <h1 className="text-2xl font-bold text-gray-900">Goal Configuration</h1>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8 max-w-2xl">
        <div className="mb-8">
          <GoalForm currentGoal={currentGoal || undefined} onSuccess={fetchGoals} />
        </div>

        {/* Goal History */}
        {goalHistory.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Goal History</CardTitle>
              <CardDescription>
                Your previous goal configurations
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {goalHistory.map((goal) => (
                  <div
                    key={goal.id}
                    className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                  >
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        Effective from {formatDate(goal.effective_from)}
                      </p>
                      <p className="text-xs text-gray-600 mt-1">
                        💧 {goal.daily_water_bottles} bottles • 🍽️{' '}
                        {goal.daily_carb_max_portions} portions • 🏃{' '}
                        {goal.weekly_exercise_sessions} sessions/week
                      </p>
                    </div>
                    {goal.id === currentGoal?.id && (
                      <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded">
                        Current
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
}

