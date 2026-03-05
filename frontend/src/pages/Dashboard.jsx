import { useState, useEffect } from 'react';
import { dashboardAPI } from '../services/api';
import { useAuth } from '../auth/AuthContext';
import { TrendingUp, ShoppingBag, Clock, MessageCircle, Percent, CheckCircle } from 'lucide-react';
import toast from 'react-hot-toast';

function StatCard({ label, value, icon: Icon, color, sub }) {
  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm font-medium text-gray-500">{label}</p>
        <div className={`w-10 h-10 ${color} rounded-xl flex items-center justify-center`}>
          <Icon className="w-5 h-5 text-white" />
        </div>
      </div>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
      {sub && <p className="text-xs text-gray-500 mt-1">{sub}</p>}
    </div>
  );
}

export default function Dashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    dashboardAPI.summary()
      .then(res => setStats(res.data))
      .catch(() => toast.error('Failed to load dashboard'))
      .finally(() => setLoading(false));
  }, []);

  const fmt = (n) => `₦${(n || 0).toLocaleString('en-NG', { minimumFractionDigits: 0 })}`;

  if (loading) return (
    <div className="p-8 flex items-center justify-center h-64">
      <div className="w-10 h-10 border-4 border-green-500 border-t-transparent rounded-full animate-spin" />
    </div>
  );

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Good day, {user?.name?.split(' ')[0]} 👋</h1>
        <p className="text-gray-500 mt-1">Here's your business overview</p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 mb-8">
        <StatCard label="Total Revenue" value={fmt(stats?.total_revenue)} icon={TrendingUp} color="bg-green-500" />
        <StatCard label="Total Orders" value={stats?.total_orders || 0} icon={ShoppingBag} color="bg-blue-500" />
        <StatCard label="Pending" value={stats?.pending_payments || 0} icon={Clock} color="bg-amber-500" />
        <StatCard label="Paid" value={stats?.paid_orders || 0} icon={CheckCircle} color="bg-emerald-500" />
        <StatCard label="Messages" value={stats?.messages_handled || 0} icon={MessageCircle} color="bg-purple-500" />
        <StatCard label="Conversion" value={`${stats?.conversion_rate || 0}%`} icon={Percent} color="bg-pink-500" />
      </div>

      {/* Tier info banner */}
      <div className={`rounded-2xl p-6 ${
        user?.tier === 'pro' ? 'bg-amber-50 border border-amber-200' :
        user?.tier === 'growth' ? 'bg-purple-50 border border-purple-200' :
        'bg-blue-50 border border-blue-200'
      }`}>
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-gray-900">
              You're on the {user?.tier?.charAt(0).toUpperCase() + user?.tier?.slice(1)} Plan
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              {user?.tier === 'starter' && 'Upgrade to Growth to unlock payment links and analytics.'}
              {user?.tier === 'growth' && 'Upgrade to Pro to unlock abandoned cart reminders and broadcast.'}
              {user?.tier === 'pro' && '🎉 You have access to all features!'}
            </p>
          </div>
          {user?.tier !== 'pro' && (
            <a href="mailto:upgrade@whatsales.ng"
              className="px-4 py-2 bg-gray-900 text-white text-sm font-medium rounded-lg hover:bg-gray-700 transition-colors">
              Upgrade Plan
            </a>
          )}
        </div>
      </div>
    </div>
  );
}
