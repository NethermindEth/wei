"use client";

import * as React from "react";

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}

export function Modal({ isOpen, onClose, title, children }: ModalProps) {
  React.useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    
    if (isOpen) {
      document.addEventListener("keydown", handleEscape);
    }
    
    return () => {
      document.removeEventListener("keydown", handleEscape);
    };
  }, [isOpen, onClose]);

  React.useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "auto";
    }
    
    return () => {
      document.body.style.overflow = "auto";
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6">
      <div 
        className="absolute inset-0 bg-black/70 backdrop-blur-sm" 
        onClick={onClose}
      />
      
      <div className="relative z-10 w-full max-w-md sm:max-w-lg max-h-[95vh] sm:max-h-[90vh] overflow-hidden rounded-lg bg-[#121212] border border-white/10 shadow-xl">
        <div className="flex items-center justify-between border-b border-white/10 px-4 sm:px-6 py-3 sm:py-4">
          <h3 className="text-lg font-medium text-white">{title}</h3>
          <button 
            onClick={onClose}
            className="rounded-full p-1 hover:bg-white/10 transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        
        <div className="p-4 sm:p-6 overflow-y-auto overflow-x-hidden max-h-[calc(95vh-120px)] sm:max-h-[calc(90vh-140px)]">
          {children}
        </div>
      </div>
    </div>
  );
}
