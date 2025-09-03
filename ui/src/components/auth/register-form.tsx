"use client";

import * as React from "react";
import { RegisterRequest } from "../../services/auth";
import { useAuth } from "../../contexts/auth-context";

interface RegisterFormProps {
  onSuccess?: () => void;
  onSwitchToLogin?: () => void;
  onError?: (error: string) => void;
}

export function RegisterForm({ onSuccess, onSwitchToLogin, onError }: RegisterFormProps) {
  const { register } = useAuth();
  const [formData, setFormData] = React.useState<RegisterRequest>({
    email: "",
    password: "",
    username: "",
    first_name: "",
    last_name: "",
  });
  const [confirmPassword, setConfirmPassword] = React.useState("");
  const [isLoading, setIsLoading] = React.useState(false);
  const [errors, setErrors] = React.useState<Partial<RegisterRequest & { confirmPassword: string }>>({});

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    
    if (name === "confirmPassword") {
      setConfirmPassword(value);
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
    
    // Clear error when user starts typing
    if (errors[name as keyof typeof errors]) {
      setErrors(prev => ({ ...prev, [name]: undefined }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Partial<RegisterRequest & { confirmPassword: string }> = {};

    if (!formData.email.trim()) {
      newErrors.email = "Email is required";
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = "Please enter a valid email address";
    }

    if (!formData.password) {
      newErrors.password = "Password is required";
    } else if (formData.password.length < 8) {
      newErrors.password = "Password must be at least 8 characters long";
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(formData.password)) {
      newErrors.password = "Password must contain at least one uppercase letter, one lowercase letter, and one number";
    }

    if (!confirmPassword) {
      newErrors.confirmPassword = "Please confirm your password";
    } else if (formData.password !== confirmPassword) {
      newErrors.confirmPassword = "Passwords do not match";
    }

    if (formData.first_name && formData.first_name.trim().length < 2) {
      newErrors.first_name = "First name must be at least 2 characters long";
    }

    if (formData.last_name && formData.last_name.trim().length < 2) {
      newErrors.last_name = "Last name must be at least 2 characters long";
    }

    if (formData.username && formData.username.trim()) {
      if (formData.username.trim().length < 3) {
        newErrors.username = "Username must be at least 3 characters long";
      } else if (formData.username.trim().length > 50) {
        newErrors.username = "Username must be no more than 50 characters long";
      } else if (!/^[a-zA-Z0-9_]+$/.test(formData.username.trim())) {
        newErrors.username = "Username can only contain letters, numbers, and underscores";
      }
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
      // Clean up form data - remove empty optional fields
      const cleanData: RegisterRequest = {
        email: formData.email.trim(),
        password: formData.password,
        ...(formData.username?.trim() && { username: formData.username.trim() }),
        ...(formData.first_name?.trim() && { first_name: formData.first_name.trim() }),
        ...(formData.last_name?.trim() && { last_name: formData.last_name.trim() }),
      };

      await register(cleanData);
      onSuccess?.();
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Registration failed. Please try again.";
      setErrors({ email: errorMessage });
      onError?.(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label htmlFor="first_name" className="block text-sm font-medium text-white/90 mb-2">
            First Name (Optional)
          </label>
          <input
            type="text"
            id="first_name"
            name="first_name"
            value={formData.first_name}
            onChange={handleInputChange}
            className={`w-full px-3 py-2 bg-white/5 border rounded-lg text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-accent/50 focus:border-transparent transition-colors ${
              errors.first_name ? "border-red-500" : "border-white/20"
            }`}
            placeholder="First name"
            disabled={isLoading}
          />
          {errors.first_name && (
            <p className="mt-1 text-sm text-red-400">{errors.first_name}</p>
          )}
        </div>

        <div>
          <label htmlFor="last_name" className="block text-sm font-medium text-white/90 mb-2">
            Last Name (Optional)
          </label>
          <input
            type="text"
            id="last_name"
            name="last_name"
            value={formData.last_name}
            onChange={handleInputChange}
            className={`w-full px-3 py-2 bg-white/5 border rounded-lg text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-accent/50 focus:border-transparent transition-colors ${
              errors.last_name ? "border-red-500" : "border-white/20"
            }`}
            placeholder="Last name"
            disabled={isLoading}
          />
          {errors.last_name && (
            <p className="mt-1 text-sm text-red-400">{errors.last_name}</p>
          )}
        </div>
      </div>

      <div>
        <label htmlFor="email" className="block text-sm font-medium text-white/90 mb-2">
          Email *
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
          required
        />
        {errors.email && (
          <p className="mt-1 text-sm text-red-400">{errors.email}</p>
        )}
      </div>

      <div>
        <label htmlFor="username" className="block text-sm font-medium text-white/90 mb-2">
          Username (Optional)
        </label>
        <input
          type="text"
          id="username"
          name="username"
          value={formData.username}
          onChange={handleInputChange}
          className={`w-full px-3 py-2 bg-white/5 border rounded-lg text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-accent/50 focus:border-transparent transition-colors ${
            errors.username ? "border-red-500" : "border-white/20"
          }`}
          placeholder="Choose a username"
          disabled={isLoading}
        />
        {errors.username && (
          <p className="mt-1 text-sm text-red-400">{errors.username}</p>
        )}
        <p className="mt-1 text-xs text-white/50">
          3-50 characters, letters, numbers, and underscores only
        </p>
      </div>

      <div>
        <label htmlFor="password" className="block text-sm font-medium text-white/90 mb-2">
          Password *
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
          placeholder="Create a password"
          disabled={isLoading}
          required
        />
        {errors.password && (
          <p className="mt-1 text-sm text-red-400">{errors.password}</p>
        )}
        <p className="mt-1 text-xs text-white/50">
          Must be at least 8 characters with uppercase, lowercase, and number
        </p>
      </div>

      <div>
        <label htmlFor="confirmPassword" className="block text-sm font-medium text-white/90 mb-2">
          Confirm Password *
        </label>
        <input
          type="password"
          id="confirmPassword"
          name="confirmPassword"
          value={confirmPassword}
          onChange={handleInputChange}
          className={`w-full px-3 py-2 bg-white/5 border rounded-lg text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-accent/50 focus:border-transparent transition-colors ${
            errors.confirmPassword ? "border-red-500" : "border-white/20"
          }`}
          placeholder="Confirm your password"
          disabled={isLoading}
          required
        />
        {errors.confirmPassword && (
          <p className="mt-1 text-sm text-red-400">{errors.confirmPassword}</p>
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
            Creating account...
          </div>
        ) : (
          "Create Account"
        )}
      </button>

      {onSwitchToLogin && (
        <div className="text-center">
          <p className="text-white/60 text-sm">
            Already have an account?{" "}
            <button
              type="button"
              onClick={onSwitchToLogin}
              className="text-accent hover:text-accent/80 font-medium transition-colors"
            >
              Sign in
            </button>
          </p>
        </div>
      )}
    </form>
  );
}
