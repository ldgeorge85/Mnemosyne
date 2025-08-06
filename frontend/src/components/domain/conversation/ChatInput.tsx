/**
 * Chat Input Component
 * 
 * A component for typing and sending messages in the chat interface,
 * with support for multiline input, keyboard shortcuts, and attachments.
 */
import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Flex,
  Input,
  IconButton,
  Button,
  useColorModeValue,
  Tooltip,
  HStack,
} from '@chakra-ui/react';
import { FiSend, FiPaperclip } from 'react-icons/fi';

interface ChatInputProps {
  /**
   * Called when a message is submitted
   */
  onSendMessage: (message: string) => void;
  
  /**
   * Whether a message is currently being sent
   */
  isLoading?: boolean;
  
  /**
   * Placeholder text for the input
   */
  placeholder?: string;
  
  /**
   * Maximum height of the input (px)
   */
  maxHeight?: number;
  
  /**
   * Whether to support attachments
   */
  allowAttachments?: boolean;
  
  /**
   * Called when an attachment is added
   */
  onAddAttachment?: (file: File) => void;
}

/**
 * Input component for typing and sending messages
 */
const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  isLoading = false,
  placeholder = 'Type a message...',
  maxHeight = 150,
  allowAttachments = false,
  onAddAttachment,
}) => {
  // State for the input value
  const [message, setMessage] = useState<string>('');
  // Reference to the textarea for focus management
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  // Reference to the file input
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  // Auto-resize the textarea based on content
  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current;
    if (!textarea) return;
    
    // Reset height to auto to get the correct scrollHeight
    textarea.style.height = 'auto';
    
    // Set the height based on scrollHeight, with a maximum
    const newHeight = Math.min(textarea.scrollHeight, maxHeight);
    textarea.style.height = `${newHeight}px`;
  };
  
  // Handle input changes
  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value);
    adjustTextareaHeight();
  };
  
  // Handle key presses (e.g., Enter to send)
  const handleKeyDown = (e: React.KeyboardEvent) => {
    // Ctrl/Cmd + Enter to send message
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      handleSendMessage();
      e.preventDefault();
    }
    
    // Shift + Enter for new line, standard Enter to send
    if (e.key === 'Enter' && !e.shiftKey) {
      handleSendMessage();
      e.preventDefault();
    }
  };
  
  // Handle sending a message
  const handleSendMessage = () => {
    // Don't send empty messages
    const trimmedMessage = message.trim();
    if (!trimmedMessage || isLoading) return;
    
    // Send the message and clear the input
    onSendMessage(trimmedMessage);
    setMessage('');
    
    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
    
    // Focus back on the textarea
    setTimeout(() => {
      textareaRef.current?.focus();
    }, 0);
  };
  
  // Handle file selection
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && onAddAttachment) {
      onAddAttachment(file);
    }
  };
  
  // Trigger file selection dialog
  const openFileDialog = () => {
    fileInputRef.current?.click();
  };
  
  // Focus the textarea on component mount
  useEffect(() => {
    textareaRef.current?.focus();
  }, []);
  
  // Adjust textarea height when message changes
  useEffect(() => {
    adjustTextareaHeight();
  }, [message]);
  
  // Background and border colors
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  
  return (
    <Box
      width="100%"
      borderTop="1px solid"
      borderColor={borderColor}
      p={4}
      bg={bgColor}
      borderBottomRadius="md"
      position="relative"
    >
      <Flex direction="column" width="100%">
        <Box position="relative" width="100%">
          <Input
            ref={textareaRef}
            value={message}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            height="40px"
            borderRadius="md"
            py={2}
            px={4}
            pr={16} // Space for the send button
            focusBorderColor="blue.400"
            isDisabled={isLoading}
            fontSize="md"
            bg={useColorModeValue('gray.50', 'gray.700')}
          />
          
          <HStack position="absolute" right={2} bottom={2}>
            {/* File attachment button */}
            {allowAttachments && (
              <>
                <Tooltip label="Add attachment">
                  <IconButton
                    icon={<FiPaperclip />}
                    aria-label="Add attachment"
                    variant="ghost"
                    size="sm"
                    onClick={openFileDialog}
                    isDisabled={isLoading}
                  />
                </Tooltip>
                <input
                  ref={fileInputRef}
                  type="file"
                  style={{ display: 'none' }}
                  onChange={handleFileSelect}
                  accept="image/*,.pdf,.doc,.docx,.txt"
                />
              </>
            )}
            
            {/* Send button */}
            <Tooltip label="Send message (Ctrl + Enter)">
              <IconButton
                icon={<FiSend />}
                aria-label="Send message"
                colorScheme="blue"
                variant="ghost"
                size="sm"
                onClick={handleSendMessage}
                isDisabled={!message.trim() || isLoading}
              />
            </Tooltip>
          </HStack>
        </Box>
        
        {/* Helper text */}
        <Box mt={1} textAlign="right">
          <Button
            variant="link"
            size="xs"
            fontStyle="italic"
            color={useColorModeValue('gray.500', 'gray.400')}
          >
            Press Enter to send, Shift + Enter for new line
          </Button>
        </Box>
      </Flex>
    </Box>
  );
};

export default ChatInput;
