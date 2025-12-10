'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { CheckCircle2, XCircle } from 'lucide-react';

interface TodayCardProps {
  title: string;
  current: number;
  goal: number;
  emoji: string;
  achieved?: boolean;
  isLimit?: boolean; // For carbs (lower is better)
}

export default function TodayCard({
  title,
  current,
  goal,
  emoji,
  achieved,
  isLimit = false,
}: TodayCardProps) {
  // Determine if goal is met
  const goalMet = achieved !== undefined 
    ? achieved 
    : isLimit 
      ? current <= goal 
      : current >= goal;

  const percentage = Math.min((current / goal) * 100, 100);

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <span className="text-2xl">{emoji}</span>
      </CardHeader>
      <CardContent>
        <div className="flex items-baseline justify-between mb-2">
          <div className="text-2xl font-bold">
            {current.toFixed(1)}
            <span className="text-sm font-normal text-gray-500 ml-1">
              / {goal.toFixed(1)}
            </span>
          </div>
          {goalMet ? (
            <CheckCircle2 className="h-5 w-5 text-green-600" />
          ) : (
            <XCircle className="h-5 w-5 text-gray-400" />
          )}
        </div>
        
        {/* Progress bar */}
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all ${
              goalMet ? 'bg-green-600' : 'bg-blue-600'
            }`}
            style={{ width: `${percentage}%` }}
          />
        </div>
        
        <p className="text-xs text-gray-500 mt-2">
          {isLimit ? (
            current <= goal ? 'Within limit ✓' : 'Over limit'
          ) : (
            goalMet ? 'Goal achieved! 🎉' : `${(goal - current).toFixed(1)} to go`
          )}
        </p>
      </CardContent>
    </Card>
  );
}

