"""
Document processors for knowledge extraction.

AI Agents: Available processors:
- DocumentSummarizer: Extract summaries and key information
- BatchProcessor: Process multiple documents efficiently

Example:
    from processors import DocumentSummarizer
    
    summarizer = DocumentSummarizer()
    result = await summarizer.process(content, metadata)
"""

from .summarizer import DocumentSummarizer, BatchProcessor

__all__ = ["DocumentSummarizer", "BatchProcessor"]