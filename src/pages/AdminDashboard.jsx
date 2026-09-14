import React, { useState } from 'react';
import { 
  Users, Briefcase, Database, BarChart3, Plus, 
  Search, CheckCircle2, AlertCircle, Sparkles, Filter, RefreshCw 
} from 'lucide-react';
import { MOCK_OPPORTUNITIES } from '../data/mockOpportunities';

export default function AdminDashboard({ onNavigate }) {
  const [activeTab, setActiveTab] = useState('opportunities'); // 'opportunities' | 'stats' | 'datasets'
  const [opportunities, setOpportunities] = useState(MOCK_OPPORTUNITIES);
  const [searchTerm, setSearchTerm] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newCategory, setNewCategory] = useState('Green Energy / Technical');
  const [newLocation, setNewLocation] = useState('District Skill Center');

  const filtered = opportunities.filter(o => 
    o.title.toLowerCase().includes(searchTerm.toLowerCase()) || 
    o.category.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleAddOpportunity = (e) => {
    e.preventDefault();
    if (!newTitle) return;

    const newOpp = {
      id: `opp-${Date.now()}`,
      title: newTitle,
      category: newCategory,
      matchScore: 90,
      location: newLocation,
      type: 'Government Empaneled Scheme',
      duration: '30 Days Training',
      stipend: '₹3,500 / month',
      avgEarnings: '₹15,000 / month',
      partner: 'State Skill Development Mission (SSDM)',
      overview: 'Newly empaneled training and placement opportunity.',
      whyMatches: 'Added by Administrator.',
      skillsPossessed: ['Basic willingness to learn'],
      skillsMissing: ['Specialized trade certification'],
      eligibility: ['Age 18+', 'Resident of district']
    };

    setOpportunities([newOpp, ...opportunities]);
    setNewTitle('');
    setShowAddModal(false);
  };

  return (
    <div className="relative z-20 flex-1 px-4 sm:px-6 lg:px-12 py-8 max-w-6xl mx-auto w-full">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8 pb-6 border-b border-[#b8ded6]">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-3 py-0.5 rounded-full bg-[#134e40] text-white text-xs font-semibold uppercase tracking-wider">
              Administration & Analytics
            </span>
            <span className="text-xs text-[#718078]">National Public Livelihood Grid</span>
          </div>
          <h1 className="font-serif-heading text-3xl sm:text-4xl font-bold text-[#134e40]">
            Utthan Administrator Portal
          </h1>
          <p className="text-sm text-[#718078]">
            Manage verified opportunities, monitor regional language engagement, and audit AI recommendation matches.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => onNavigate('landing')}
            className="px-4 py-2 rounded-full border border-[#134e40] text-[#134e40] text-xs sm:text-sm font-semibold hover:bg-white"
          >
            ← Beneficiary View
          </button>
          <button
            onClick={() => setShowAddModal(true)}
            className="px-4 py-2 rounded-full bg-[#134e40] hover:bg-[#0d3b30] text-white text-xs sm:text-sm font-semibold flex items-center gap-1.5 shadow-sm"
          >
            <Plus className="w-4 h-4" />
            <span>Add Opportunity</span>
          </button>
        </div>
      </div>

      {/* KPI Cards Overview */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div className="bg-white/95 p-4 sm:p-5 rounded-2xl border border-[#b8ded6] shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-[#718078] font-semibold uppercase tracking-wider">Total Onboarded</span>
            <Users className="w-4 h-4 text-[#134e40]" />
          </div>
          <div className="text-2xl sm:text-3xl font-bold text-[#134e40]">124,850</div>
          <span className="text-[11px] text-emerald-700 font-semibold">+18.4% this month</span>
        </div>

        <div className="bg-white/95 p-4 sm:p-5 rounded-2xl border border-[#b8ded6] shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-[#718078] font-semibold uppercase tracking-wider">Active Programs</span>
            <Briefcase className="w-4 h-4 text-[#e69943]" />
          </div>
          <div className="text-2xl sm:text-3xl font-bold text-[#134e40]">342</div>
          <span className="text-[11px] text-[#718078]">Across 28 states & UTs</span>
        </div>

        <div className="bg-white/95 p-4 sm:p-5 rounded-2xl border border-[#b8ded6] shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-[#718078] font-semibold uppercase tracking-wider">Voice Conversations</span>
            <Sparkles className="w-4 h-4 text-[#134e40]" />
          </div>
          <div className="text-2xl sm:text-3xl font-bold text-[#134e40]">78.2%</div>
          <span className="text-[11px] text-emerald-700 font-semibold">Voice-first adoption</span>
        </div>

        <div className="bg-white/95 p-4 sm:p-5 rounded-2xl border border-[#b8ded6] shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-[#718078] font-semibold uppercase tracking-wider">Placement Rate</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="text-2xl sm:text-3xl font-bold text-[#134e40]">84.6%</div>
          <span className="text-[11px] text-[#718078]">Certified beneficiaries</span>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 border-b border-[#b8ded6] mb-6">
        <button
          onClick={() => setActiveTab('opportunities')}
          className={`pb-3 px-4 text-sm font-semibold border-b-2 transition-colors ${
            activeTab === 'opportunities'
              ? 'border-[#134e40] text-[#134e40]'
              : 'border-transparent text-[#718078] hover:text-[#263238]'
          }`}
        >
          Opportunity & Scheme Management ({opportunities.length})
        </button>
        <button
          onClick={() => setActiveTab('stats')}
          className={`pb-3 px-4 text-sm font-semibold border-b-2 transition-colors ${
            activeTab === 'stats'
              ? 'border-[#134e40] text-[#134e40]'
              : 'border-transparent text-[#718078] hover:text-[#263238]'
          }`}
        >
          Language & Demographics Analytics
        </button>
        <button
          onClick={() => setActiveTab('datasets')}
          className={`pb-3 px-4 text-sm font-semibold border-b-2 transition-colors ${
            activeTab === 'datasets'
              ? 'border-[#134e40] text-[#134e40]'
              : 'border-transparent text-[#718078] hover:text-[#263238]'
          }`}
        >
          Verified Data Sources
        </button>
      </div>

      {/* Tab 1: Opportunities Management */}
      {activeTab === 'opportunities' && (
        <div className="bg-white/95 rounded-3xl p-6 border border-[#b8ded6] shadow-sm">
          {/* Search bar */}
          <div className="flex items-center justify-between gap-4 mb-6">
            <div className="relative flex-1 max-w-md">
              <Search className="w-4 h-4 text-[#718078] absolute left-3 top-3" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search scheme name or category..."
                className="w-full pl-9 pr-4 py-2 rounded-xl text-sm border border-[#cbd5e1] bg-[#FAF7F0] focus:outline-none focus:border-[#134e40]"
              />
            </div>
            <span className="text-xs text-[#718078]">Showing {filtered.length} verified listings</span>
          </div>

          {/* Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-[#b8ded6] text-xs uppercase tracking-wider text-[#718078]">
                <tr>
                  <th className="pb-3 font-semibold">Opportunity Name</th>
                  <th className="pb-3 font-semibold">Sector</th>
                  <th className="pb-3 font-semibold">Location</th>
                  <th className="pb-3 font-semibold">Stipend</th>
                  <th className="pb-3 font-semibold">Status</th>
                  <th className="pb-3 font-semibold text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#b8ded6]/40">
                {filtered.map((opp) => (
                  <tr key={opp.id} className="hover:bg-[#FAF7F0]/60 transition-colors">
                    <td className="py-3.5 pr-3">
                      <div className="font-bold text-[#134e40]">{opp.title}</div>
                      <div className="text-xs text-[#718078]">{opp.partner}</div>
                    </td>
                    <td className="py-3.5 px-3 text-xs text-[#37474F]">{opp.category}</td>
                    <td className="py-3.5 px-3 text-xs text-[#37474F]">{opp.location}</td>
                    <td className="py-3.5 px-3 text-xs font-semibold text-emerald-700">{opp.stipend}</td>
                    <td className="py-3.5 px-3">
                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-300">
                        <CheckCircle2 className="w-3 h-3" /> Live
                      </span>
                    </td>
                    <td className="py-3.5 pl-3 text-right">
                      <button 
                        onClick={() => alert(`Editing: ${opp.title}`)}
                        className="text-xs font-semibold text-[#134e40] hover:underline"
                      >
                        Edit
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 2: Stats */}
      {activeTab === 'stats' && (
        <div className="bg-white/95 rounded-3xl p-6 border border-[#b8ded6] shadow-sm space-y-6">
          <h3 className="text-lg font-bold text-[#134e40]">Top Regional Languages Utilized</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            {[
              { lang: 'Hindi (हिन्दी)', pct: '41.2%', users: '51,438' },
              { lang: 'Bengali (বাংলা)', pct: '14.8%', users: '18,477' },
              { lang: 'Tamil (தமிழ்)', pct: '11.5%', users: '14,357' },
              { lang: 'Telugu (తెలుగు)', pct: '9.8%', users: '12,235' },
              { lang: 'Marathi (मराठी)', pct: '8.4%', users: '10,487' },
              { lang: 'Gujarati (ગુજરાતી)', pct: '6.1%', users: '7,615' },
            ].map((st, i) => (
              <div key={i} className="p-4 rounded-xl bg-[#FAF7F0] border border-[#b8ded6]">
                <div className="flex justify-between items-center mb-1">
                  <span className="font-bold text-sm text-[#134e40]">{st.lang}</span>
                  <span className="text-xs font-bold text-[#e69943]">{st.pct}</span>
                </div>
                <div className="w-full bg-[#dbeef5] h-2 rounded-full overflow-hidden">
                  <div className="bg-[#134e40] h-full" style={{ width: st.pct }} />
                </div>
                <span className="text-xs text-[#718078] mt-1.5 block">{st.users} active voice sessions</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 3: Datasets */}
      {activeTab === 'datasets' && (
        <div className="bg-white/95 rounded-3xl p-6 border border-[#b8ded6] shadow-sm space-y-4">
          <h3 className="text-lg font-bold text-[#134e40]">Government Synchronized Data Sources</h3>
          <div className="space-y-3">
            {[
              { name: 'National Career Service (NCS) API', lastSync: '12 mins ago', status: 'Healthy', records: '48,290 openings' },
              { name: 'Skill India Digital Hub (SIDH)', lastSync: '1 hour ago', status: 'Healthy', records: '1,240 training centers' },
              { name: 'PM-KUSUM / Surya Ghar Scheme Datasets', lastSync: '3 hours ago', status: 'Healthy', records: '85,000 rooftop quotas' },
              { name: 'National Health Mission ASHA/ANM Portal', lastSync: '5 hours ago', status: 'Healthy', records: '12,400 village vacancies' }
            ].map((ds, i) => (
              <div key={i} className="p-4 rounded-xl bg-[#FAF7F0] border border-[#cbd5e1] flex items-center justify-between">
                <div>
                  <h4 className="font-bold text-sm text-[#134e40]">{ds.name}</h4>
                  <p className="text-xs text-[#718078]">{ds.records} • Last synced {ds.lastSync}</p>
                </div>
                <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300">
                  {ds.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Modal: Add Opportunity */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl p-6 sm:p-8 max-w-lg w-full border border-[#b8ded6] shadow-2xl animate-in zoom-in-95 duration-200">
            <h2 className="text-xl font-bold text-[#134e40] mb-4">Add Verified Opportunity</h2>
            <form onSubmit={handleAddOpportunity} className="space-y-4">
              <div>
                <label className="text-xs font-semibold text-[#718078] uppercase block mb-1">Opportunity Title</label>
                <input
                  type="text"
                  required
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  placeholder="e.g. Electric Vehicle Charging Station Technician"
                  className="w-full px-3.5 py-2 rounded-xl border border-[#cbd5e1] text-sm focus:outline-none focus:border-[#134e40]"
                />
              </div>
              <div>
                <label className="text-xs font-semibold text-[#718078] uppercase block mb-1">Category</label>
                <select
                  value={newCategory}
                  onChange={(e) => setNewCategory(e.target.value)}
                  className="w-full px-3.5 py-2 rounded-xl border border-[#cbd5e1] text-sm focus:outline-none focus:border-[#134e40]"
                >
                  <option>Green Energy / Technical</option>
                  <option>Traditional Craft & Textiles</option>
                  <option>Agri-Tech / Modern Farming</option>
                  <option>Healthcare & Public Service</option>
                  <option>Animal Husbandry & Dairy</option>
                </select>
              </div>
              <div>
                <label className="text-xs font-semibold text-[#718078] uppercase block mb-1">Location / District</label>
                <input
                  type="text"
                  value={newLocation}
                  onChange={(e) => setNewLocation(e.target.value)}
                  className="w-full px-3.5 py-2 rounded-xl border border-[#cbd5e1] text-sm focus:outline-none focus:border-[#134e40]"
                />
              </div>

              <div className="flex justify-end gap-2 pt-4 border-t border-[#b8ded6]">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 text-sm text-[#718078] hover:text-[#263238]"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-full bg-[#134e40] text-white text-sm font-semibold hover:bg-[#0d3b30]"
                >
                  Save Listing
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
