import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import Card, { CardBody, CardHeader, CardTitle } from '../common/Card';
import Button from '../common/Button';
import Input from '../common/Input';
import LoadingSpinner from '../common/LoadingSpinner';


interface UserProfileProps {
  onClose?: () => void;
}

export const UserProfile: React.FC<UserProfileProps> = ({ onClose }) => {
  const { user, updatePreferences, changePassword, logout } = useAuth();
  
  const [isLoading, setIsLoading] = useState(false);
  const [notification, setNotification] = useState<{
    type: 'success' | 'error';
    message: string;
  } | null>(null);

  // Preferences form
  const [preferences, setPreferences] = useState({
    theme: user?.preferences?.theme || 'dark',
    default_expansion: user?.preferences?.default_expansion || 0,
    items_per_page: user?.preferences?.items_per_page || 25,
  });

  // Password change form
  const [passwordForm, setPasswordForm] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });
  const [showPasswordForm, setShowPasswordForm] = useState(false);

  const handlePreferencesUpdate = async () => {
    setIsLoading(true);
    try {
      await updatePreferences(preferences);
      setNotification({
        type: 'success',
        message: 'Preferences updated successfully!',
      });
    } catch (error: any) {
      setNotification({
        type: 'error',
        message: error.message || 'Failed to update preferences',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handlePasswordChange = async () => {
    if (passwordForm.newPassword !== passwordForm.confirmPassword) {
      setNotification({
        type: 'error',
        message: 'New passwords do not match',
      });
      return;
    }

    if (passwordForm.newPassword.length < 8) {
      setNotification({
        type: 'error',
        message: 'New password must be at least 8 characters',
      });
      return;
    }

    setIsLoading(true);
    try {
      await changePassword(passwordForm.currentPassword, passwordForm.newPassword);
      setNotification({
        type: 'success',
        message: 'Password changed successfully!',
      });
      setPasswordForm({
        currentPassword: '',
        newPassword: '',
        confirmPassword: '',
      });
      setShowPasswordForm(false);
    } catch (error: any) {
      setNotification({
        type: 'error',
        message: error.message || 'Failed to change password',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    if (onClose) {
      onClose();
    }
  };

  if (!user) {
    return (
      <div className="text-center py-8">
        <p className="text-muted-foreground">User not found</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Notification */}
      {notification && (
        <div className={`p-4 rounded-md border ${
          notification.type === 'success' 
            ? 'bg-green-50 border-green-200 text-green-800' 
            : 'bg-red-50 border-red-200 text-red-800'
        }`}>
          <div className="flex items-center justify-between">
            <p className="text-sm font-medium">{notification.message}</p>
            <button
              onClick={() => setNotification(null)}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
      )}

      {/* User Info */}
      <Card>
        <CardHeader>
          <CardTitle>Account Information</CardTitle>
        </CardHeader>
        <CardBody>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-muted-foreground mb-1">
                Email Address
              </label>
              <p className="text-foreground">{user.email}</p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-muted-foreground mb-1">
                Account Type
              </label>
              <p className="text-foreground">
                {user.is_admin ? 'Administrator' : 'User'}
              </p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-muted-foreground mb-1">
                Member Since
              </label>
              <p className="text-foreground">
                {new Date(user.created_at).toLocaleDateString()}
              </p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-muted-foreground mb-1">
                Last Login
              </label>
              <p className="text-foreground">
                {new Date(user.last_login).toLocaleString()}
              </p>
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Preferences */}
      <Card>
        <CardHeader>
          <CardTitle>Preferences</CardTitle>
        </CardHeader>
        <CardBody>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-muted-foreground mb-2">
                Theme
              </label>
              <select
                value={preferences.theme}
                onChange={(e) => setPreferences(prev => ({ ...prev, theme: e.target.value }))}
                className="w-full px-3 py-2 bg-background border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option value="dark">Dark</option>
                <option value="light">Light</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-muted-foreground mb-2">
                Default Expansion
              </label>
              <select
                value={preferences.default_expansion}
                onChange={(e) => setPreferences(prev => ({ ...prev, default_expansion: parseInt(e.target.value) }))}
                className="w-full px-3 py-2 bg-background border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option value={0}>Classic</option>
                <option value={1}>Kunark</option>
                <option value={2}>Velious</option>
                <option value={3}>Luclin</option>
                <option value={4}>Planes of Power</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-muted-foreground mb-2">
                Items Per Page
              </label>
              <select
                value={preferences.items_per_page}
                onChange={(e) => setPreferences(prev => ({ ...prev, items_per_page: parseInt(e.target.value) }))}
                className="w-full px-3 py-2 bg-background border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option value={10}>10</option>
                <option value={25}>25</option>
                <option value={50}>50</option>
                <option value={100}>100</option>
              </select>
            </div>
            
            <Button
              onClick={handlePreferencesUpdate}
              disabled={isLoading}
              variant="primary"
            >
              {isLoading ? (
                <div className="flex items-center space-x-2">
                  <LoadingSpinner size="sm" />
                  <span>Updating...</span>
                </div>
              ) : (
                'Update Preferences'
              )}
            </Button>
          </div>
        </CardBody>
      </Card>

      {/* Password Change */}
      <Card>
        <CardHeader>
          <CardTitle>Change Password</CardTitle>
        </CardHeader>
        <CardBody>
          {!showPasswordForm ? (
            <Button
              onClick={() => setShowPasswordForm(true)}
              variant="outline"
            >
              Change Password
            </Button>
          ) : (
            <div className="space-y-4">
              <Input
                label="Current Password"
                type="password"
                value={passwordForm.currentPassword}
                onChange={(e) => setPasswordForm(prev => ({ ...prev, currentPassword: e.target.value }))}
                placeholder="Enter current password"
                disabled={isLoading}
              />
              
              <Input
                label="New Password"
                type="password"
                value={passwordForm.newPassword}
                onChange={(e) => setPasswordForm(prev => ({ ...prev, newPassword: e.target.value }))}
                placeholder="Enter new password"
                disabled={isLoading}
              />
              
              <Input
                label="Confirm New Password"
                type="password"
                value={passwordForm.confirmPassword}
                onChange={(e) => setPasswordForm(prev => ({ ...prev, confirmPassword: e.target.value }))}
                placeholder="Confirm new password"
                disabled={isLoading}
              />
              
              <div className="flex space-x-2">
                <Button
                  onClick={handlePasswordChange}
                  disabled={isLoading}
                  variant="primary"
                >
                  {isLoading ? (
                    <div className="flex items-center space-x-2">
                      <LoadingSpinner size="sm" />
                      <span>Changing...</span>
                    </div>
                  ) : (
                    'Change Password'
                  )}
                </Button>
                
                <Button
                  onClick={() => {
                    setShowPasswordForm(false);
                    setPasswordForm({
                      currentPassword: '',
                      newPassword: '',
                      confirmPassword: '',
                    });
                  }}
                  variant="outline"
                  disabled={isLoading}
                >
                  Cancel
                </Button>
              </div>
            </div>
          )}
        </CardBody>
      </Card>

      {/* Logout */}
      <Card>
        <CardBody>
          <Button
            onClick={handleLogout}
            variant="danger"
            className="w-full"
          >
            Sign Out
          </Button>
        </CardBody>
      </Card>
    </div>
  );
};

export default UserProfile; 