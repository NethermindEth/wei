/**
 * Convert IPFS URLs to HTTP gateway URLs
 */
export function convertIpfsUrl(url: string): string {
  if (!url) return '';
  
  // If it's already an HTTP URL, return as is
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url;
  }
  
  // Handle ipfs:// protocol
  if (url.startsWith('ipfs://')) {
    const hash = url.replace('ipfs://', '');
    return `https://gateway.pinata.cloud/ipfs/${hash}`;
  }
  
  // Handle /ipfs/ prefix
  if (url.startsWith('/ipfs/')) {
    return `https://gateway.pinata.cloud${url}`;
  }
  
  // If it looks like an IPFS hash (starts with Qm or baf), convert it
  if (url.match(/^(Qm[1-9A-HJ-NP-Za-km-z]{44}|baf[A-Za-z0-9]{5,})/)) {
    return `https://gateway.pinata.cloud/ipfs/${url}`;
  }
  
  // Return original URL if no conversion needed
  return url;
}

/**
 * Check if a URL is a valid image URL
 */
export function isValidImageUrl(url: string): boolean {
  if (!url) return false;
  
  const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.ico'];
  const lowerUrl = url.toLowerCase();
  
  return imageExtensions.some(ext => lowerUrl.includes(ext)) || 
         lowerUrl.includes('image') || 
         url.startsWith('data:image/');
}
