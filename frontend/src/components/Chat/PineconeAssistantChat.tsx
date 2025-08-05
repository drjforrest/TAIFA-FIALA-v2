'use client'

import { useState, useRef, useEffect } from 'react'
import { MessageCircle, Send, Bot, User, Loader2, Zap } from 'lucide-react'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  loading?: boolean
}

interface PineconeAssistantChatProps {
  innovation?: {
    id: string
    title: string
    description: string
    innovation_type?: string
  }
  assistantName?: string
}

export default function PineconeAssistantChat({ 
  innovation,
  assistantName = "taifa-fiala-assistant" 
}: PineconeAssistantChatProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: innovation 
        ? `Hi! I can help you understand "${innovation.title}" and explore related documents in our African AI knowledge base. What would you like to know?`
        : 'Hi! I can help you explore the African AI innovation ecosystem. Ask me about innovations, research, funding, trends, or any specific topics you\'re interested in.',
      timestamp: new Date()
    }
  ])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage.trim(),
      timestamp: new Date()
    }

    // Add user message and loading assistant message
    const loadingMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: 'Thinking...',
      timestamp: new Date(),
      loading: true
    }

    setMessages(prev => [...prev, userMessage, loadingMessage])
    setInputMessage('')
    setIsLoading(true)

    try {
      // Call the Pinecone Assistant API
      const response = await fetch('/api/chat/assistant', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          assistant_name: assistantName,
          message: inputMessage.trim(),
          context_filter: innovation ? { innovation_id: innovation.id } : undefined,
          innovation_context: innovation || undefined
        }),
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`)
      }

      // For now, we'll simulate a response since the actual API isn't implemented yet
      const mockResponse = generateMockResponse(inputMessage.trim(), innovation)
      
      // Remove loading message and add real response
      setMessages(prev => {
        const withoutLoading = prev.filter(msg => !msg.loading)
        return [...withoutLoading, {
          id: Date.now().toString(),
          role: 'assistant',
          content: mockResponse,
          timestamp: new Date()
        }]
      })

    } catch (error) {
      console.error('Error sending message:', error)
      
      // Remove loading message and add error message
      setMessages(prev => {
        const withoutLoading = prev.filter(msg => !msg.loading)
        return [...withoutLoading, {
          id: Date.now().toString(),
          role: 'assistant',
          content: "I'm sorry, I'm having trouble connecting to the knowledge base right now. Please try again later.",
          timestamp: new Date()
        }]
      })
    } finally {
      setIsLoading(false)
    }
  }

  const generateMockResponse = (message: string, innovation?: any): string => {
    const lowerMessage = message.toLowerCase()
    
    if (innovation) {
      if (lowerMessage.includes('funding') || lowerMessage.includes('money') || lowerMessage.includes('investment')) {
        return `Based on our knowledge base, here's what I found about funding for ${innovation.title}:\n\n• This innovation is in the ${innovation.innovation_type} space, which has seen significant investment growth in Africa\n• Similar innovations in this domain typically receive seed funding between $100K - $2M\n• Key funding sources include local VCs, international development funds, and government innovation grants\n\nWould you like me to search for specific funding opportunities or similar successful cases?`
      }
      
      if (lowerMessage.includes('similar') || lowerMessage.includes('related') || lowerMessage.includes('like this')) {
        return `I found several innovations related to ${innovation.title} in our database:\n\n• Other ${innovation.innovation_type} solutions across Africa\n• Innovations addressing similar challenges\n• Projects by organizations in the same ecosystem\n\nWould you like me to provide more details about any specific similar innovations?`
      }
      
      if (lowerMessage.includes('impact') || lowerMessage.includes('users') || lowerMessage.includes('success')) {
        return `Regarding the impact of ${innovation.title}:\n\n• This type of innovation typically serves communities across multiple African countries\n• Similar solutions have shown measurable social and economic impact\n• Success metrics often include user adoption, revenue generation, and job creation\n\nBased on the innovation's description, it appears to focus on ${innovation.description.slice(0, 100)}...\n\nWould you like me to find specific impact data from similar innovations?`
      }
    }
    
    // General responses
    if (lowerMessage.includes('trend') || lowerMessage.includes('popular') || lowerMessage.includes('growing')) {
      return `Based on our African AI innovation database, here are the current trends:\n\n• **Healthcare AI** is the fastest-growing domain (23.5% of innovations)\n• **AgriTech** and **FinTech** are also major focus areas\n• **Nigeria, Kenya, and South Africa** lead in innovation volume\n• **Cross-border collaboration** is increasing significantly\n\nWould you like me to dive deeper into any of these trends?`
    }
    
    if (lowerMessage.includes('research') || lowerMessage.includes('publication') || lowerMessage.includes('paper')) {
      return `Our knowledge base contains extensive research from across Africa:\n\n• Academic publications from top African universities\n• Research papers on AI applications in African contexts\n• Conference proceedings from major tech events\n• Collaboration networks between researchers and innovators\n\nWhat specific research topic interests you most?`
    }
    
    // Default response
    return `I understand you're asking about "${message}". Let me search our comprehensive African AI knowledge base for relevant information.\n\n• **Innovation Database**: 1,200+ documented AI projects\n• **Research Papers**: 800+ publications\n• **Funding Data**: Investment trends and opportunities\n• **Geographic Coverage**: 15+ African countries\n\nCould you be more specific about what aspect you'd like to explore? For example:\n- Funding opportunities\n- Similar innovations\n- Research papers\n- Market trends\n- Technical details`
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const formatTimestamp = (timestamp: Date) => {
    return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div className="flex flex-col h-[600px] border rounded-lg" style={{ backgroundColor: "var(--color-card)", borderColor: "var(--color-border)" }}>
      {/* Chat Header */}
      <div className="flex items-center justify-between p-4 border-b" style={{ borderColor: "var(--color-border)", backgroundColor: "var(--color-muted)" }}>
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-full flex items-center justify-center" style={{ backgroundColor: "var(--color-primary)" }}>
            <MessageCircle className="h-5 w-5" style={{ color: "var(--color-primary-foreground)" }} />
          </div>
          <div>
            <h3 className="font-semibold" style={{ color: "var(--color-card-foreground)" }}>
              AI Assistant
            </h3>
            <p className="text-sm" style={{ color: "var(--color-muted-foreground)" }}>
              {innovation ? `Context: ${innovation.title}` : 'African AI Knowledge Base'}
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-1 text-xs px-2 py-1 rounded-full" style={{ backgroundColor: "var(--color-primary)", color: "var(--color-primary-foreground)" }}>
          <Zap className="h-3 w-3" />
          <span>Powered by Pinecone</span>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div key={message.id} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`flex items-start space-x-2 max-w-[80%] ${message.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
              {/* Avatar */}
              <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                message.role === 'user' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-600 text-white'
              }`}>
                {message.role === 'user' ? (
                  <User className="h-4 w-4" />
                ) : message.loading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Bot className="h-4 w-4" />
                )}
              </div>

              {/* Message Content */}
              <div className={`rounded-lg p-3 ${
                message.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : message.loading
                    ? 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400'
                    : 'bg-gray-100 dark:bg-gray-800'
              }`} style={message.role === 'assistant' && !message.loading ? {
                backgroundColor: "var(--color-muted)",
                color: "var(--color-card-foreground)"
              } : {}}>
                <div className="whitespace-pre-wrap break-words">
                  {message.content}
                </div>
                <div className={`text-xs mt-1 opacity-70 ${message.role === 'user' ? 'text-blue-100' : 'text-gray-500'}`}>
                  {formatTimestamp(message.timestamp)}
                </div>
              </div>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t" style={{ borderColor: "var(--color-border)" }}>
        <div className="flex space-x-2">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about this innovation or explore the knowledge base..."
            disabled={isLoading}
            className="flex-1 px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
            style={{
              backgroundColor: "var(--color-background)",
              borderColor: "var(--color-border)",
              color: "var(--color-foreground)"
            }}
          />
          <button
            onClick={sendMessage}
            disabled={!inputMessage.trim() || isLoading}
            className="px-4 py-2 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            style={{
              backgroundColor: "var(--color-primary)",
              color: "var(--color-primary-foreground)"
            }}
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </button>
        </div>
        <p className="text-xs mt-2" style={{ color: "var(--color-muted-foreground)" }}>
          Press Enter to send, Shift+Enter for new line
        </p>
      </div>
    </div>
  )
}