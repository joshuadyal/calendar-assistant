export function monthLabel(date: Date) {
  return date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
}

export function calendarDays(date: Date) {
  const start = new Date(date.getFullYear(), date.getMonth(), 1);
  const offset = start.getDay();
  const total = new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate();

  return Array.from(
    { length: Math.ceil((offset + total) / 7) * 7 },
    (_, index) => {
      const day = index - offset + 1;
      return day > 0 && day <= total ? day : null;
    },
  );
}

export function isToday(day: number | null, month: Date, today = new Date()) {
  return (
    day === today.getDate() &&
    month.getMonth() === today.getMonth() &&
    month.getFullYear() === today.getFullYear()
  );
}
