import React, { useState } from 'react';
import { 
  User, GraduationCap, Wrench, Heart, Briefcase, MapPin, 
  Compass, CheckCircle, Edit3, Save, Plus, X, ArrowRight, ShieldCheck 
} from 'lucide-react';

export default function ProfilePage({ userProfile, onUpdateProfile, onNavigate }) {
  const [isEditing, setIsEditing] = useState(false);
  const [profile, setProfile] = useState(userProfile);
  const [newSkill, setNewSkill] = useState('');

  const handleSave = () => {
    setIsEditing(false);
    onUpdateProfile(profile);
  };

  const addSkill = () => {
    if (newSkill.trim() && !profile.skills.includes(newSkill.trim())) {
      setProfile({
        ...profile,
        skills: [...profile.skills, newSkill.trim()]
      });
      setNewSkill('');
    }
  };

  const removeSkill = (skillToRemove) => {
    setProfile({
      ...profile,
      skills: profile.skills.filter(s => s !== skillToRemove)
    });
  };

  return (
    <div className="relative z-20 flex-1 px-4 sm:px-6 lg:px-12 py-8 max-w-4xl mx-auto w-full">
      {/* 1. Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8 pb-6 border-b border-[#b8ded6]">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2.5 py-0.5 rounded-full bg-[#134e40]/10 text-[#134e40] text-xs font-semibold uppercase tracking-wider">
              Beneficiary Profile
            </span>
            <span className="flex items-center gap-1 text-xs text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
              <ShieldCheck className="w-3.5 h-3.5" />
              Verified Public Record
            </span>
          </div>
          <h1 className="font-serif-heading text-3xl sm:text-4xl font-bold text-[#134e40]">
            {profile.fullName}
          </h1>
          <p className="text-sm text-[#718078]">
            {profile.location} • Preferred Language: {profile.preferredLanguage}
          </p>
        </div>

        <div className="flex items-center gap-3">
          {isEditing ? (
            <button
              onClick={handleSave}
              className="px-4 py-2 rounded-full bg-[#134e40] text-white text-sm font-medium flex items-center gap-2 shadow-sm hover:bg-[#0d3b30]"
            >
              <Save className="w-4 h-4" />
              <span>Save Changes</span>
            </button>
          ) : (
            <button
              onClick={() => setIsEditing(true)}
              className="px-4 py-2 rounded-full border border-[#134e40] text-[#134e40] text-sm font-medium flex items-center gap-2 hover:bg-white transition-colors"
            >
              <Edit3 className="w-4 h-4" />
              <span>Edit Profile</span>
            </button>
          )}

          <button
            onClick={() => onNavigate('opportunities')}
            className="px-5 py-2 rounded-full bg-[#134e40] text-white text-sm font-medium flex items-center gap-2 hover:bg-[#0d3b30] shadow-sm"
          >
            <span>View Opportunities</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* 2. Structured Profile Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-8">
        {/* Education & Current Work */}
        <div className="bg-white/90 rounded-2xl p-5 border border-[#b8ded6] shadow-sm space-y-4">
          <div className="flex items-start gap-3">
            <div className="p-2.5 rounded-xl bg-[#dbeef5] text-[#134e40] shrink-0">
              <GraduationCap className="w-5 h-5" />
            </div>
            <div className="flex-1">
              <span className="text-xs font-semibold text-[#718078] uppercase tracking-wider block mb-1">
                Highest Education Completed
              </span>
              {isEditing ? (
                <input
                  type="text"
                  value={profile.education}
                  onChange={(e) => setProfile({ ...profile, education: e.target.value })}
                  className="w-full text-sm font-medium text-[#263238] border border-[#cbd5e1] rounded-lg p-2 bg-[#FAF7F0]"
                />
              ) : (
                <p className="text-base font-semibold text-[#263238]">{profile.education}</p>
              )}
            </div>
          </div>

          <div className="pt-4 border-t border-[#b8ded6]/40 flex items-start gap-3">
            <div className="p-2.5 rounded-xl bg-[#dbeef5] text-[#134e40] shrink-0">
              <Briefcase className="w-5 h-5" />
            </div>
            <div className="flex-1">
              <span className="text-xs font-semibold text-[#718078] uppercase tracking-wider block mb-1">
                Current Occupation
              </span>
              {isEditing ? (
                <input
                  type="text"
                  value={profile.currentWork}
                  onChange={(e) => setProfile({ ...profile, currentWork: e.target.value })}
                  className="w-full text-sm font-medium text-[#263238] border border-[#cbd5e1] rounded-lg p-2 bg-[#FAF7F0]"
                />
              ) : (
                <p className="text-base font-semibold text-[#263238]">{profile.currentWork}</p>
              )}
            </div>
          </div>
        </div>

        {/* Location & Mobility Preference */}
        <div className="bg-white/90 rounded-2xl p-5 border border-[#b8ded6] shadow-sm space-y-4">
          <div className="flex items-start gap-3">
            <div className="p-2.5 rounded-xl bg-[#dbeef5] text-[#134e40] shrink-0">
              <MapPin className="w-5 h-5" />
            </div>
            <div className="flex-1">
              <span className="text-xs font-semibold text-[#718078] uppercase tracking-wider block mb-1">
                District / State
              </span>
              {isEditing ? (
                <input
                  type="text"
                  value={profile.location}
                  onChange={(e) => setProfile({ ...profile, location: e.target.value })}
                  className="w-full text-sm font-medium text-[#263238] border border-[#cbd5e1] rounded-lg p-2 bg-[#FAF7F0]"
                />
              ) : (
                <p className="text-base font-semibold text-[#263238]">{profile.location}</p>
              )}
            </div>
          </div>

          <div className="pt-4 border-t border-[#b8ded6]/40 flex items-start gap-3">
            <div className="p-2.5 rounded-xl bg-[#dbeef5] text-[#134e40] shrink-0">
              <Compass className="w-5 h-5" />
            </div>
            <div className="flex-1">
              <span className="text-xs font-semibold text-[#718078] uppercase tracking-wider block mb-1">
                Mobility Preference
              </span>
              {isEditing ? (
                <input
                  type="text"
                  value={profile.mobilityPreference}
                  onChange={(e) => setProfile({ ...profile, mobilityPreference: e.target.value })}
                  className="w-full text-sm font-medium text-[#263238] border border-[#cbd5e1] rounded-lg p-2 bg-[#FAF7F0]"
                />
              ) : (
                <p className="text-base font-semibold text-[#263238]">{profile.mobilityPreference}</p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* 3. Skills Section */}
      <div className="bg-white/90 rounded-2xl p-6 border border-[#b8ded6] shadow-sm mb-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2.5 rounded-xl bg-[#dbeef5] text-[#134e40]">
            <Wrench className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-[#134e40]">Skills & Competencies</h2>
            <p className="text-xs text-[#718078]">Practical abilities you currently possess</p>
          </div>
        </div>

        <div className="flex flex-wrap gap-2 mb-4">
          {profile.skills.map((skill, index) => (
            <span
              key={index}
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-[#134e40]/10 text-[#134e40] font-medium text-sm border border-[#134e40]/20"
            >
              <span>{skill}</span>
              {isEditing && (
                <button
                  onClick={() => removeSkill(skill)}
                  className="p-0.5 hover:text-red-600 rounded-full"
                  aria-label={`Remove ${skill}`}
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              )}
            </span>
          ))}
        </div>

        {isEditing && (
          <div className="flex items-center gap-2 mt-3 max-w-sm">
            <input
              type="text"
              placeholder="Add another skill..."
              value={newSkill}
              onChange={(e) => setNewSkill(e.target.value)}
              className="flex-1 text-sm border border-[#cbd5e1] rounded-lg px-3 py-1.5 bg-[#FAF7F0]"
            />
            <button
              onClick={addSkill}
              className="px-3 py-1.5 bg-[#134e40] text-white rounded-lg text-sm font-medium flex items-center gap-1"
            >
              <Plus className="w-4 h-4" />
              <span>Add</span>
            </button>
          </div>
        )}
      </div>

      {/* 4. Interests & Goals */}
      <div className="bg-white/90 rounded-2xl p-6 border border-[#b8ded6] shadow-sm">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2.5 rounded-xl bg-[#dbeef5] text-[#134e40]">
            <Heart className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-[#134e40]">Growth Interests & Future Aspiration</h2>
            <p className="text-xs text-[#718078]">Sectors and trades you want to specialize in</p>
          </div>
        </div>

        <div className="flex flex-wrap gap-2">
          {profile.interests.map((interest, index) => (
            <span
              key={index}
              className="px-3.5 py-1.5 rounded-full bg-[#FAF7F0] text-[#263238] font-medium text-sm border border-[#b8ded6]"
            >
              ★ {interest}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
