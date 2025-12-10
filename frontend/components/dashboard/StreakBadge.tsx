'use client';

import { Flame } from 'lucide-react';

interface StreakBadgeProps {
  label: string;
  streak: number;
  emoji: string;
}

export default function StreakBadge({ label, streak, emoji }: StreakBadgeProps) {
  return (
    <div className="flex items-center gap-2 px-4 py-2 bg-orange-50 border border-orange-200 rounded-lg">
      <span className="text-xl">{emoji}</span>
      <div className="flex-1">
        <p className="text-xs text-gray-600">{label}</p>
        <p className="text-sm font-semibold text-gray-900">
          {streak} {streak === 1 ? 'day' : 'days'}
        </p>
      </div>
      {streak > 0 && <Flame className="h-5 w-5 text-orange-500" />}
    </div>
  );
}

