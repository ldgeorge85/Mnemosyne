/**
 * Media Attachment Component
 * 
 * A component for displaying various types of media attachments
 * including images, videos, audio, PDFs, and other file types.
 */
import React, { useState } from 'react';
import {
  Box,
  Image,
  AspectRatio,
  Link,
  Flex,
  Text,
  Icon,
  useColorModeValue,
  Button,
} from '@chakra-ui/react';
import {
  FiFile,
  FiFileText,
  FiDownload,
  FiImage,
  FiVideo,
  FiMusic,
  FiExternalLink,
} from 'react-icons/fi';

interface MediaAttachmentProps {
  /**
   * URL of the media file
   */
  url: string;
  
  /**
   * Type of media (auto-detected if not provided)
   */
  type?: 'image' | 'video' | 'audio' | 'pdf' | 'other';
  
  /**
   * Name of the file to display
   */
  fileName?: string;
  
  /**
   * Size of the file in bytes
   */
  fileSize?: number;
  
  /**
   * Maximum width for the media container
   */
  maxWidth?: string;
  
  /**
   * Maximum height for the media container
   */
  maxHeight?: string;
  
  /**
   * Alt text for images
   */
  alt?: string;
  
  /**
   * Whether to open link in new tab
   */
  isExternal?: boolean;
}

/**
 * Component for displaying media attachments in messages
 */
