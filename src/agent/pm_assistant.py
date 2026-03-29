"""
PM Assistant agent for answering product management questions.
"""
import os
from typing import List, Dict, Optional
from openai import OpenAI
from dotenv import load_dotenv
from ..retrieval.retriever import Retriever

load_dotenv()


class PMAssistant:
    """Product Management Assistant powered by Lenny's Podcast insights."""
    
    def __init__(self, retriever: Retriever, model: str = "gpt-4o-mini"):
        """
        Initialize PM Assistant.
        
        Args:
            retriever: Retriever instance for finding relevant content
            model: OpenAI model to use for chat
        """
        self.retriever = retriever
        self.model = model
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        self.system_prompt = """You are a Product Management advisor powered by insights from Lenny's Podcast, featuring conversations with world-class product leaders, founders, and experts.

Your role is to:
1. Provide actionable advice based on the retrieved transcript excerpts
2. Synthesize insights from multiple sources when relevant
3. Include specific examples, frameworks, and tactics mentioned by the guests
4. Always cite your sources with guest names and episode titles
5. Be honest when information is limited or uncertain

Guidelines:
- Focus on practical, actionable advice
- Use direct quotes when they add value
- Acknowledge different perspectives when they exist
- Keep responses concise but comprehensive
- Format citations as: [Guest Name - Episode Title]

Remember: You're drawing from real conversations with industry leaders. Make their wisdom accessible and actionable."""
    
    def answer_question(self, question: str, conversation_history: Optional[List[Dict]] = None,
                       n_results: int = 5) -> Dict:
        """
        Answer a product management question.
        
        Args:
            question: User's question
            conversation_history: Previous messages in the conversation
            n_results: Number of relevant chunks to retrieve
            
        Returns:
            Dictionary with answer and sources
        """
        # Retrieve relevant context
        retrieval_result = self.retriever.retrieve_with_context(question, n_results)
        context = retrieval_result['context']
        sources = retrieval_result['sources']
        
        # Build messages for OpenAI
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add current question with context
        user_message = f"""Based on the following insights from Lenny's Podcast, please answer this question:

Question: {question}

Relevant Insights:
{context}

Please provide a helpful answer with specific citations."""
        
        messages.append({"role": "user", "content": user_message})
        
        # Generate response
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            answer = response.choices[0].message.content
            
            return {
                'answer': answer,
                'sources': sources,
                'context_used': context
            }
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return {
                'answer': "I apologize, but I encountered an error generating a response. Please try again.",
                'sources': sources,
                'context_used': context
            }
    
    def format_response_with_citations(self, result: Dict) -> str:
        """
        Format the response with citations for display.
        
        Args:
            result: Result dictionary from answer_question
            
        Returns:
            Formatted response string
        """
        response = result['answer']
        
        if result['sources']:
            response += "\n\n---\n\n**Sources:**\n"
            for source in result['sources']:
                response += f"\n{source['number']}. **{source['guest']}** - {source['title']}"
                if source['youtube_url']:
                    # Add timestamp to YouTube URL
                    timestamp = source['timestamp'].replace(':', 'h', 1).replace(':', 'm') + 's'
                    url_with_timestamp = f"{source['youtube_url']}&t={timestamp}"
                    response += f"\n   [Watch at {source['timestamp']}]({url_with_timestamp})"
                response += f"\n   (Relevance: {source['similarity_score']:.1%})\n"
        
        return response
    
    def get_example_questions(self) -> List[str]:
        """Get example questions users can ask."""
        return [
            "How do I find product-market fit?",
            "What are the best practices for user research?",
            "How should I prioritize features on my roadmap?",
            "What makes a great product manager?",
            "How do I build a strong product culture?",
            "What are effective growth strategies for early-stage products?",
            "How do I work effectively with engineering teams?",
            "What frameworks should I use for product strategy?",
            "How do I measure product success?",
            "What are common mistakes in product management?"
        ]


if __name__ == "__main__":
    # Test the PM Assistant
    from ..retrieval.vector_store import VectorStore
    from ..ingestion.embedder import EmbeddingGenerator
    
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found")
        exit(1)
    
    vector_store = VectorStore()
    embedder = EmbeddingGenerator()
    retriever = Retriever(vector_store, embedder)
    assistant = PMAssistant(retriever)
    
    if vector_store.count() == 0:
        print("Vector store is empty. Run ingestion first.")
        exit(1)
    
    # Test question
    question = "How do I find product-market fit?"
    print(f"\nQuestion: {question}\n")
    
    result = assistant.answer_question(question, n_results=3)
    formatted_response = assistant.format_response_with_citations(result)
    
    print(formatted_response)

# Made with Bob
