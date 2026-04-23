const ProductSkeleton = () => {
  return (
    <div className="animate-pulse">
      <div className="bg-gray-200 aspect-[3/4] mb-4 rounded-sm" />
      <div className="h-4 bg-gray-200 w-3/4 mb-2" />
      <div className="h-4 bg-gray-200 w-1/2" />
      <div className="h-6 bg-gray-200 w-1/3 mt-4" />
    </div>
  );
};

export default ProductSkeleton;