import { CalendarDays, MessageCircle, X } from 'lucide-react';
import type { View } from '../lib/types';

type SidebarProps = {
  view: View;
  conversationCount: number;
  mobileOpen: boolean;
  onViewChange: (view: View) => void;
  onClose: () => void;
};

export function Sidebar({
  view,
  conversationCount,
  mobileOpen,
  onViewChange,
  onClose,
}: SidebarProps) {
  return (
    <aside className={`sidebar ${mobileOpen ? 'sidebar-open' : ''}`}>
      <div className="sidebar-heading">
        <span>WORKSPACE</span>
        <button
          onClick={onClose}
          className="close-nav"
          aria-label="Close navigation"
        >
          <X size={17} />
        </button>
      </div>
      <nav className="side-nav" aria-label="Workspace navigation">
        <button
          className={view === 'chat' ? 'nav-item active' : 'nav-item'}
          onClick={() => {
            onViewChange('chat');
            onClose();
          }}
        >
          <MessageCircle size={18} />
          <span>Agent</span>
          <span className="nav-count">{conversationCount || ''}</span>
        </button>
        <button
          className={view === 'calendar' ? 'nav-item active' : 'nav-item'}
          onClick={() => {
            onViewChange('calendar');
            onClose();
          }}
        >
          <CalendarDays size={18} />
          <span>Calendar</span>
        </button>
      </nav>
      <div className="sidebar-footer">
        <div className="status-dot" />
        <div>
          <strong>Google Calendar</strong>
          <span>Connected</span>
        </div>
      </div>
    </aside>
  );
}
