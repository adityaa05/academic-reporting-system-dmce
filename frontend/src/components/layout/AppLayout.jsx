import { Navigation } from './Navigation';
import { CollegeHeader } from './CollegeHeader';

export const AppLayout = ({ children }) => {
  return (
    <div className="min-h-screen bg-background">
      <CollegeHeader />
      <Navigation />

      {/* Main content with responsive padding */}
      <main className="md:ml-64 pb-24 md:pb-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </div>
      </main>
    </div>
  );
};
