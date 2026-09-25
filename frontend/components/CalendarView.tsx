import {
  CalendarDays,
  ChevronLeft,
  ChevronRight,
  MessageCircle,
} from 'lucide-react';
import { calendarDays, isToday, monthLabel } from '../lib/calendar';

type CalendarViewProps = {
  month: Date;
  onMonthChange: (month: Date) => void;
  onAskAssistant: () => void;
  onAskToday: () => void;
};

export function CalendarView({
  month,
  onMonthChange,
  onAskAssistant,
  onAskToday,
}: CalendarViewProps) {
  const days = calendarDays(month);
  return (
    <section className="calendar-view">
      <div className="content-header">
        <div>
          <p className="eyebrow">YOUR CALENDAR</p>
          <h2>Make room for what matters.</h2>
          <p className="section-subtitle">
            A quick view of your time, with the assistant one message away.
          </p>
        </div>
        <button className="primary-button" onClick={onAskAssistant}>
          <MessageCircle size={16} /> Ask the assistant
        </button>
      </div>
      <div className="calendar-card">
        <div className="calendar-toolbar">
          <button
            className="icon-button"
            onClick={() =>
              onMonthChange(
                new Date(month.getFullYear(), month.getMonth() - 1, 1),
              )
            }
            aria-label="Previous month"
          >
            <ChevronLeft size={18} />
          </button>
          <h3>{monthLabel(month)}</h3>
          <button
            className="icon-button"
            onClick={() =>
              onMonthChange(
                new Date(month.getFullYear(), month.getMonth() + 1, 1),
              )
            }
            aria-label="Next month"
          >
            <ChevronRight size={18} />
          </button>
          <button
            className="today-button"
            onClick={() => onMonthChange(new Date())}
          >
            Today
          </button>
        </div>
        <div className="calendar-weekdays">
          {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day) => (
            <span key={day}>{day}</span>
          ))}
        </div>
        <div className="calendar-grid">
          {days.map((day, index) => (
            <div
              className={`calendar-day ${day === null ? 'muted-day' : ''} ${isToday(day, month) ? 'today' : ''}`}
              key={`${day}-${index}`}
            >
              {day && (
                <>
                  <span>{day}</span>
                  {isToday(day, month) && <small>Today</small>}
                </>
              )}
            </div>
          ))}
        </div>
        <div className="calendar-empty">
          <div className="empty-icon">
            <CalendarDays size={20} />
          </div>
          <div>
            <strong>Events will appear here</strong>
            <p>
              The current API does not expose event listing yet. Ask the
              assistant about your schedule to work with connected calendar
              data.
            </p>
          </div>
          <button className="secondary-button" onClick={onAskToday}>
            Ask about today
          </button>
        </div>
      </div>
    </section>
  );
}
