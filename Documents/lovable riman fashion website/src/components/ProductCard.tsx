import { Link } from "react-router-dom";
import type { Product } from "@/data/products";

interface ProductCardProps {
  product: Product;
}

const ProductCard = ({ product }: ProductCardProps) => {
  const isAvailableForSale = product.productType === "sale" || product.productType === "both";
  const isAvailableForRent = product.productType === "rent" || product.productType === "both";

  const price = isAvailableForSale
    ? `AED ${product.salePrice?.toLocaleString()}`
    : `AED ${product.rentalPrice?.toLocaleString()} / day`;

  return (
    <Link to={`/product/${product.id}`} className="group block">
      <div className="relative overflow-hidden aspect-[3/4] mb-4">
        <img
          src={product.images[0]}
          alt={product.name}
          className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
          loading="lazy"
        />
        <div className="absolute top-4 left-4 flex gap-2">
          {isAvailableForSale && (
            <span className="badge-sale">For Sale</span>
          )}
          {isAvailableForRent && (
            <span className="badge-rent">For Rent</span>
          )}
          {product.isNew && (
            <span className="badge-sale">New</span>
          )}
        </div>
      </div>
      <div className="text-center">
        <p className="font-body text-[10px] tracking-[0.2em] uppercase text-muted-foreground mb-1">
          {product.category}
        </p>
        <h3 className="font-heading text-xl tracking-wide mb-1 group-hover:text-gold transition-colors">
          {product.name}
        </h3>
        <p className="font-body text-xs text-muted-foreground tracking-wider">
          {price}
        </p>
      </div>
    </Link>
  );
};

export default ProductCard;
