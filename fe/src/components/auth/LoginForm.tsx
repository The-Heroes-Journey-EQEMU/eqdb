import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import Card, { CardBody, CardHeader, CardTitle } from '../common/Card';
import Button from '../common/Button';
import Input from '../common/Input';
import LoadingSpinner from '../common/LoadingSpinner';

interface LoginFormProps {
  onSuccess?: () => void;
  redirectTo?: string;
  isModal?: boolean;
}

export const LoginForm: React.FC<LoginFormProps> = ({ 
  onSuccess, 
  redirectTo = '/',
  isModal = false
}) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, isLoading, error } = useAuth();
  
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  // Get redirect path from location state or props
  const redirectPath = location.state?.from?.pathname || redirectTo;

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!formData.email) {
      errors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      errors.email = 'Please enter a valid email address';
    }

    if (!formData.password) {
      errors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      errors.password = 'Password must be at least 8 characters';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    try {
      await login(formData);
      
      // Call success callback if provided
      if (onSuccess) {
        onSuccess();
      } else {
        // Navigate to redirect path
        navigate(redirectPath, { replace: true });
      }
    } catch (error) {
      // Error is handled by the auth context
      console.error('Login error:', error);
    }
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Clear validation error when user starts typing
    if (validationErrors[field]) {
      setValidationErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const formContent = (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Email Field */}
      <div>
        <Input
          label="Email Address"
          type="email"
          value={formData.email}
          onChange={(e) => handleInputChange('email', e.target.value)}
          placeholder="Enter your email"
          error={validationErrors.email}
          disabled={isLoading}
          required
        />
      </div>

      {/* Password Field */}
      <div>
        <Input
          label="Password"
          type="password"
          value={formData.password}
          onChange={(e) => handleInputChange('password', e.target.value)}
          placeholder="Enter your password"
          error={validationErrors.password}
          disabled={isLoading}
          required
        />
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-md">
          <p className="text-destructive text-sm">{error}</p>
        </div>
      )}

      {/* Submit Button */}
      <Button
        type="submit"
        variant="primary"
        className="w-full"
        disabled={isLoading}
      >
        {isLoading ? (
          <div className="flex items-center space-x-2">
            <LoadingSpinner size="sm" />
            <span>Signing In...</span>
          </div>
        ) : (
          'Sign In'
        )}
      </Button>
    </form>
  );

  // If it's a modal, just return the form content
  if (isModal) {
    return (
      <div className="space-y-4">
        {formContent}
        
        {/* Demo Account Info */}
        <div className="p-4 bg-muted/50 rounded-md">
          <h4 className="font-medium text-sm mb-2">Demo Account</h4>
          <p className="text-xs text-muted-foreground mb-2">
            For testing purposes, you can use:
          </p>
          <div className="text-xs space-y-1">
            <p><strong>Email:</strong> aepod23@gmail.com</p>
            <p><strong>Password:</strong> frogluck23</p>
          </div>
        </div>
      </div>
    );
  }

  // Full-screen layout
  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold">Welcome Back</CardTitle>
          <p className="text-muted-foreground">
            Sign in to your EQDB account
          </p>
        </CardHeader>
        
        <CardBody>
          {formContent}

          {/* Demo Account Info */}
          <div className="mt-6 p-4 bg-muted/50 rounded-md">
            <h4 className="font-medium text-sm mb-2">Demo Account</h4>
            <p className="text-xs text-muted-foreground mb-2">
              For testing purposes, you can use:
            </p>
            <div className="text-xs space-y-1">
              <p><strong>Email:</strong> aepod23@gmail.com</p>
              <p><strong>Password:</strong> frogluck23</p>
            </div>
          </div>

          {/* Additional Links */}
          <div className="mt-6 text-center">
            <p className="text-sm text-muted-foreground">
              Don't have an account?{' '}
              <button
                type="button"
                className="text-primary hover:underline"
                onClick={() => navigate('/register')}
              >
                Contact an administrator
              </button>
            </p>
          </div>
        </CardBody>
      </Card>
    </div>
  );
};

export default LoginForm; 