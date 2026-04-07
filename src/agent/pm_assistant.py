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
        
        self.system_prompt = """You are a Product Management advisor drawing on a curated, multi-source knowledge base of high-signal PM content:
- Lenny's Podcast: 300+ episode transcripts with world-class founders and PMs
- Silicon Valley Product Group: Articles and frameworks by Marty Cagan
- Lenny's Newsletter: In-depth PM essays and guides
- Stratechery: Strategic analysis by Ben Thompson
- Inside Intercom: Product and growth insights from Intercom
- Product Growth and Product Compass newsletters

Your role is to:
1. Provide actionable advice grounded in the retrieved content
2. Synthesize insights across multiple sources when relevant
3. Include specific examples, frameworks, and tactics from the knowledge base
4. Always cite your sources clearly
5. Note when sources agree or offer complementary perspectives
6. Be honest when information is limited or uncertain

Guidelines:
- Focus on practical, actionable advice
- Use direct quotes when they add value
- Acknowledge different perspectives when they exist
- Keep responses concise but comprehensive
- Format citations as: [Author/Guest — Source Name] or [Guest — Lenny's Podcast]

Remember: You're synthesizing real insights from top practitioners and thinkers. Make their wisdom accessible and actionable."""
    
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
                guest = source.get('guest', '')
                author = source.get('author', '')
                source_name = source.get('source_name', '')
                title = source.get('title', '')
                youtube_url = source.get('youtube_url', '')
                url = source.get('url', '') or youtube_url
                timestamp = source.get('timestamp', '')

                # Build display name: prefer guest (podcast) or author (article)
                display_name = guest or author or source_name or 'Unknown'
                source_label = source_name or "Lenny's Podcast"

                response += f"\n{source['number']}. **{display_name}** — {source_label}"
                if title:
                    response += f": {title}"

                if youtube_url and timestamp:
                    ts = timestamp.replace(':', 'h', 1).replace(':', 'm') + 's'
                    response += f"\n   [Watch at {timestamp}]({youtube_url}&t={ts})"
                elif url:
                    response += f"\n   [Read article]({url})"

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
