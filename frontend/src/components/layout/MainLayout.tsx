/**
 * Main Layout Component
 * 
 * This component provides the main application layout including
 * header, navigation, footer, and content area.
 */
import React from 'react';
import { Outlet } from 'react-router-dom';
import {
  Box,
  Flex,
  Container,
  useColorModeValue,
  useDisclosure
} from '@chakra-ui/react';

// Import layout components
import Header from './Header';
import Sidebar from './Sidebar';
import Footer from './Footer';

/**
 * Main layout component that wraps all pages
 * Provides consistent layout structure with header, sidebar, and footer
 */
const MainLayout: React.FC = () => {
  // Control sidebar visibility on mobile
  const { isOpen, onOpen, onClose } = useDisclosure();
  
  // Background colors for light/dark mode
  const bgColor = useColorModeValue('gray.50', 'gray.900');
  const contentBgColor = useColorModeValue('white', 'gray.800');
  
  return (
    <Box minH="100vh" bg={bgColor}>
      {/* Header component with hamburger menu for mobile */}
      <Header onOpenSidebar={onOpen} />
      
      <Flex>
        {/* Sidebar navigation */}
        <Sidebar isOpen={isOpen} onClose={onClose} />
        
        {/* Main content area */}
        <Box
          flex="1"
          p={4}
          ml={{ base: 0, md: 60 }}
          transition="margin-left 0.3s"
        >
          <Container maxW="container.xl" py={6}>
            <Box
              bg={contentBgColor}
              borderRadius="lg"
              p={6}
              boxShadow="sm"
              minH="calc(100vh - 180px)"
            >
              {/* Page content renders here */}
              <Outlet />
            </Box>
          </Container>
          
          {/* Footer */}
          <Footer />
        </Box>
      </Flex>
    </Box>
  );
};

export default MainLayout;
