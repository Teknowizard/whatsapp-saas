import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard, Package, MessageSquare, ShoppingCart,
  BarChart2, Settings, LogOut, Zap, Users
} from 'lucide-react';
import { useAuth } from '../auth/AuthContext';

const navItems = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard', adminOnly: false },
  { to: '/products', icon: Package, label: 'Products', adminOnly: false },
  { to: '/autoreplies', icon: MessageSquare, label: 'Auto Replies', adminOnly: false },
  { to: '/orders', icon: ShoppingCart, label: 'Orders', adminOnly: false },
  { to: '/analytics', icon: BarChart2, label: 'Analytics', adminOnly: false },
];

const adminNavItems = [
  { to: '/admin', icon: Settings, label: 'Admin Panel' },
  { to: '/admin/users', icon: Users, label: 'User Management' },
];

export default function Sidebar() {
  const { user, logout } = useAuth();

  const tierColors = {
    starter: 'bg-blue-100 text-blue-700',
    growth: 'bg-purple-100 text-purple-700',
    pro: 'bg-amber-100 text-amber-700',
  };

  return (
    <aside className="w-64 bg-gray-900 min-h-screen flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-gray-800">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-green-500 rounded-xl flex items-center justify-center">
            <Zap className="w-6 h-6 text-white" />
          </div>
          <div>
            <p className="text-white font-bold text-sm">Zubo</p>
            <p className="text-gray-400 text-xs">Sales Automation</p>
          </div>
        </div>
      </div>

      {/* User info */}
      <div className="p-4 border-b border-gray-800">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-green-600 rounded-full flex items-center justify-center text-white font-bold text-sm">
            {user?.name?.[0]?.toUpperCase()}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-white text-sm font-medium truncate">{user?.name}</p>
            <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${tierColors[user?.tier]}`}>
              {user?.tier?.toUpperCase()}
            </span>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? 'bg-green-600 text-white'
                  : 'text-gray-400 hover:bg-gray-800 hover:text-white'
              }`
            }
          >
            <Icon className="w-5 h-5 flex-shrink-0" />
            {label}
          </NavLink>
        ))}
        
        {/* Admin Section */}
        {user?.is_admin && (
          <>
            <div className="pt-4 pb-2">
              <p className="text-xs font-semibold text-gray-500 uppercase px-3">Admin</p>
            </div>
            {adminNavItems.map(({ to, icon: Icon, label }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-purple-600 text-white'
                      : 'text-gray-400 hover:bg-gray-800 hover:text-white'
                  }`
                }
              >
                <Icon className="w-5 h-5 flex-shrink-0" />
                {label}
              </NavLink>
            ))}
          </>
        )}
      </nav>

      {/* Logout */}
      <div className="p-4 border-t border-gray-800">
        <button
          onClick={logout}
          className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-gray-400 hover:bg-gray-800 hover:text-red-400 w-full transition-all"
        >
          <LogOut className="w-5 h-5" />
          Sign Out
        </button>
      </div>
    </aside>
  );
}
