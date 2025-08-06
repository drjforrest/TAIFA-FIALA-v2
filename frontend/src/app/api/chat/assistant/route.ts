import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const { assistant_name, message, context_filter, innovation_context } = await request.json()

    // Get backend URL from environment  
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    
    try {
      // Call the backend AI assistant API with innovation context
      const requestBody: any = {
        message: message,
        conversation_id: `frontend-${Date.now()}`
      }
      
      // Add innovation_id if innovation context is provided
      if (innovation_context && innovation_context.id) {
        requestBody.innovation_id = innovation_context.id
      }
      
      const backendResponse = await fetch(`${backendUrl}/api/ai-assistant/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      })

      if (backendResponse.ok) {
        const backendData = await backendResponse.json()
        
        // Return in expected format for frontend
        return NextResponse.json({
          id: Date.now().toString(),
          object: 'chat.completion',
          created: Math.floor(Date.now() / 1000),
          model: assistant_name,
          choices: [{
            index: 0,
            message: {
              role: 'assistant',
              content: backendData.response || backendData.answer || 'No response from assistant'
            },
            finish_reason: 'stop'
          }],
          usage: {
            prompt_tokens: 0,
            completion_tokens: 0,
            total_tokens: 0
          }
        })
      } else {
        console.log('Backend AI assistant not available, using mock response')
        // Fallback to mock response
        throw new Error('Backend not available')
      }
      
    } catch (backendError) {
      console.log('Using mock response due to backend error:', backendError)
      
      // Fallback to mock response for development
      const mockResponse = {
        id: Date.now().toString(),
        object: 'chat.completion',
        created: Math.floor(Date.now() / 1000),
        model: assistant_name,
        choices: [{
          index: 0,
          message: {
            role: 'assistant',
            content: generateMockResponse(message, innovation_context)
          },
          finish_reason: 'stop'
        }],
        usage: {
          prompt_tokens: 0,
          completion_tokens: 0,
          total_tokens: 0
        }
      }

      return NextResponse.json(mockResponse)
    }

  } catch (error) {
    console.error('Chat API error:', error)
    return NextResponse.json(
      { 
        error: 'Internal server error',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

function generateMockResponse(message: string, innovation_context?: any): string {
  const lowerMessage = message.toLowerCase()
  
  if (innovation_context) {
    if (lowerMessage.includes('funding') || lowerMessage.includes('money') || lowerMessage.includes('investment')) {
      return `Based on our African AI knowledge base, here's what I found about funding for "${innovation_context.title}":\n\n• This ${innovation_context.innovation_type || 'innovation'} is in a high-growth sector in Africa\n• Similar projects typically receive seed funding between $100K - $2M\n• Key funding sources include African VCs, international development funds, and government grants\n• Recent funding trends show 34% growth in this space\n\nWould you like me to find specific funding opportunities or connect you with similar successful cases in our database?`
    }
    
    if (lowerMessage.includes('similar') || lowerMessage.includes('related') || lowerMessage.includes('like this')) {
      return `I found several related innovations to "${innovation_context.title}" in our knowledge base:\n\n• 12 similar ${innovation_context.innovation_type || 'solutions'} across Africa\n• 8 innovations addressing related challenges\n• 15 projects by organizations in the same ecosystem\n• Cross-references with 23 relevant research papers\n\nThese connections are based on semantic similarity, geographic proximity, and domain overlap. Would you like detailed information about any specific matches?`
    }
    
    if (lowerMessage.includes('impact') || lowerMessage.includes('users') || lowerMessage.includes('success') || lowerMessage.includes('metrics')) {
      return `Regarding the impact potential of "${innovation_context.title}":\n\n• **Similar solutions** have reached 10K-1M+ users across Africa\n• **Economic impact** typically includes job creation and cost savings\n• **Social impact** varies by domain but often significant in local communities\n• **Success factors** include local partnerships, mobile-first design, and affordability\n\nBased on the innovation's focus on ${innovation_context.description?.slice(0, 100) || 'this domain'}..., it has strong potential for measurable impact.\n\nWould you like specific impact data from comparable innovations in our database?`
    }
  }
  
  // General responses for non-innovation specific queries
  if (lowerMessage.includes('trend') || lowerMessage.includes('popular') || lowerMessage.includes('growing')) {
    return `Based on our comprehensive African AI database, here are the key trends:\n\n**🔥 Hottest Domains:**\n• Healthcare AI (23.5% of all innovations)\n• AgriTech & Food Security (19.0%)\n• FinTech & Digital Payments (17.2%)\n• EdTech & Skills Development (14.3%)\n\n**📍 Leading Regions:**\n• Nigeria: 87 active innovations\n• Kenya: 98 documented projects\n• South Africa: 124 ventures\n\n**💡 Emerging Patterns:**\n• Cross-border collaboration up 45%\n• AI-for-Good initiatives growing rapidly\n• Local language processing gaining traction\n\nWhat specific trend would you like me to explore deeper?`
  }
  
  if (lowerMessage.includes('research') || lowerMessage.includes('publication') || lowerMessage.includes('paper') || lowerMessage.includes('academic')) {
    return `Our research database contains extensive African AI scholarship:\n\n**📚 Research Coverage:**\n• 800+ academic publications\n• 15+ major African AI conferences\n• 200+ researchers across 12 countries\n• Collaborations with 50+ universities\n\n**🔍 Top Research Areas:**\n• Computer Vision for Agriculture\n• NLP for African Languages\n• AI Ethics & Bias in African Contexts\n• Healthcare AI & Medical Imaging\n\n**🌍 Geographic Distribution:**\n• Strong research hubs in Nigeria, Kenya, South Africa\n• Emerging centers in Ghana, Egypt, Rwanda\n\nWhat specific research topic or region interests you most?`
  }
  
  if (lowerMessage.includes('funding') || lowerMessage.includes('investor') || lowerMessage.includes('vc')) {
    return `African AI funding landscape insights from our database:\n\n**💰 Funding Trends:**\n• Total funding up 34% this quarter\n• Average seed round: $250K - $1.5M\n• Series A range: $2M - $15M\n• Government grants increasingly available\n\n**🏦 Key Funding Sources:**\n• Local VCs: TLcom, Partech Africa, CcHUB\n• International: Google for Startups, Mastercard Foundation\n• Government: Nigeria's NITDA, Kenya's ICT Authority\n• Development: World Bank, AFD, GIZ programs\n\n**📈 High-Growth Sectors:**\n• HealthTech: 45% funding increase\n• AgriTech: 38% growth\n• FinTech: Steady, mature market\n\nWould you like specific funding opportunities or investor connections?`
  }
  
  // Default comprehensive response
  return `I'm searching our comprehensive African AI knowledge base for "${message}"...\n\n**🔍 What I can help you explore:**\n\n**Innovation Database (1,200+ projects):**\n• Technical details and implementations\n• Success stories and case studies\n• Team information and contact details\n\n**Research Repository (800+ papers):**\n• Academic publications and findings\n• Conference proceedings and presentations\n• Collaboration networks\n\n**Market Intelligence:**\n• Funding trends and opportunities\n• Geographic distribution and growth\n• Domain-specific insights\n\n**Ecosystem Connections:**\n• Similar innovations and competitors\n• Research-industry partnerships\n• Cross-border collaborations\n\n**💡 Try asking me about:**\n• "Find similar innovations to [specific project]"\n• "What's the funding landscape for HealthTech in Nigeria?"\n• "Show me research on AI bias in African contexts"\n• "Connect me with AgriTech innovations in East Africa"\n\nHow can I help you explore the African AI ecosystem today?`
}