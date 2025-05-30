/**
 * Message Formatter Component
 * 
 * This component orchestrates the formatting of message content,
 * supporting markdown, code blocks, media attachments, and more.
 */
import React from 'react';
import { Box } from '@chakra-ui/react';
import MarkdownRenderer from './MarkdownRenderer';
import MediaAttachment from './MediaAttachment';

interface MessageAttachment {
  /**
   * Type of the attachment
   */
  type: 'image' | 'video' | 'audio' | 'pdf' | 'other';
  
  /**
   * URL of the attachment
   */
  url: string;
  
  /**
   * Name of the file
   */
  fileName?: string;
  
  /**
   * Size of the file in bytes
   */
  fileSize?: number;
}

interface MessageFormatterProps {
  /**
   * Content of the message
   */
  content: string;
  
  /**
   * Attachments for the message
   */
  attachments?: MessageAttachment[];
  
  /**
   * Whether to enable markdown rendering
   */
  enableMarkdown?: boolean;
}

/**
 * Formats message content with support for markdown, code blocks, and attachments
 */
const MessageFormatter: React.FC<MessageFormatterProps> = ({
  content,
  attachments = [],
  enableMarkdown = true,
}) => {
  // Process content to detect and handle special formats
  const processContent = () => {
    // For now, we'll just use the markdown renderer for all content
    if (enableMarkdown) {
      return <MarkdownRenderer content={content} />;
    }
    
    // If markdown is disabled, just render as plain text
    return <Box whiteSpace="pre-wrap">{content}</Box>;
  };

  return (
    <Box width="100%">
      {/* Render the main content */}
      {processContent()}
      
      {/* Render attachments if any */}
      {attachments.length > 0 && (
        <Box mt={3} display="flex" flexWrap="wrap" gap={3}>
          {attachments.map((attachment, index) => (
            <MediaAttachment
              key={`${attachment.url}-${index}`}
              url={attachment.url}
              type={attachment.type}
              fileName={attachment.fileName}
              fileSize={attachment.fileSize}
            />
          ))}
        </Box>
      )}
    </Box>
  );
};

export default MessageFormatter;
