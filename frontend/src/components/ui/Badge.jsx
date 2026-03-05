import { DOMAIN_COLORS, DOMAIN_LABELS } from '../../constants';

export const Badge = ({ children, variant = 'default', className = '' }) => {
  const variants = {
    default: 'bg-gray-200 text-gray-700',
    primary: 'bg-blue-100 text-blue-700',
    success: 'bg-green-100 text-green-700',
    warning: 'bg-amber-100 text-amber-700',
    danger: 'bg-red-100 text-red-700',
  };

  return (
    <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider ${variants[variant]} ${className}`}>
      {children}
    </span>
  );
};

export const DomainBadge = ({ domain }) => {
  const color = DOMAIN_COLORS[domain] || DOMAIN_COLORS.OTHER;
  const label = DOMAIN_LABELS[domain] || domain;

  return (
    <span
      className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider"
      style={{
        backgroundColor: color + '20',
        color: color
      }}
    >
      {label}
    </span>
  );
};
