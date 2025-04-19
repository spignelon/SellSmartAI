import React from 'react';
import { getFullMediaUrl } from '../services/api';

interface ProductImageProps {
  src: string;
  alt: string;
  className?: string;
}

const ProductImage: React.FC<ProductImageProps> = ({ src, alt, className = "" }) => {
  const fullUrl = getFullMediaUrl(src);
  
  return (
    <img 
      src={fullUrl} 
      alt={alt} 
      className={className}
      onError={(e) => {
        console.error(`Failed to load image: ${fullUrl}`);
        // Set a fallback image
        e.currentTarget.src = '/placeholder.png';
      }}
    />
  );
};

export default ProductImage;
