import React from 'react';
import { motion } from 'framer-motion';

export default function MicButton({ isRecording, onClick }) {
  // Choix de la classe Tailwind selon l’état
  const bgClass = isRecording ? 'bg-red-500' : 'bg-blue-500';

  return (
    <motion.button
      onClick={onClick}
      className={`
        ${bgClass}
        w-20 h-20 rounded-full
        flex items-center justify-center
        focus:outline-none shadow-lg
      `}
      // On garde la petite pulsation pendant l’enregistrement
      animate={
        isRecording
          ? { scale: [1, 1.1, 1] }
          : {}
      }
      transition={
        isRecording
          ? { repeat: Infinity, repeatType: 'reverse', duration: 1 }
          : {}
      }
    >
      <svg xmlns="http://www.w3.org/2000/svg"
           className="w-10 h-10 text-white"
           fill="currentColor"
           viewBox="0 0 24 24">
        <path d="M12 14a3 3 0 0 0 3-3V5a3 3 0 0 0-6 0v6a3 3 0 0 0 3 3z"/>
        <path d="M19 11v1a7 7 0 0 1-14 0v-1H3v1a9 9 0 0 0 8 8.94V22h2v-1.06A9 9 0 0 0 21 12v-1h-2z"/>
      </svg>
    </motion.button>
  );
}
