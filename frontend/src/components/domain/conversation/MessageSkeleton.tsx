/**
 * Message Skeleton Component
 * 
 * This component displays a skeleton placeholder for messages that are loading.
 */
import React from 'react';
import {
  Box,
  Flex,
  Skeleton,
  SkeletonCircle,
  VStack,
  useColorModeValue
} from '@chakra-ui/react';

interface MessageSkeletonProps {
  /**
   * Number of skeleton items to display
   */
  count?: number;
}

/**
 * Displays a loading placeholder for messages
 */
const MessageSkeleton: React.FC<MessageSkeletonProps> = ({ count = 3 }) => {
  const bgColor = useColorModeValue('gray.100', 'gray.700');
  
  return (
    <VStack spacing={4} width="100%" align="stretch">
      {Array.from({ length: count }).map((_, index) => (
        <Flex 
          key={index} 
          direction={index % 2 === 0 ? 'row' : 'row-reverse'} 
          align="start"
        >
          <SkeletonCircle size="8" mr={index % 2 === 0 ? 2 : 0} ml={index % 2 === 0 ? 0 : 2} />
          <Box
            maxWidth="70%"
            borderRadius="lg"
            p={4}
            bg={bgColor}
          >
            <Skeleton height="20px" width="100%" mb={2} />
            <Skeleton height="20px" width="80%" mb={2} />
            <Skeleton height="20px" width={`${40 + Math.random() * 40}%`} />
            <Skeleton height="12px" width="80px" mt={2} />
          </Box>
        </Flex>
      ))}
    </VStack>
  );
};

export default MessageSkeleton;
