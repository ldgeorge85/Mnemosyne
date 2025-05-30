/**
 * Message Item Component
 * 
 * This component displays a single message in the conversation,
 * with appropriate styling based on the message role.
 */
import React from 'react';
import {
  Box,
  Flex,
  Text,
  IconButton,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  Avatar,
  Tooltip,
  useColorModeValue,
  HStack,
} from '@chakra-ui/react';
import { MessageFormatter } from '../../common/formatting';
import { FiMoreVertical, FiCopy, FiTrash2 } from 'react-icons/fi';
import { Message } from '../../../types';
import { formatTimestamp } from '../../../utils/dateUtils';

interface MessageItemProps {
  /**
   * Message to display
   */
  message: Message;
  
  /**
   * Called when message is deleted
   */
  onDelete?: () => void;
  
  /**
   * Called when message is copied
   */
  onCopy?: () => void;
}

/**
 * Displays a single message with appropriate styling based on role
 */
const MessageItem: React.FC<MessageItemProps> = ({ message, onDelete, onCopy }) => {
  const isUser = message.role === 'user';
  const isSystem = message.role === 'system';
  
  // Background colors for different message roles
  const userBgColor = useColorModeValue('blue.100', 'blue.800');
  const assistantBgColor = useColorModeValue('gray.100', 'gray.700');
  const systemBgColor = useColorModeValue('purple.100', 'purple.800');
  
  // Text colors for different message roles
  const userTextColor = useColorModeValue('blue.800', 'white');
  const assistantTextColor = useColorModeValue('gray.800', 'white');
  const systemTextColor = useColorModeValue('purple.800', 'white');
  
  // Determine background and text color based on role
  const bgColor = isUser 
    ? userBgColor 
    : isSystem 
      ? systemBgColor 
      : assistantBgColor;
  
  const textColor = isUser 
    ? userTextColor 
    : isSystem 
      ? systemTextColor 
      : assistantTextColor;
  
  // Avatar icons for different roles
  const avatarBg = isUser 
    ? 'blue.500' 
    : isSystem 
      ? 'purple.500' 
      : 'gray.500';
  
  const avatarContent = isUser 
    ? 'U' 
    : isSystem 
      ? 'S' 
      : 'A';
  
  return (
    <Box width="100%" position="relative">
      <Flex
        direction={isUser ? 'row-reverse' : 'row'}
        align="start"
        justify="flex-start"
        width="100%"
      >
        {/* Avatar */}
        <Avatar
          size="sm"
          name={message.role}
          bg={avatarBg}
          color="white"
          fontSize="sm"
          mt={1}
          mx={2}
        >
          {avatarContent}
        </Avatar>
        
        {/* Message content */}
        <Box
          maxWidth="80%"
          borderRadius="lg"
          px={4}
          py={3}
          bg={bgColor}
          color={textColor}
          position="relative"
        >
          <MessageFormatter 
            content={message.content} 
            attachments={message.attachments} 
            enableMarkdown={true} 
          />
          
          {/* Timestamp */}
          <Text
            fontSize="xs"
            color={useColorModeValue('gray.500', 'gray.400')}
            mt={1}
          >
            {formatTimestamp(message.createdAt)}
          </Text>
        </Box>
        
        {/* Actions menu */}
        <Menu placement="left-start">
          <MenuButton
            as={IconButton}
            icon={<FiMoreVertical />}
            variant="ghost"
            size="sm"
            aria-label="Message options"
            opacity={0.6}
            _hover={{ opacity: 1 }}
          />
          <MenuList>
            {onCopy && (
              <MenuItem icon={<FiCopy />} onClick={onCopy}>
                Copy message
              </MenuItem>
            )}
            {onDelete && (
              <MenuItem icon={<FiTrash2 />} onClick={onDelete}>
                Delete message
              </MenuItem>
            )}
          </MenuList>
        </Menu>
      </Flex>
    </Box>
  );
};

export default MessageItem;
