/**
 * Typing Indicator Component
 * 
 * This component displays an animated typing indicator to show when
 * the AI agent is composing a response.
 */
import React from 'react';
import {
  Box,
  Flex,
  Avatar,
  keyframes,
  useColorModeValue,
} from '@chakra-ui/react';

interface TypingIndicatorProps {
  /**
   * Name to display for the avatar
   */
  name?: string;
  
  /**
   * Duration of the animation in seconds
   */
  animationDuration?: number;
}

/**
 * Displays an animated typing indicator with bouncing dots
 */
const TypingIndicator: React.FC<TypingIndicatorProps> = ({
  name = 'Assistant',
  animationDuration = 1.5,
}) => {
  // Create bounce animation keyframes
  const bounce = keyframes`
    0%, 80%, 100% { 
      transform: translateY(0);
    }
    40% { 
      transform: translateY(-6px);
    }
  `;

  // Animation styles for each dot with delay
  const dotAnimation = (delay: number) => ({
    animation: `${bounce} ${animationDuration}s infinite ease-in-out`,
    animationDelay: `${delay}s`,
  });

  // Colors
  const bgColor = useColorModeValue('gray.100', 'gray.700');
  const dotColor = useColorModeValue('blue.500', 'blue.300');
  
  return (
    <Flex align="center" mb={4}>
      <Avatar
        size="sm"
        name={name}
        bg="gray.500"
        color="white"
        fontSize="sm"
        mr={2}
      >
        A
      </Avatar>
      <Box
        borderRadius="lg"
        px={4}
        py={3}
        bg={bgColor}
        display="inline-flex"
        alignItems="center"
      >
        <Flex align="center">
          {/* Three bouncing dots */}
          {[0, 0.15, 0.3].map((delay, index) => (
            <Box
              key={index}
              h="8px"
              w="8px"
              borderRadius="full"
              bg={dotColor}
              mx="2px"
              sx={dotAnimation(delay)}
            />
          ))}
        </Flex>
      </Box>
    </Flex>
  );
};

export default TypingIndicator;