const MediaAttachment: React.FC<MediaAttachmentProps> = ({
  url,
  type,
  fileName,
  fileSize,
  maxWidth = '300px',
  maxHeight = '300px',
  alt = 'Attachment',
  isExternal = true,
}) => {
  // State for tracking errors loading media
  const [hasError, setHasError] = useState(false);
  
  // Auto-detect media type from URL if not provided
  const detectType = (): 'image' | 'video' | 'audio' | 'pdf' | 'other' => {
    if (type) return type;
    
    const extension = url.split('.').pop()?.toLowerCase() || '';
    
    if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'].includes(extension)) {
      return 'image';
    } else if (['mp4', 'webm', 'ogg', 'mov'].includes(extension)) {
      return 'video';
    } else if (['mp3', 'wav', 'ogg'].includes(extension)) {
      return 'audio';
    } else if (extension === 'pdf') {
      return 'pdf';
    } else {
      return 'other';
    }
  };
  
  // Get file name from URL if not provided
  const getFileName = (): string => {
    if (fileName) return fileName;
    return url.split('/').pop() || 'attachment';
  };
  
  // Format file size
  const formatFileSize = (bytes?: number): string => {
    if (!bytes) return '';
    
    if (bytes < 1024) {
      return `${bytes} B`;
    } else if (bytes < 1024 * 1024) {
      return `${(bytes / 1024).toFixed(1)} KB`;
    } else {
      return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    }
  };
  
  // Get icon based on file type
  const getFileIcon = () => {
    const mediaType = detectType();
    
    switch (mediaType) {
      case 'image':
        return FiImage;
      case 'video':
        return FiVideo;
      case 'audio':
        return FiMusic;
      case 'pdf':
        return FiFileText;
      default:
        return FiFile;
    }
  };
  
  // Background and border colors
  const bgColor = useColorModeValue('gray.100', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  
  // Render different components based on media type
  const renderMedia = () => {
    const mediaType = detectType();
    
    if (hasError) {
      // Fallback for failed media
      return (
        <Box
          p={4}
          borderRadius="md"
          border="1px solid"
          borderColor={borderColor}
          bg={bgColor}
        >
          <Flex align="center">
            <Icon as={getFileIcon()} boxSize={6} mr={3} />
            <Box>
              <Text fontWeight="medium">{getFileName()}</Text>
              <Flex fontSize="sm" color="gray.500" align="center" mt={1}>
                <Text>Failed to load media</Text>
                {fileSize && <Text ml={2}>({formatFileSize(fileSize)})</Text>}
              </Flex>
              <Button
                leftIcon={<FiExternalLink />}
                size="sm"
                variant="ghost"
                mt={2}
                as={Link}
                href={url}
                isExternal={isExternal}
              >
                Open in new tab
              </Button>
            </Box>
          </Flex>
        </Box>
      );
    }
    
    switch (mediaType) {
      case 'image':
        return (
          <Box
            borderRadius="md"
            overflow="hidden"
            maxW={maxWidth}
            border="1px solid"
            borderColor={borderColor}
          >
            <Image
              src={url}
              alt={alt}
              objectFit="contain"
              maxH={maxHeight}
              onError={() => setHasError(true)}
              loading="lazy"
            />
            {fileName && (
              <Flex
                justify="space-between"
                align="center"
                p={2}
                bg={bgColor}
                borderTop="1px solid"
                borderColor={borderColor}
              >
                <Text fontSize="sm" fontWeight="medium" noOfLines={1}>
                  {getFileName()}
                </Text>
                <Link href={url} download isExternal={isExternal}>
                  <Icon as={FiDownload} />
                </Link>
              </Flex>
            )}
          </Box>
        );
        
      case 'video':
        return (
          <Box
            borderRadius="md"
            overflow="hidden"
            maxW={maxWidth}
            border="1px solid"
            borderColor={borderColor}
          >
            <AspectRatio ratio={16 / 9} maxW={maxWidth}>
              <video
                controls
                preload="metadata"
                onError={() => setHasError(true)}
              >
                <source src={url} />
                Your browser does not support the video tag.
              </video>
            </AspectRatio>
            {fileName && (
              <Flex
                justify="space-between"
                align="center"
                p={2}
                bg={bgColor}
                borderTop="1px solid"
                borderColor={borderColor}
              >
                <Text fontSize="sm" fontWeight="medium" noOfLines={1}>
                  {getFileName()}
                </Text>
                <Link href={url} download isExternal={isExternal}>
                  <Icon as={FiDownload} />
                </Link>
              </Flex>
            )}
          </Box>
        );
        
      case 'audio':
        return (
          <Box
            p={3}
            borderRadius="md"
            border="1px solid"
            borderColor={borderColor}
            bg={bgColor}
            maxW={maxWidth}
          >
            <Flex mb={2} align="center">
              <Icon as={FiMusic} mr={2} />
              <Text fontWeight="medium" fontSize="sm" noOfLines={1}>
                {getFileName()}
              </Text>
            </Flex>
            <Box width="100%">
              <audio
                controls
                style={{ width: '100%' }}
                preload="metadata"
                onError={() => setHasError(true)}
              >
                <source src={url} />
                Your browser does not support the audio tag.
              </audio>
            </Box>
            {fileSize && (
              <Text fontSize="xs" mt={1} color="gray.500">
                {formatFileSize(fileSize)}
              </Text>
            )}
          </Box>
        );
        
      case 'pdf':
        return (
          <Box
            p={4}
            borderRadius="md"
            border="1px solid"
            borderColor={borderColor}
            bg={bgColor}
            maxW={maxWidth}
          >
            <Flex align="center">
              <Icon as={FiFileText} boxSize={6} mr={3} />
              <Box>
                <Text fontWeight="medium">{getFileName()}</Text>
                {fileSize && (
                  <Text fontSize="sm" color="gray.500" mt={1}>
                    {formatFileSize(fileSize)}
                  </Text>
                )}
              </Box>
            </Flex>
            <Flex mt={3} justify="space-between">
              <Button
                leftIcon={<FiExternalLink />}
                size="sm"
                variant="outline"
                as={Link}
                href={url}
                isExternal={isExternal}
              >
                View
              </Button>
              <Button
                leftIcon={<FiDownload />}
                size="sm"
                colorScheme="blue"
                as={Link}
                href={url}
                download
              >
                Download
              </Button>
            </Flex>
          </Box>
        );
        
      default:
        // Generic file attachment
        return (
          <Box
            p={4}
            borderRadius="md"
            border="1px solid"
            borderColor={borderColor}
            bg={bgColor}
            maxW={maxWidth}
          >
            <Flex align="center">
              <Icon as={FiFile} boxSize={6} mr={3} />
              <Box>
                <Text fontWeight="medium">{getFileName()}</Text>
                {fileSize && (
                  <Text fontSize="sm" color="gray.500" mt={1}>
                    {formatFileSize(fileSize)}
                  </Text>
                )}
              </Box>
            </Flex>
            <Button
              leftIcon={<FiDownload />}
              size="sm"
              colorScheme="blue"
              mt={3}
              as={Link}
              href={url}
              download
            >
              Download
            </Button>
          </Box>
        );
    }
  };
  
  return renderMedia();
};

export default MediaAttachment;
