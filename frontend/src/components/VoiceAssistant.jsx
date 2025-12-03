import React, { useState, useEffect, useRef } from 'react'
import './VoiceAssistant.css'
import { processVoiceCommand } from '../services/api'

const VoiceAssistant = ({ onInventoryUpdate, onRecipeUpdate, onShoppingListUpdate }) => {
  const [isListening, setIsListening] = useState(false)
  const [response, setResponse] = useState('')
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [transcript, setTranscript] = useState('')
  const recognitionRef = useRef(null)
  const synthRef = useRef(window.speechSynthesis)

  // Initialize speech recognition
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    
    if (!SpeechRecognition) {
      console.warn('Speech recognition not supported in this browser')
      return
    }

    const recognition = new SpeechRecognition()
    recognition.continuous = false
    recognition.interimResults = false
    recognition.lang = 'en-US'

    recognition.onresult = async (event) => {
      const transcript = event.results[0][0].transcript
      setTranscript(transcript)
      await handleVoiceCommand(transcript)
    }

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error)
      setIsListening(false)
      setResponse('Sorry, I had trouble understanding. Please try again.')
    }

    recognition.onend = () => {
      setIsListening(false)
    }

    recognitionRef.current = recognition

    return () => {
      if (recognition) {
        recognition.abort()
      }
    }
  }, [])

  const handleVoiceCommand = async (text) => {
    try {
      const data = await processVoiceCommand(text)
      setResponse(data.text)
      
      // Speak the response
      speakText(data.text)
      
      // Update relevant sections based on action
      if (data.action === 'inventory_updated') {
        onInventoryUpdate()
      } else if (data.action === 'recipe_suggested') {
        onRecipeUpdate(data.data)
      } else if (data.action === 'shopping_list') {
        onShoppingListUpdate()
      } else if (data.action === 'inventory_list') {
        onInventoryUpdate()
      }
    } catch (error) {
      console.error('Error processing voice command:', error)
      const errorMsg = 'Sorry, I encountered an error processing your request.'
      setResponse(errorMsg)
      speakText(errorMsg)
    }
  }

  const speakText = (text) => {
    if (!synthRef.current) return

    // Cancel any ongoing speech
    synthRef.current.cancel()

    const utterance = new SpeechSynthesisUtterance(text)
    utterance.rate = 0.9
    utterance.pitch = 1
    utterance.volume = 1

    utterance.onstart = () => {
      setIsSpeaking(true)
    }

    utterance.onend = () => {
      setIsSpeaking(false)
    }

    utterance.onerror = (event) => {
      console.error('Speech synthesis error:', event.error)
      setIsSpeaking(false)
    }

    synthRef.current.speak(utterance)
  }

  const startListening = () => {
    if (!recognitionRef.current) {
      setResponse('Speech recognition is not supported in your browser. Please use the text input instead.')
      return
    }

    if (isListening) {
      recognitionRef.current.stop()
      setIsListening(false)
      return
    }

    try {
      setTranscript('')
      setResponse('')
      setIsListening(true)
      recognitionRef.current.start()
    } catch (error) {
      console.error('Error starting recognition:', error)
      setIsListening(false)
    }
  }

  const stopSpeaking = () => {
    if (synthRef.current) {
      synthRef.current.cancel()
      setIsSpeaking(false)
    }
  }

  const handleTextSubmit = async (e) => {
    e.preventDefault()
    const formData = new FormData(e.target)
    const text = formData.get('command')
    
    if (!text.trim()) return

    setTranscript(text)
    await handleVoiceCommand(text)
    e.target.reset()
  }

  return (
    <div className="voice-assistant">
      <div className="voice-assistant-header">
        <h2>🎤 Voice Assistant</h2>
        <div className="voice-controls">
          <button
            className={`mic-button ${isListening ? 'listening' : ''}`}
            onClick={startListening}
            disabled={isSpeaking}
          >
            {isListening ? '🛑 Stop Listening' : '🎤 Start Voice'}
          </button>
          {isSpeaking && (
            <button className="stop-button" onClick={stopSpeaking}>
              🔇 Stop Speaking
            </button>
          )}
        </div>
      </div>

      <form onSubmit={handleTextSubmit} className="text-input-form">
        <input
          type="text"
          name="command"
          placeholder="Type or say: 'Add flour to inventory', 'Suggest a recipe', etc."
          className="command-input"
        />
        <button type="submit" className="submit-button">Send</button>
      </form>

      {transcript && (
        <div className="transcript">
          <strong>You said:</strong> {transcript}
        </div>
      )}

      {response && (
        <div className={`response ${isSpeaking ? 'speaking' : ''}`}>
          <strong>Assistant:</strong> {response}
        </div>
      )}

      <div className="voice-help">
        <details>
          <summary>Supported Commands</summary>
          <ul>
            <li>"Add [item] to inventory" - Add an item</li>
            <li>"Add 2 cups of flour to inventory" - Add with quantity</li>
            <li>"Remove [item] from inventory" - Remove an item</li>
            <li>"Update [item] quantity to [amount]" - Update quantity</li>
            <li>"Suggest a recipe" - Get recipe suggestion</li>
            <li>"What's my shopping list?" - Get shopping list</li>
            <li>"What ingredients do I have?" - Show inventory</li>
          </ul>
        </details>
      </div>
    </div>
  )
}

export default VoiceAssistant













