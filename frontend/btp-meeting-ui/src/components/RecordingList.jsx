import React from 'react';

export default function RecordingList({ recordings }) {
  return (
    <div className="p-4">
      <h2 className="text-lg font-semibold mb-2">Enregistrements récents</h2>
      <ul className="space-y-2">
        {recordings.map(rec => (
          <li
            key={rec.id}
            className="bg-blue-800 rounded-lg p-3 flex justify-between items-center"
          >
            <div>
              <div className="font-medium">{rec.title}</div>
              <div className="text-sm text-blue-300">
                {rec.date} • {rec.duration}
              </div>
            </div>
            <button>
              <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6 text-blue-400" fill="currentColor" viewBox="0 0 24 24">
                <path d="M8 5v14l11-7z"/>
              </svg>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
