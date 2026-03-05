import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import toast from 'react-hot-toast';
import { Zap, Check } from 'lucide-react';

const TIERS = [
  { value: 'starter', name: 'Starter', setup: '₦2,500', monthly: '₦5,000', features: ['10 products', 'Auto-replies', 'Order logging'] },
  { value: 'growth', name: 'Growth', setup: '₦5,000', monthly: '₦7,500', features: ['30 products', 'Payment links', 'Basic analytics'] },
  { value: 'pro', name: 'Pro', setup: '₦10,000', monthly: '₦10,000', features: ['Unlimited products', 'Abandoned cart', 'Broadcast & multi-number'] },
];

export default function Register() {
  const [form, setForm] = useState({ name: '', phone: '', email: '', password: '', tier: 'starter' });
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (form.password.length < 8) return toast.error('Password must be at least 8 characters');
    setLoading(true);
    try {
      await register(form);
      navigate('/dashboard');
      toast.success('Account created! Welcome 🎉');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-green-900 py-8 px-4">
      <div className="max-w-3xl mx-auto">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-green-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <Zap className="w-9 h-9 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white">Start Selling on WhatsApp with Zubo</h1>
          <p className="text-gray-400 mt-1">Choose your plan and get started in minutes</p>
        </div>

        {/* Tier Selection */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          {TIERS.map(tier => (
            <button
              key={tier.value}
              type="button"
              onClick={() => setForm(f => ({ ...f, tier: tier.value }))}
              className={`p-4 rounded-xl border-2 text-left transition-all ${
                form.tier === tier.value
                  ? 'border-green-500 bg-green-500/10'
                  : 'border-gray-600 bg-gray-800/50 hover:border-gray-500'
              }`}
            >
              <p className={`font-bold text-lg ${form.tier === tier.value ? 'text-green-400' : 'text-white'}`}>{tier.name}</p>
              <p className="text-gray-300 text-sm">{tier.monthly}/mo</p>
              <p className="text-gray-500 text-xs mt-1">Setup: {tier.setup}</p>
              <ul className="mt-3 space-y-1">
                {tier.features.map(f => (
                  <li key={f} className="flex items-center gap-2 text-xs text-gray-400">
                    <Check className="w-3 h-3 text-green-400 flex-shrink-0" />
                    {f}
                  </li>
                ))}
              </ul>
            </button>
          ))}
        </div>

        <div className="bg-white rounded-2xl shadow-2xl p-8">
          <h2 className="text-xl font-bold text-gray-900 mb-6">Create Your Account</h2>
          <form onSubmit={handleSubmit} className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
              <input required value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500"
                placeholder="John Doe" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Phone Number</label>
              <input required value={form.phone} onChange={e => setForm(f => ({ ...f, phone: e.target.value }))}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500"
                placeholder="+2348012345678" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input type="email" required value={form.email} onChange={e => setForm(f => ({ ...f, email: e.target.value }))}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500"
                placeholder="you@example.com" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
              <input type="password" required value={form.password} onChange={e => setForm(f => ({ ...f, password: e.target.value }))}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500"
                placeholder="Min 8 characters" />
            </div>
            <div className="col-span-2">
              <button type="submit" disabled={loading}
                className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-3 rounded-xl transition-colors disabled:opacity-60">
                {loading ? 'Creating account...' : `Create ${TIERS.find(t => t.value === form.tier)?.name} Account`}
              </button>
            </div>
          </form>
          <p className="text-center text-sm text-gray-600 mt-4">
            Already have an account? <Link to="/login" className="text-green-600 font-semibold hover:underline">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
