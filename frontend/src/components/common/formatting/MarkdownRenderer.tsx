/**
 * Markdown Renderer Component
 * 
 * A component that renders markdown content with proper formatting,
 * supporting text styling, lists, links, and other markdown features.
 */
import React, { useMemo } from 'react';
import {
  Box,
  Link,
  Text,
  ListItem,
  UnorderedList,
  OrderedList,
  Heading,
  Divider,
  useColorModeValue,
} from '@chakra-ui/react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import CodeBlock from './CodeBlock';

interface MarkdownRendererProps {
  /**
   * The markdown content to render
   */
  content: string;
  
  /**
   * Optional className for styling
   */
  className?: string;
}

/**
 * Renders markdown content with proper formatting and components
 */
const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content, className }) => {
  // Text colors
  const linkColor = useColorModeValue('blue.600', 'blue.300');
  const headingColor = useColorModeValue('gray.800', 'gray.100');
  
  // Custom components for markdown rendering
  const components = useMemo(() => ({
    // Headings
    h1: (props: any) => <Heading as="h1" size="xl" mt={6} mb={4} color={headingColor} {...props} />,
    h2: (props: any) => <Heading as="h2" size="lg" mt={5} mb={3} color={headingColor} {...props} />,
    h3: (props: any) => <Heading as="h3" size="md" mt={4} mb={2} color={headingColor} {...props} />,
    h4: (props: any) => <Heading as="h4" size="sm" mt={3} mb={2} color={headingColor} {...props} />,
    h5: (props: any) => <Heading as="h5" size="xs" mt={2} mb={1} color={headingColor} {...props} />,
    h6: (props: any) => <Heading as="h6" size="xs" fontWeight="medium" mt={2} mb={1} color={headingColor} {...props} />,
    
    // Paragraphs and text
    p: (props: any) => <Text mb={4} {...props} />,
    strong: (props: any) => <Text as="strong" fontWeight="bold" {...props} />,
    em: (props: any) => <Text as="em" fontStyle="italic" {...props} />,
    
    // Lists
    ul: (props: any) => <UnorderedList pl={4} mb={4} spacing={1} {...props} />,
    ol: (props: any) => <OrderedList pl={4} mb={4} spacing={1} {...props} />,
    li: (props: any) => <ListItem {...props} />,
    
    // Links
    a: (props: any) => <Link color={linkColor} isExternal {...props} />,
    
    // Horizontal rule
    hr: () => <Divider my={6} />,
    
    // Code blocks and inline code
    code: ({ node, inline, className, children, ...props }: any) => {
      const match = /language-(\w+)/.exec(className || '');
      const language = match ? match[1] : '';
      
      // Check if this is a code block or inline code
      if (!inline) {
        return (
          <CodeBlock
            code={String(children).replace(/\n$/, '')}
            language={language || 'text'}
            showLineNumbers={true}
            wrapLines={true}
          />
        );
      }
      
      // Inline code
      return (
        <Text
          as="code"
          px={1}
          py={0.5}
          bg={useColorModeValue('gray.100', 'gray.700')}
          borderRadius="sm"
          fontFamily="mono"
          fontSize="sm"
          {...props}
        >
          {children}
        </Text>
      );
    },
  }), [headingColor, linkColor]);
  
  return (
    <Box className={className}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={components}
      >
        {content}
      </ReactMarkdown>
    </Box>
  );
};

export default MarkdownRenderer;
