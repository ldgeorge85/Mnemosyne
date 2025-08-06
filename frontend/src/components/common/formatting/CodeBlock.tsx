/**
 * Code Block Component
 * 
 * A component that renders code blocks with syntax highlighting.
 * Supports various programming languages and includes copy functionality.
 */
import React, { useState } from 'react';
import {
  Box,
  Flex,
  Text,
  IconButton,
  useColorModeValue,
  Tooltip,
  useToast,
} from '@chakra-ui/react';
import { FiCopy, FiCheck } from 'react-icons/fi';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow, oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface CodeBlockProps {
  /**
   * The code to display
   */
  code: string;

  /**
   * The programming language for syntax highlighting
   */
  language?: string;

  /**
   * Whether to show line numbers
   */
  showLineNumbers?: boolean;

  /**
   * Whether to wrap long lines
   */
  wrapLines?: boolean;
}

/**
 * A component for displaying code blocks with syntax highlighting
 */
const CodeBlock: React.FC<CodeBlockProps> = ({
  code,
  language = 'javascript',
  showLineNumbers = true,
  wrapLines = true,
}) => {
  // State for tracking copy button status
  const [isCopied, setIsCopied] = useState(false);
  
  // Toast for notifications
  const toast = useToast();
  
  // Theme colors
  const bgColor = useColorModeValue('gray.50', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const headerBgColor = useColorModeValue('gray.100', 'gray.800');
  
  // Choose the right theme based on color mode
  const codeStyle = useColorModeValue(oneLight, tomorrow);
  
  /**
   * Handle copying code to clipboard
   */
  const handleCopyCode = () => {
    navigator.clipboard.writeText(code);
    setIsCopied(true);
    
    toast({
      title: 'Code copied to clipboard',
      status: 'success',
      duration: 2000,
      isClosable: true,
    });
    
    // Reset the copied state after 2 seconds
    setTimeout(() => {
      setIsCopied(false);
    }, 2000);
  };
  
  return (
    <Box
      borderRadius="md"
      border="1px solid"
      borderColor={borderColor}
      mb={4}
      overflow="hidden"
    >
      {/* Code header with language indicator and copy button */}
      <Flex
        justify="space-between"
        align="center"
        bg={headerBgColor}
        px={4}
        py={2}
        borderBottom="1px solid"
        borderColor={borderColor}
      >
        <Text fontSize="sm" fontWeight="medium">
          {language.toUpperCase()}
        </Text>
        <Tooltip label={isCopied ? 'Copied!' : 'Copy code'}>
          <IconButton
            icon={isCopied ? <FiCheck /> : <FiCopy />}
            size="sm"
            aria-label="Copy code"
            onClick={handleCopyCode}
            variant="ghost"
            colorScheme={isCopied ? 'green' : 'gray'}
          />
        </Tooltip>
      </Flex>
      
      {/* Code content with syntax highlighting */}
      <Box overflow="auto" maxH="400px">
        <SyntaxHighlighter
          language={language}
          style={codeStyle}
          showLineNumbers={showLineNumbers}
          wrapLines={wrapLines}
          customStyle={{
            margin: 0,
            padding: '1rem',
            backgroundColor: 'transparent',
          }}
        >
          {code}
        </SyntaxHighlighter>
      </Box>
    </Box>
  );
};

export default CodeBlock;
