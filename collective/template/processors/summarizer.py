"""
Document summarizer using LangChain.

AI Agents: This processor handles document summarization and extraction.
It uses source-specific prompts when available.
"""

import os
from typing import Dict, Any, Optional
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import structlog

logger = structlog.get_logger()


class DocumentSummarizer:
    """
    Summarizes and extracts information from documents.
    
    AI Agents: Key features:
    - Uses source-specific prompts
    - Extracts structured information
    - Preserves metadata
    """
    
    def __init__(self, model: str = None, temperature: float = None):
        """
        Initialize summarizer with LLM.
        
        Args:
            model: OpenAI model name (defaults to LLM_MODEL env var)
            temperature: Generation temperature (defaults to 0.7)
        """
        self.model = model or os.getenv("LLM_MODEL", "gpt-4")
        self.temperature = temperature or float(os.getenv("LLM_TEMPERATURE", "0.7"))
        
        self.llm = ChatOpenAI(
            model=self.model,
            temperature=self.temperature
        )
        
    async def process(
        self, 
        content: str, 
        metadata: Dict[str, Any],
        prompt_template: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process document content with appropriate prompt.
        
        Args:
            content: Document text
            metadata: Document metadata (title, source, etc.)
            prompt_template: Specific prompt to use
            
        Returns:
            Processed document with summary and extractions
            
        Example:
            result = await summarizer.process(
                content=doc["text"],
                metadata={"title": doc["title"], "id": doc["id"]}
            )
        """
        if not content:
            return metadata
            
        # Get appropriate prompt
        if not prompt_template:
            prompt_template = self._get_default_prompt()
            
        # Format prompt with content
        prompt = prompt_template.format(
            title=metadata.get("title", "Document"),
            text=content[:4000]  # Limit content length
        )
        
        try:
            # Generate summary/extraction
            messages = [
                SystemMessage(content="You are a knowledge extraction assistant. Extract structured information from documents."),
                HumanMessage(content=prompt)
            ]
            
            response = await self.llm.apredict_messages(messages)
            
            # Parse response (in production, use structured output)
            result = {
                **metadata,
                "original_content": content[:1000],  # Keep preview
                "processed": response.content,
                "summary": self._extract_section(response.content, "Main Purpose"),
                "key_concepts": self._extract_section(response.content, "Key Concepts"),
                "action_items": self._extract_section(response.content, "Action Items"),
                "technical_details": self._extract_section(response.content, "Technical Details")
            }
            
            logger.info(f"Processed document: {metadata.get('title', 'Unknown')}")
            return result
            
        except Exception as e:
            logger.error(f"Processing failed for document", error=str(e))
            # Return original with error
            return {
                **metadata,
                "original_content": content[:1000],
                "processing_error": str(e)
            }
    
    def _get_default_prompt(self) -> str:
        """Get default processing prompt."""
        return """
Analyze this document and extract key information:

Title: {title}
Content: {text}

Please extract:
1. **Main Purpose**: What is this document about? (2-3 sentences)
2. **Key Concepts**: Important terms, systems, or ideas (bullet points)
3. **Action Items**: Any procedures, steps, or tasks described
4. **Technical Details**: APIs, configurations, code examples

Format each section clearly with the heading followed by the content.
"""
    
    def _extract_section(self, text: str, section: str) -> str:
        """
        Extract a specific section from structured text.
        
        Simple extraction - in production use better parsing.
        """
        lines = text.split('\n')
        in_section = False
        section_content = []
        
        for line in lines:
            if section in line and "**" in line:
                in_section = True
                continue
            elif in_section and "**" in line and ":" in line:
                # Hit next section
                break
            elif in_section and line.strip():
                section_content.append(line.strip())
        
        return " ".join(section_content)


class BatchProcessor:
    """
    Process multiple documents in batches.
    
    AI Agents: Use this for bulk processing.
    """
    
    def __init__(self, summarizer: DocumentSummarizer = None):
        self.summarizer = summarizer or DocumentSummarizer()
        
    async def process_batch(
        self, 
        documents: List[Dict[str, Any]], 
        batch_size: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Process documents in batches.
        
        Args:
            documents: List of documents to process
            batch_size: Documents per batch
            
        Returns:
            Processed documents
        """
        processed = []
        
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            
            # Process batch concurrently
            batch_results = []
            for doc in batch:
                result = await self.summarizer.process(
                    content=doc.get("text") or doc.get("content", ""),
                    metadata=doc
                )
                batch_results.append(result)
            
            processed.extend(batch_results)
            logger.info(f"Processed batch {i//batch_size + 1}, total: {len(processed)}")
        
        return processed