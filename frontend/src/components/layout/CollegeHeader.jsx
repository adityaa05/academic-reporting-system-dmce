export const CollegeHeader = () => {
  return (
    <header className="bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-center sm:justify-start py-3 sm:py-4 gap-3 sm:gap-4">
          {/* College Logo */}
          <div className="flex-shrink-0">
            <img
              src="/images/dmce-logo.png"
              alt="DMCE Logo"
              className="w-12 h-12 sm:w-16 sm:h-16 object-contain"
              onError={(e) => {
                e.target.style.display = 'none';
                e.target.nextSibling.style.display = 'flex';
              }}
            />
            <div className="w-12 h-12 sm:w-16 sm:h-16 bg-blue-600 rounded-full items-center justify-center hidden">
              <span className="text-white font-bold text-lg sm:text-2xl">DMCE</span>
            </div>
          </div>

          {/* College Name */}
          <div className="flex flex-col">
            <p className="text-xs sm:text-sm text-gray-600 font-medium">
              Nagar Yuwak Shikshan Sanstha, Airoli's
            </p>
            <h1 className="text-lg sm:text-2xl md:text-3xl font-bold text-gray-900">
              Datta Meghe College of Engineering
            </h1>
          </div>
        </div>
      </div>
      <div className="h-1 bg-gradient-to-r from-yellow-400 via-yellow-500 to-yellow-400"></div>
    </header>
  );
};
