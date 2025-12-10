'use client';

import { useState } from 'react';
import { apiClient, type GoalInput, type GoalResponse } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

interface GoalFormProps {
  currentGoal?: GoalResponse;
  onSuccess?: () => void;
}

export default function GoalForm({ currentGoal, onSuccess }: GoalFormProps) {
  const [goals, setGoals] = useState<GoalInput>({
    daily_water_bottles: currentGoal?.daily_water_bottles || 3,
    daily_carb_max_portions: currentGoal?.daily_carb_max_portions || 4,
    weekly_exercise_sessions: currentGoal?.weekly_exercise_sessions || 5,
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError(null);

    try {
      await apiClient.createGoal(goals);
      alert('Goals updated successfully! 🎉');
      onSuccess?.();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update goals');
    } finally {
      setSaving(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Set Your Goals</CardTitle>
        <CardDescription>
          Configure your daily and weekly targets. Changes take effect immediately.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="water">💧 Daily Water Goal (bottles)</Label>
            <Input
              id="water"
              type="number"
              step="0.5"
              min="0.5"
              max="20"
              value={goals.daily_water_bottles}
              onChange={(e) =>
                setGoals({ ...goals, daily_water_bottles: parseFloat(e.target.value) })
              }
              required
            />
            <p className="text-xs text-gray-500">
              How many bottles of water you aim to drink daily
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="carbs">🍽️ Daily Carb Limit (portions)</Label>
            <Input
              id="carbs"
              type="number"
              step="0.5"
              min="0.5"
              max="20"
              value={goals.daily_carb_max_portions}
              onChange={(e) =>
                setGoals({ ...goals, daily_carb_max_portions: parseFloat(e.target.value) })
              }
              required
            />
            <p className="text-xs text-gray-500">
              Maximum carb portions per day (Meal = 2 portions, Snack = 1 portion)
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="exercise">🏃 Weekly Exercise Goal (sessions)</Label>
            <Input
              id="exercise"
              type="number"
              min="1"
              max="30"
              value={goals.weekly_exercise_sessions}
              onChange={(e) =>
                setGoals({ ...goals, weekly_exercise_sessions: parseInt(e.target.value) })
              }
              required
            />
            <p className="text-xs text-gray-500">
              Number of exercise sessions you aim to complete each week
            </p>
          </div>

          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-md text-sm text-red-600">
              {error}
            </div>
          )}

          <Button type="submit" disabled={saving} className="w-full">
            {saving ? 'Saving...' : 'Save Goals'}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}

