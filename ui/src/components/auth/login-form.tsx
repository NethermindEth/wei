"use client";

import * as React from "react";
import { LoginRequest } from "../../services/auth";
import { useAuth } from "../../contexts/auth-context";

interface LoginFormProps {
  onSuccess?: () => void;
  onSwitchToRegister?: () => void;
  onError?: (error: string) => void;
}

export function LoginForm({ onSuccess, onSwitchToRegister, onError }: LoginFormProps) {
  const { login } = useAuth();
  const [formData, setFormData] = React.useState<LoginRequest>({
    email: "",
    password: "",
  });
  const [isLoading, setIsLoading] = React.useState(false);
  const [errors, setErrors] = React.useState<Partial<LoginRequest>>({});

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // Clear error when user starts typing
    if (errors[name as keyof LoginRequest]) {
      setErrors(prev => ({ ...prev, [name]: undefined }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Partial<LoginRequest> = {};

    if (!formData.email.trim()) {
      newErrors.email = "Email is required";
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = "Please enter a valid email address";
    }

    if (!formData.password) {
      newErrors.password = "Password is required";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    setIsLoading(true);
    setErrors({});

    try {
      await login(formData.email, formData.password);
      onSuccess?.();
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Login failed. Please try again.";
      setErrors({ email: errorMessage });
      onError?.(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div>
        <label htmlFor="email" className="block text-sm font-medium text-white/90 mb-1">
          Email
        </label>
        <input
          type="email"
          id="email"
          name="email"
          value={formData.email}
          onChange={handleInputChange}
          className={`w-full px-3 py-2 bg-white/5 border rounded-lg text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-accent/50 focus:border-transparent transition-colors ${
            errors.email ? "border-red-500" : "border-white/20"
          }`}
          placeholder="Enter your email"
          disabled={isLoading}
        />
        {errors.email && (
          <p className="mt-1 text-sm text-red-400">{errors.email}</p>
        )}
      </div>

      <div>
        <label htmlFor="password" className="block text-sm font-medium text-white/90 mb-1">
          Password
        </label>
        <input
          type="password"
          id="password"
          name="password"
          value={formData.password}
          onChange={handleInputChange}
          className={`w-full px-3 py-2 bg-white/5 border rounded-lg text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-accent/50 focus:border-transparent transition-colors ${
            errors.password ? "border-red-500" : "border-white/20"
          }`}
          placeholder="Enter your password"
          disabled={isLoading}
        />
        {errors.password && (
          <p className="mt-1 text-sm text-red-400">{errors.password}</p>
        )}
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full bg-accent hover:bg-accent/90 text-black font-medium py-2 px-4 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-accent/50"
      >
        {isLoading ? (
          <div className="flex items-center justify-center">
            <div className="w-4 h-4 border-2 border-black/30 border-t-black rounded-full animate-spin mr-2" />
            Signing in...
          </div>
        ) : (
          "Sign In"
        )}
      </button>

      {onSwitchToRegister && (
        <div className="text-center">
          <p className="text-white/60 text-sm">
            Don&apos;t have an account?{" "}
            <button
              type="button"
              onClick={onSwitchToRegister}
              className="text-accent hover:text-accent/80 font-medium transition-colors"
            >
              Sign up
            </button>
          </p>
        </div>
      )}
    </form>
  );
}
