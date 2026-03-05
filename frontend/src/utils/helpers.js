import { format, parseISO } from 'date-fns';

export const formatDate = (dateString) => {
  try {
    return format(parseISO(dateString), 'MMM dd, yyyy');
  } catch {
    return dateString;
  }
};

export const formatTime = (dateString) => {
  try {
    return format(parseISO(dateString), 'hh:mm a');
  } catch {
    return dateString;
  }
};

export const formatDateTime = (dateString) => {
  try {
    return format(parseISO(dateString), 'MMM dd, yyyy hh:mm a');
  } catch {
    return dateString;
  }
};

export const getGreeting = () => {
  const hour = new Date().getHours();
  if (hour < 12) return 'Good morning';
  if (hour < 18) return 'Good afternoon';
  return 'Good evening';
};

export const truncate = (str, length = 100) => {
  if (str.length <= length) return str;
  return str.substring(0, length) + '...';
};
