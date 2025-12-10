'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { apiClient, type UserResponse } from '@/lib/api';
import { authLib } from '@/lib/auth';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { ArrowLeft } from 'lucide-react';

export default function SettingsPage() {
  const router = useRouter();
  const [user, setUser] = useState<UserResponse | null>(null);
  const [recapEnabled, setRecapEnabled] = useState(true);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    // Check authentication
    if (!authLib.isAuthenticated()) {
      router.push('/');
      return;
    }

    fetchUser();
  }, [router]);

  const fetchUser = async () => {
    try {
      const { data } = await apiClient.getMe();
      setUser(data);
      setRecapEnabled(data.recap_enabled);
    } catch (error) {
      console.error('Failed to fetch user:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await apiClient.updatePreferences({ recap_enabled: recapEnabled });
      alert('Settings saved successfully! ✅');
      fetchUser();
    } catch (error) {
      console.error('Failed to save settings:', error);
      alert('Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading settings...</p>
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
            <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8 max-w-2xl">
        {/* User Info */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Account Information</CardTitle>
            <CardDescription>Your Telegram account details</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div>
                <Label className="text-gray-600">Name</Label>
                <p className="text-gray-900 font-medium">
                  {user?.first_name} {user?.last_name || ''}
                </p>
              </div>
              {user?.username && (
                <div>
                  <Label className="text-gray-600">Username</Label>
                  <p className="text-gray-900 font-medium">@{user.username}</p>
                </div>
              )}
              <div>
                <Label className="text-gray-600">Telegram ID</Label>
                <p className="text-gray-900 font-medium">{user?.telegram_user_id}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Notification Settings */}
        <Card>
          <CardHeader>
            <CardTitle>Notification Preferences</CardTitle>
            <CardDescription>
              Manage your daily recap notifications
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <Label htmlFor="recap" className="text-base font-medium">
                    Daily Recap
                  </Label>
                  <p className="text-sm text-gray-600 mt-1">
                    Receive a daily summary of your progress at 12:05 AM SGT
                  </p>
                </div>
                <button
                  id="recap"
                  onClick={() => setRecapEnabled(!recapEnabled)}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    recapEnabled ? 'bg-blue-600' : 'bg-gray-300'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      recapEnabled ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>

              <Button onClick={handleSave} disabled={saving} className="w-full">
                {saving ? 'Saving...' : 'Save Settings'}
              </Button>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}

