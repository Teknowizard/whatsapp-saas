import { useState, useEffect } from 'react';
import { autoRepliesAPI } from '../services/api';
import { Plus, Trash2, MessageSquare, Zap } from 'lucide-react';
import toast from 'react-hot-toast';

export default function AutoReplies() {
  const [replies, setReplies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({ keyword: '', response: '' });

  useEffect(() => { fetchReplies(); }, []);

  const fetchReplies = () => {
    autoRepliesAPI.list()
      .then(res => setReplies(res.data))
      .catch(() => toast.error('Failed to load auto-replies'))
      .finally(() => setLoading(false));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await autoRepliesAPI.create(form);
      toast.success('Auto-reply created');
      setShowModal(false);
      setForm({ keyword: '', response: '' });
      fetchReplies();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to create');
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Delete this auto-reply?')) return;
    try {
      await autoRepliesAPI.delete(id);
      toast.success('Deleted');
      fetchReplies();
    } catch {
      toast.error('Failed to delete');
    }
  };

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Auto Replies</h1>
          <p className="text-gray-500 text-sm mt-1">Automatically respond to customer messages</p>
        </div>
        <button onClick={() => setShowModal(true)}
          className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2.5 rounded-xl font-medium transition-colors">
          <Plus className="w-4 h-4" /> Add Rule
        </button>
      </div>

      {loading ? (
        <div className="flex justify-center py-20">
          <div className="w-10 h-10 border-4 border-green-500 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : replies.length === 0 ? (
        <div className="text-center py-20 bg-white rounded-2xl border border-gray-100">
          <MessageSquare className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-700">No auto-replies yet</h3>
          <p className="text-gray-400 text-sm mt-1">Add keywords to auto-respond to customers</p>
          <button onClick={() => setShowModal(true)} className="mt-4 bg-green-600 text-white px-6 py-2.5 rounded-xl">
            Add First Rule
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          {replies.map(r => (
            <div key={r.id} className="bg-white rounded-xl border border-gray-100 p-5 flex items-start gap-4">
              <div className="w-10 h-10 bg-green-100 rounded-xl flex items-center justify-center flex-shrink-0">
                <Zap className="w-5 h-5 text-green-600" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-medium text-gray-500">KEYWORD</span>
                  <code className="bg-gray-100 text-gray-800 text-sm px-2 py-0.5 rounded font-mono">{r.keyword}</code>
                </div>
                <p className="text-gray-700 text-sm">{r.response}</p>
              </div>
              <button onClick={() => handleDelete(r.id)}
                className="text-red-400 hover:text-red-600 p-1.5 rounded-lg hover:bg-red-50 transition-colors flex-shrink-0">
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      )}

      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl p-6 w-full max-w-md">
            <h2 className="text-xl font-bold text-gray-900 mb-5">Add Auto-Reply Rule</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Trigger Keyword</label>
                <input required value={form.keyword} onChange={e => setForm(f => ({ ...f, keyword: e.target.value }))}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500"
                  placeholder="e.g. price, order, hello" />
                <p className="text-xs text-gray-500 mt-1">When customer sends this word, auto-reply is triggered</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Response Message</label>
                <textarea required value={form.response} onChange={e => setForm(f => ({ ...f, response: e.target.value }))}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500 resize-none"
                  rows={4} placeholder="Your automatic response..." />
              </div>
              <div className="flex gap-3">
                <button type="button" onClick={() => setShowModal(false)}
                  className="flex-1 border border-gray-300 text-gray-700 py-3 rounded-xl hover:bg-gray-50 font-medium">Cancel</button>
                <button type="submit"
                  className="flex-1 bg-green-600 text-white py-3 rounded-xl hover:bg-green-700 font-medium">Save Rule</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
