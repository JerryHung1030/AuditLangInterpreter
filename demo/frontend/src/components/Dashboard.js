import React from 'react';
import 'tailwindcss/tailwind.css';
import { useNavigate } from 'react-router-dom';
import 'tw-elements/css/tw-elements.min.css';

const highlights = [
  {
    number: '1',
    text: 'Descriptive Language',
    description: 'Redefining the language for compliance script descriptions.',
    bgColor: 'bg-blue-800',
  },
  {
    number: '5',
    text: 'Targets Supported',
    description: 'File, Directory, Registry, and Process; others use command output comparisons.',
    bgColor: 'bg-blue-700',
  },
  {
    number: '16x',
    text: 'Efficiency',
    description: 'Reduces task time from a full day to just 30 minutes.',
    bgColor: 'bg-blue-600',
  },
  {
    number: '20x',
    text: 'Code Reduction',
    description: 'Simplifies scripts from 100 lines down to just 5.',
    bgColor: 'bg-blue-500',
  },
];

const Dashboard = () => {
  const navigate = useNavigate();

  const handleButtonClick = () => {
    navigate('/prototype'); // Navigate to the prototype page
  };

  return (
    <div
      className="flex items-start justify-center min-h-screen bg-gray-900 pt-4"
      style={{ fontFamily: 'MonoLisa' }}
    >
      <div className="relative bg-gradient-to-br from-gray-900 via-gray-900 via-45% to-blue-700 rounded-3xl p-8 shadow-lg w-full max-w-custom mx-4 overflow-hidden">
        <div className="absolute inset-0 opacity-25">
          <div className="bg-gradient-to-br from-gray-900 to-gray-600 h-full w-full animate-pulse"></div>
        </div>
        <div
          className="relative p-8 flex flex-col lg:flex-row items-center lg:items-stretch w-full"
          style={{ minHeight: '600px' }}
        >
          <div className="lg:w-7/12 text-center lg:text-left flex flex-col justify-center pr-8 border-r border-gray-700">
            <h1 className="text-6xl font-bold mb-4 text-yellow-200">
              SecAuditRuleEngine+
            </h1>
            <div className="mb-4">
              <p
                className="text-2xl mb-2 text-yellow-100"
                style={{ fontFamily: 'MonoLisaScript' }}
              >
                <strong>CSTI-Intern:</strong> Bolt
              </p>
              <p
                className="text-2xl mb-2 text-yellow-100"
                style={{ fontFamily: 'MonoLisaScript' }}
              >
                <strong>Advisor:</strong> Jerryhung, Dickson
              </p>
            </div>
            <p className="text-4xl text-blue-300 mb-4">
              Advanced Automated Audit Script Writing with{' '}
              <span className="gradient-text">Descriptive Language</span> and{' '}
              <span className="gradient-text">GenAI Integration</span>.
            </p>
            {/* Add animation to button */}
            <div className="mt-6">
            <button
                onClick={handleButtonClick} // Update button to navigate
                className="px-6 py-3 bg-yellow-500 text-gray-900 font-bold rounded-full shadow-md hover:bg-yellow-400 transition duration-300 transform hover:scale-110"
              >
                Let's Try This
              </button>
            </div>
          </div>
          <div className="lg:w-10/18 mt-6 lg:mt-0 grid grid-cols-2 gap-8">
            {highlights.map((highlight, index) => (
              <div
                key={index}
                className={`${highlight.bgColor} text-white rounded-lg shadow-lg flex flex-col items-center justify-center transform transition-all duration-300 hover:scale-105`}
                style={{ width: '19rem', height: '12rem' }}
              >
                <div className="text-center w-full h-full relative flex flex-col justify-between p-4">
                  <div>
                    <p className="text-6xl font-bold text-yellow-300">
                      {highlight.number}
                    </p>
                    <p className="text-xl text-yellow-300 whitespace-normal break-words">
                      {highlight.text}
                    </p>
                  </div>
                  <div
                    className="text-sm mt-1 p-2 rounded-lg bg-opacity-90"
                    style={{
                      backgroundColor: highlight.bgColor,
                      color: 'white',
                    }}
                  >
                    {highlight.description}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
