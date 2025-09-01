"use client";

import React, { useState } from 'react';
import Image from 'next/image';
import { convertIpfsUrl, isValidImageUrl } from '../../utils/ipfs';

interface AvatarProps {
  src?: string;
  alt: string;
  size?: number;
  className?: string;
  fallback?: React.ReactNode;
}

export function Avatar({ 
  src, 
  alt, 
  size = 20, 
  className = "rounded-full flex-shrink-0",
  fallback
}: AvatarProps) {
  const [imageError, setImageError] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Don't render anything if no src or invalid image URL
  if (!src || !isValidImageUrl(src) || imageError) {
    return fallback ? <>{fallback}</> : null;
  }

  const convertedSrc = convertIpfsUrl(src);

  return (
    <>
      {isLoading && fallback && <>{fallback}</>}
      <Image
        src={convertedSrc}
        alt={alt}
        width={size}
        height={size}
        className={`${className} ${isLoading ? 'hidden' : ''}`}
        onLoad={() => setIsLoading(false)}
        onError={() => {
          setImageError(true);
          setIsLoading(false);
        }}
        unoptimized // For external/IPFS images
      />
    </>
  );
}

// Default fallback avatar component
export function DefaultAvatar({ name, size = 20 }: { name: string; size?: number }) {
  const initial = name?.charAt(0)?.toUpperCase() || '?';
  
  return (
    <div 
      className="rounded-full bg-white/10 text-white/70 flex items-center justify-center text-xs font-medium flex-shrink-0"
      style={{ width: size, height: size, fontSize: size * 0.4 }}
    >
      {initial}
    </div>
  );
}
