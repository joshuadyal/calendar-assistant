import { CalendarDays, ChevronDown, LogOut, Plus } from 'lucide-react';

function initials(email: string | null) {
  return email ? email.slice(0, 2).toUpperCase() : 'GU';
}

type TopbarProps = {
  email: string | null;
  accountOpen: boolean;
  onAccountToggle: () => void;
  onLogout: () => void;
  onMobileMenuToggle: () => void;
};

export function Topbar({
  email,
  accountOpen,
  onAccountToggle,
  onLogout,
  onMobileMenuToggle,
}: TopbarProps) {
  return (
    <header className="topbar">
      <button
        className="mobile-menu"
        onClick={onMobileMenuToggle}
        aria-label="Toggle navigation"
      >
        <Plus size={19} />
      </button>
      <div className="wordmark">
        <span className="wordmark-icon">
          <CalendarDays size={17} />
        </span>{' '}
        daymark
      </div>
      <div className="topbar-account">
        <button
          className="account-button"
          onClick={onAccountToggle}
          aria-expanded={accountOpen}
        >
          <span className="avatar">{initials(email)}</span>
          <span className="account-email">{email}</span>
          <ChevronDown size={15} />
        </button>
        {accountOpen && (
          <div className="account-menu">
            <p className="menu-label">ACCOUNT</p>
            <p className="menu-email">{email}</p>
            <button onClick={onLogout}>
              <LogOut size={15} /> Sign out
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
