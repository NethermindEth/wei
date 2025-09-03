"use client";

import * as React from "react";
import { Modal } from "../ui/modal";
import { LoginForm } from "./login-form";
import { RegisterForm } from "./register-form";

type AuthMode = "login" | "register";

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialMode?: AuthMode;
  onSuccess?: () => void;
}

export function AuthModal({ 
  isOpen, 
  onClose, 
  initialMode = "login", 
  onSuccess 
}: AuthModalProps) {
  const [mode, setMode] = React.useState<AuthMode>(initialMode);
  const [error, setError] = React.useState<string>("");

  // Reset mode when modal opens
  React.useEffect(() => {
    if (isOpen) {
      setMode(initialMode);
      setError("");
    }
  }, [isOpen, initialMode]);

  const handleSuccess = () => {
    setError("");
    onSuccess?.();
    onClose();
  };

  const handleError = (errorMessage: string) => {
    setError(errorMessage);
  };

  const switchMode = () => {
    setMode(mode === "login" ? "register" : "login");
    setError("");
  };

  const getTitle = () => {
    return mode === "login" ? "Sign In" : "Create Account";
  };

  const getSubtitle = () => {
    return mode === "login" 
      ? "Welcome back! Sign in to your account to continue."
      : "Join wei to start analyzing governance proposals.";
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={getTitle()}>
      <div className="space-y-4">
        <div className="text-center">
          <p className="text-white/70 text-sm">{getSubtitle()}</p>
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3">
            <p className="text-red-400 text-sm">{error}</p>
          </div>
        )}

        {mode === "login" ? (
          <LoginForm
            onSuccess={handleSuccess}
            onSwitchToRegister={switchMode}
            onError={handleError}
          />
        ) : (
          <RegisterForm
            onSuccess={handleSuccess}
            onSwitchToLogin={switchMode}
            onError={handleError}
          />
        )}

        <div className="border-t border-white/10 pt-4">
          <div className="text-center">
            <p className="text-white/50 text-xs">
              By continuing, you agree to our Terms of Service and Privacy Policy.
            </p>
          </div>
        </div>
      </div>
    </Modal>
  );
}
