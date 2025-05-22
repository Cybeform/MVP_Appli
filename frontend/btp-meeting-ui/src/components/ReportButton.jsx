import React from 'react';

export default function ReportButton({ onClick }) {
  return (
    <button
      onClick={onClick}
      className="mt-4 px-6 py-3 rounded-full bg-green-400 text-black font-semibold flex items-center hover:opacity-90 transition-opacity shadow"
    >
      <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
        <path d="M12 16l-4-4h3V4h2v8h3l-4 4z"/>
        <path d="M5 20h14v2H5z"/>
      </svg>
      Générer le Rapport (.docx)
    </button>
  );
}
