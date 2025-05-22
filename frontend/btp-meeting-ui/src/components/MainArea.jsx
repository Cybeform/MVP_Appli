// src/components/MainArea.jsx
import React, { useState, useRef } from 'react'
import MicButton from './MicButton'
import {
  startRecording,
  stopRecording,
  fetchRecordings,
} from '../api'

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000'

export default function MainArea({ onNewRecording = () => {} }) {
  const [isRecording,    setIsRecording]    = useState(false)
  const [currentId,      setCurrentId]      = useState(null)
  const [isUploading,    setIsUploading]    = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [isGenerating,   setIsGenerating]   = useState(false)
  const [genProgress,    setGenProgress]    = useState(0)
  const [genStep,        setGenStep]        = useState('')
  const evtRef = useRef(null)

  // 1) Enregistrement live
  const handleMic = async () => {
    if (!isRecording) {
      try {
        const id = await startRecording()
        setCurrentId(id)
        setIsRecording(true)
      } catch {
        alert('Impossible de démarrer l’enregistrement')
      }
    } else {
      try {
        await stopRecording(currentId)
        setIsRecording(false)
        const recs = await fetchRecordings()
        onNewRecording(recs)
      } catch {
        alert('Impossible d’arrêter l’enregistrement')
      }
    }
  }

  // 2) Upload de fichier audio
  const handleUpload = e => {
    const file = e.target.files[0]
    if (!file) return
    setIsUploading(true)
    setUploadProgress(0)

    const xhr = new XMLHttpRequest()
    xhr.open('POST', `${BACKEND_URL}/upload`)
    xhr.upload.onprogress = ev => {
      if (ev.lengthComputable) {
        setUploadProgress(Math.round(ev.loaded * 100 / ev.total))
      }
    }
    xhr.onload = async () => {
      setIsUploading(false)
      setUploadProgress(0)
      if (xhr.status === 200) {
        const { id } = JSON.parse(xhr.responseText)
        setCurrentId(id)
        const recs = await fetchRecordings()
        onNewRecording(recs)
      } else {
        alert(`Erreur upload (${xhr.status}) : ${xhr.responseText}`)
      }
    }
    xhr.onerror = () => {
      setIsUploading(false)
      alert('Erreur réseau durant l’upload')
    }
    const form = new FormData()
    form.append('file', file)
    xhr.send(form)
  }

  // 3) Génération du rapport SSE
  const handleGenerate = () => {
    if (!currentId) return

    if (evtRef.current) {
      evtRef.current.close()
      evtRef.current = null
    }
    setIsGenerating(true)
    setGenProgress(0)
    setGenStep('Diarization')

    const evt = new EventSource(`${BACKEND_URL}/generate-report-stream/${currentId}`)
    evtRef.current = evt

    evt.onmessage = e => {
      const msg = JSON.parse(e.data)
      if (msg.phase === 'error') {
        evt.close()
        alert(`Erreur durant la génération : ${msg.message}`)
        setIsGenerating(false)
        return
      }
      switch (msg.phase) {
        case 'diarization':
          if (msg.status === 'skipped' || msg.status === 'end') {
            setGenStep('Transcription')
            setGenProgress(0)
          }
          break
        case 'transcription':
          setGenStep('Transcription')
          if (msg.total) setGenProgress(Math.round(msg.done * 100 / msg.total))
          break
        case 'summary':
          if (msg.status === 'start') {
            setGenStep('Résumé')
            setGenProgress(0)
          }
          break
        case 'docx':
          if (msg.status === 'start') {
            setGenStep('Génération du rapport')
            setGenProgress(0)
          }
          break
        case 'done':
          evt.close()
          const link = document.createElement('a')
          link.href = `${BACKEND_URL}/download-report/${currentId}`
          link.click()
          setIsGenerating(false)
          break
      }
    }

    evt.onerror = () => {
      if (evtRef.current) {
        evtRef.current.close()
        evtRef.current = null
      }
    }
  }

  return (
    <div className="w-full flex flex-col items-center">
      {/* --- Bandeau supérieur --- */}
      <div className="w-full bg-blue-800 py-4">
        <h2 className="text-center text-white text-lg font-semibold">
          Enregistrement de Réunion
        </h2>
      </div>

      {/* --- Texte descriptif --- */}
      <div className="w-full max-w-md mt-4">
        <div className="bg-blue-600 text-white rounded-lg px-4 py-2 text-center">
          Enregistrez vos réunions et obtenez automatiquement une transcription complète
          avec résumé des points importants.
        </div>
      </div>

      {/* --- Zone principale --- */}
      <div className="bg-blue-900 rounded-2xl p-6 flex flex-col items-center w-full max-w-md space-y-6 mt-6">
        <MicButton
          isRecording={isRecording}
          onClick={handleMic}
        />

        <input
          id="file-upload"
          type="file"
          accept="audio/*"
          className="hidden"
          onChange={handleUpload}
        />
        <label
          htmlFor="file-upload"
          className={`
            inline-flex items-center justify-center
            bg-blue-600 hover:bg-blue-700
            text-white font-semibold
            rounded-full px-6 py-3
            cursor-pointer transition
            ${isUploading ? 'opacity-50 pointer-events-none' : ''}
          `}
        >
          {isUploading
            ? `Téléversement ${uploadProgress}%`
            : 'Importer un fichier audio'}
        </label>

        {!isRecording && currentId && (
          <button
            onClick={handleGenerate}
            disabled={isGenerating}
            className={`
              inline-flex items-center justify-center
              bg-green-500 hover:bg-green-600
              text-white font-semibold
              rounded-full px-6 py-3
              cursor-pointer transition
              ${isGenerating ? 'opacity-50 pointer-events-none' : ''}
            `}
          >
            {isGenerating
              ? `${genStep} ${genProgress > 0 ? `${genProgress}%` : ''}`
              : 'Générer le Rapport (.docx)'}
          </button>
        )}

        {isGenerating && (
          <div className="w-full">
            <p className="text-white text-sm mb-1">{genStep}</p>
            <div className="w-full h-2 bg-blue-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-green-400 transition-all"
                style={{ width: `${genProgress}%` }}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
