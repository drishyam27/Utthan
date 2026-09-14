import React, { useState } from 'react';
import Navbar from './components/Navbar';
import CulturalBackground from './components/CulturalBackground';
import LandingPage from './pages/LandingPage';
import LanguagePage from './pages/LanguagePage';
import ConversationPage from './pages/ConversationPage';
import ProfilePage from './pages/ProfilePage';
import OpportunitiesPage from './pages/OpportunitiesPage';
import OpportunityDetailsPage from './pages/OpportunityDetailsPage';
import ActionPathPage from './pages/ActionPathPage';
import HowToUsePage from './pages/HowToUsePage';
import AdminDashboard from './pages/AdminDashboard';
import { LANGUAGES } from './data/languages';
import { INITIAL_USER_PROFILE, MOCK_OPPORTUNITIES } from './data/mockOpportunities';
import { getUIText } from './data/uiTranslations';
import { X } from 'lucide-react';

export default function App() {
  const [currentPage, setCurrentPage] = useState('landing');
  const [currentLanguage, setCurrentLanguage] = useState(LANGUAGES[0]); // English default matching reference
  const [userProfile, setUserProfile] = useState(INITIAL_USER_PROFILE);
  const [selectedOpportunity, setSelectedOpportunity] = useState(MOCK_OPPORTUNITIES[0]);
  const [languageModalOpen, setLanguageModalOpen] = useState(false);
  const [initialPromptText, setInitialPromptText] = useState('');

  // Navigation handler
  const handleNavigate = (pageId) => {
    setCurrentPage(pageId);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Start Voice conversation flow
  const handleStartVoice = () => {
    setInitialPromptText('');
    setCurrentPage('conversation');
  };

  // Start Text conversation flow
  const handleStartText = (text = '') => {
    setInitialPromptText(text);
    setCurrentPage('conversation');
  };

  // Start Onboarding from Navbar "Get Started"
  const handleStartOnboarding = () => {
    // Start with AI Step 0: Language Input (Voice or Click) -> Step-by-Step Questions -> Matched Opportunities
    setCurrentPage('conversation');
  };

  // Language selection callback
  const handleSelectLanguage = (lang) => {
    setCurrentLanguage(lang);
    setLanguageModalOpen(false);
    setUserProfile((prev) => ({ ...prev, preferredLanguage: lang.name }));
  };

  // Callback when AI conversation completes
  const handleCompleteConversation = (answers) => {
    if (answers.workInterest) {
      setUserProfile((prev) => ({
        ...prev,
        interests: [answers.workInterest, ...prev.interests.filter(i => i !== answers.workInterest)]
      }));
    }
    setCurrentPage('opportunities');
  };

  // Select opportunity for details view
  const handleSelectOpportunity = (opp) => {
    setSelectedOpportunity(opp);
    setCurrentPage('details');
  };

  // Start action path from opportunity details
  const handleStartActionPath = (opp) => {
    setSelectedOpportunity(opp);
    setCurrentPage('action-path');
  };

  return (
    <div className="relative min-h-screen flex flex-col bg-[#FAF7F0] text-[#263238] font-sans selection:bg-[#134e40] selection:text-white">
      {/* 1. Cultural Indian Line Art, Scripts & Watercolor Wash Background */}
      <CulturalBackground />

      {/* 2. Top Navigation Bar matching reference */}
      <Navbar
        currentLanguage={currentLanguage}
        onOpenLanguageModal={() => setLanguageModalOpen(true)}
        currentPage={currentPage}
        onNavigate={handleNavigate}
        onStartOnboarding={handleStartOnboarding}
      />

      {/* 3. Page Content Switcher */}
      <div className="flex-1 flex flex-col">
        {currentPage === 'landing' && (
          <LandingPage
            currentLanguage={currentLanguage}
            onStartVoice={handleStartVoice}
            onStartText={handleStartText}
            onNavigate={handleNavigate}
          />
        )}

        {currentPage === 'languages' && (
          <LanguagePage
            currentLanguage={currentLanguage}
            onSelectLanguage={(lang) => {
              handleSelectLanguage(lang);
              setCurrentPage('landing');
            }}
            onBack={() => setCurrentPage('landing')}
          />
        )}

        {currentPage === 'conversation' && (
          <ConversationPage
            currentLanguage={currentLanguage}
            onSelectLanguage={handleSelectLanguage}
            initialPrompt={initialPromptText}
            onCompleteConversation={handleCompleteConversation}
            onNavigate={handleNavigate}
          />
        )}

        {currentPage === 'profile' && (
          <ProfilePage
            userProfile={userProfile}
            onUpdateProfile={setUserProfile}
            onNavigate={handleNavigate}
          />
        )}

        {currentPage === 'opportunities' && (
          <OpportunitiesPage
            currentLanguage={currentLanguage}
            onSelectOpportunity={handleSelectOpportunity}
            onNavigate={handleNavigate}
          />
        )}

        {currentPage === 'details' && (
          <OpportunityDetailsPage
            currentLanguage={currentLanguage}
            opportunity={selectedOpportunity}
            onBack={() => setCurrentPage('opportunities')}
            onStartActionPath={handleStartActionPath}
          />
        )}

        {currentPage === 'action-path' && (
          <ActionPathPage
            currentLanguage={currentLanguage}
            opportunity={selectedOpportunity}
            onNavigate={handleNavigate}
          />
        )}

        {currentPage === 'how-to-use' && (
          <HowToUsePage
            onStartOnboarding={handleStartOnboarding}
            currentLanguage={currentLanguage}
          />
        )}

        {currentPage === 'admin' && (
          <AdminDashboard
            onNavigate={handleNavigate}
          />
        )}
      </div>

      {/* 4. Language Selection Modal Overlay */}
      {languageModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/45 backdrop-blur-xs flex items-center justify-center p-3 sm:p-4">
          <div className="relative bg-[#FAF7F0] rounded-3xl border-2 border-[#b8ded6] max-w-3xl w-full shadow-2xl overflow-hidden animate-in zoom-in-95 duration-200">
            <button
              onClick={() => setLanguageModalOpen(false)}
              className="absolute top-4 right-4 p-2 rounded-full hover:bg-white/80 text-[#718078] hover:text-[#134e40] transition-colors z-30"
              aria-label="Close Language Modal"
            >
              <X className="w-5 h-5" />
            </button>
            <LanguagePage
              currentLanguage={currentLanguage}
              onSelectLanguage={handleSelectLanguage}
              onBack={() => setLanguageModalOpen(false)}
              isModal={true}
            />
          </div>
        </div>
      )}

      {/* 5. Minimal Public Service Footer (Subtle, unobtrusive) */}
      <footer className="relative z-10 py-4 px-4 text-center text-xs text-[#718078]/80 select-none">
        <div className="flex flex-wrap items-center justify-center gap-4 mb-1">
          <button onClick={() => handleNavigate('how-to-use')} className="hover:underline">
            {getUIText('footer', 'aboutUtthan', currentLanguage.id)}
          </button>
          <span>•</span>
          <button onClick={() => handleNavigate('how-to-use')} className="hover:underline">
            {getUIText('footer', 'digitalPublicGoods', currentLanguage.id)}
          </button>
          <span>•</span>
          <button onClick={() => handleNavigate('admin')} className="hover:underline">
            {getUIText('footer', 'nlm', currentLanguage.id)}
          </button>
          <span>•</span>
          <button onClick={() => setLanguageModalOpen(true)} className="hover:underline">
            {getUIText('footer', 'allLanguages', currentLanguage.id)}
          </button>
        </div>
        <p className="text-[11px] text-[#718078]/70">
          {getUIText('footer', 'tagline', currentLanguage.id)}
        </p>
      </footer>
    </div>
  );
}
