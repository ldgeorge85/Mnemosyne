/**
 * Sidebar Component
 * 
 * This component provides the application sidebar navigation
 * with links to main sections and user account options.
 */
import React from 'react';
import { Link as RouterLink, useLocation } from 'react-router-dom';
import {
  Box,
  CloseButton,
  Flex,
  Icon,
  useColorModeValue,
  Text,
  Drawer,
  DrawerContent,
  BoxProps,
  FlexProps,
  Tooltip,
  IconButton,
  HStack,
} from '@chakra-ui/react';
import {
  FiHome,
  FiTrendingUp,
  FiSettings,
  FiMessageSquare,
  FiCalendar,
  FiDatabase,
  FiList,
  FiUsers,
  FiBookmark,
  FiHelpCircle,
  FiActivity,
  FiBriefcase,
} from 'react-icons/fi';
import { IconType } from 'react-icons';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

interface NavItemProps extends FlexProps {
  icon: IconType;
  children: React.ReactNode;
  to: string;
  isActive?: boolean;
  badge?: string | number;
  key?: string;
}

interface LinkItemProps {
  name: string;
  icon: IconType;
  to: string;
  category?: string;
  badge?: string | number;
}

// Navigation items with icons, routes, and categories
const LinkItems: Array<LinkItemProps> = [
  // Main Navigation
  { name: 'Home', icon: FiHome, to: '/', category: 'Main' },
  { name: 'Dashboard', icon: FiTrendingUp, to: '/dashboard', category: 'Main' },
  { name: 'Chat', icon: FiMessageSquare, to: '/chat', category: 'Main' },
  
  // Knowledge Management
  { name: 'Conversations', icon: FiMessageSquare, to: '/conversations', category: 'Knowledge' },
  { name: 'Memories', icon: FiDatabase, to: '/memories', category: 'Knowledge' },
  { name: 'Bookmarks', icon: FiBookmark, to: '/bookmarks', category: 'Knowledge' },
  
  // Productivity
  { name: 'Tasks', icon: FiList, to: '/tasks', category: 'Productivity', badge: 3 },
  { name: 'Calendar', icon: FiCalendar, to: '/calendar', category: 'Productivity' },
  { name: 'Projects', icon: FiBriefcase, to: '/projects', category: 'Productivity' },
  
  // Network
  { name: 'Contacts', icon: FiUsers, to: '/contacts', category: 'Network' },
  { name: 'Activity', icon: FiActivity, to: '/activity', category: 'Network' },
  
  // System
  { name: 'Settings', icon: FiSettings, to: '/settings', category: 'System' },
  { name: 'Help', icon: FiHelpCircle, to: '/help', category: 'System' },
];

// Mobile navigation items (simplified for bottom navigation)
const MobileNavItems = [
  { name: 'Home', icon: FiHome, to: '/' },
  { name: 'Chat', icon: FiMessageSquare, to: '/chat' },
  { name: 'Tasks', icon: FiList, to: '/tasks', badge: 3 },
  { name: 'Memories', icon: FiDatabase, to: '/memories' },
  { name: 'Settings', icon: FiSettings, to: '/settings' },
];

/**
 * Main sidebar component
 */
const Sidebar = ({ isOpen, onClose }: SidebarProps) => {
  return (
    <>
      {/* Desktop sidebar */}
      <SidebarContent
        display={{ base: 'none', md: 'block' }}
        onClose={() => onClose}
      />
      
      {/* Mobile sidebar drawer (full screen) */}
      <Drawer
        isOpen={isOpen}
        placement="left"
        onClose={onClose}
        returnFocusOnClose={false}
        onOverlayClick={onClose}
        size="full">
        <DrawerContent>
          <SidebarContent onClose={onClose} />
        </DrawerContent>
      </Drawer>
      
      {/* Mobile bottom navigation bar */}
      <MobileNavigation display={{ base: 'flex', md: 'none' }} />
    </>
  );
};

/**
 * Sidebar content component used in both desktop and mobile versions
 */
const SidebarContent = ({ onClose, ...rest }: BoxProps & { onClose: () => void }) => {
  const location = useLocation();
  
  // Group navigation items by category
  const groupedLinks = LinkItems.reduce((acc, link) => {
    const category = link.category || 'Other';
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(link);
    return acc;
  }, {} as Record<string, LinkItemProps[]>);
  
  // Order of categories
  const categoryOrder = ['Main', 'Knowledge', 'Productivity', 'Network', 'System', 'Other'];
  
  /**
   * Check if route is active, including nested routes
   */
  const isRouteActive = (path: string): boolean => {
    // Exact match for home route
    if (path === '/' && location.pathname === '/') {
      return true;
    }
    // For other routes, check if the location pathname starts with the path
    // But only if the path is not just '/'  
    return path !== '/' && location.pathname.startsWith(path);
  };
  
  return (
    <Box
      bg={useColorModeValue('white', 'gray.900')}
      borderRight="1px"
      borderRightColor={useColorModeValue('gray.200', 'gray.700')}
      w={{ base: 'full', md: 60 }}
      pos="fixed"
      h="full"
      overflow="auto"
      css={{
        '&::-webkit-scrollbar': {
          width: '4px',
        },
        '&::-webkit-scrollbar-track': {
          width: '6px',
        },
        '&::-webkit-scrollbar-thumb': {
          background: useColorModeValue('rgba(0,0,0,0.1)', 'rgba(255,255,255,0.1)'),
          borderRadius: '24px',
        },
      }}
      {...rest}>
      <Flex h="20" alignItems="center" mx="8" justifyContent="space-between">
        <Text fontSize="2xl" fontFamily="monospace" fontWeight="bold" color="brand.500">
          Mnemosyne
        </Text>
        <CloseButton display={{ base: 'flex', md: 'none' }} onClick={onClose} />
      </Flex>
      
      {/* Navigation Links grouped by category */}
      <Box px={3}>
        {categoryOrder.map(category => {
          const links = groupedLinks[category] || [];
          if (links.length === 0) return null;
          
          return (
            <Box key={category} mb={4}>
              {/* Category header */}
              <Text
                px={3}
                fontSize="xs"
                fontWeight="bold"
                textTransform="uppercase"
                letterSpacing="wider"
                color={useColorModeValue('gray.500', 'gray.400')}
                mb={2}
              >
                {category}
              </Text>
              
              {/* Category links */}
              {links.map((link) => (
                <NavItem 
                  key={link.name} 
                  icon={link.icon} 
                  to={link.to}
                  isActive={isRouteActive(link.to)}
                  badge={link.badge}
                >
                  {link.name}
                </NavItem>
              ))}
            </Box>
          );
        })}
      </Box>
    </Box>
  );
};

/**
 * Individual navigation item in the sidebar
 */
const NavItem = ({ icon, children, to, isActive, badge, ...rest }: NavItemProps) => {
  const activeColor = useColorModeValue('brand.500', 'brand.200');
  const activeBg = useColorModeValue('brand.50', 'gray.700');
  const hoverBg = useColorModeValue('gray.100', 'gray.700');
  const badgeBg = useColorModeValue('brand.500', 'brand.200');
  
  return (
    <Box
      as={RouterLink}
      to={to}
      style={{ textDecoration: 'none' }}
      _focus={{ boxShadow: 'none' }}
      mb={1}
    >
      <Flex
        align="center"
        p="3"
        mx="1"
        borderRadius="lg"
        role="group"
        cursor="pointer"
        bg={isActive ? activeBg : 'transparent'}
        color={isActive ? activeColor : 'inherit'}
        _hover={{
          bg: hoverBg,
        }}
        position="relative"
        transition="all 0.2s"
        {...rest}>
        {icon && (
          <Icon
            mr="3"
            fontSize="16"
            as={icon}
            color={isActive ? activeColor : 'inherit'}
            _groupHover={{
              color: activeColor,
            }}
          />
        )}
        <Text fontWeight={isActive ? 'medium' : 'normal'}>{children}</Text>
        
        {/* Badge for notifications or counts */}
        {badge && (
          <Box
            px={2}
            py={1}
            ml="auto"
            borderRadius="full"
            bg={badgeBg}
            color="white"
            fontSize="xs"
            fontWeight="bold"
            lineHeight="none"
            minW="1rem"
            textAlign="center"
          >
            {badge}
          </Box>
        )}
      </Flex>
    </Box>
  );
};

/**
 * Mobile bottom navigation component
 */
const MobileNavigation = (props: BoxProps) => {
  const location = useLocation();
  const activeColor = useColorModeValue('brand.500', 'brand.200');
  const bg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  
  return (
    <Box
      position="fixed"
      bottom={0}
      left={0}
      right={0}
      height="60px"
      bg={bg}
      borderTopWidth="1px"
      borderColor={borderColor}
      zIndex={3}
      {...props}
    >
      <HStack justify="space-around" align="center" h="100%">
        {MobileNavItems.map((item) => {
          const isActive = location.pathname === item.to ||
            (item.to !== '/' && location.pathname.startsWith(item.to));
          
          return (
            <Tooltip key={item.name} label={item.name} placement="top" hasArrow>
              <Box as={RouterLink} to={item.to} position="relative">
                <IconButton
                  aria-label={item.name}
                  variant="ghost"
                  icon={<Icon as={item.icon} />}
                  fontSize="xl"
                  color={isActive ? activeColor : 'inherit'}
                  _hover={{
                    color: activeColor,
                  }}
                />
                {item.badge && (
                  <Box
                    position="absolute"
                    top="-2px"
                    right="-2px"
                    px={1.5}
                    py={0.5}
                    fontSize="xs"
                    fontWeight="bold"
                    lineHeight="none"
                    color="white"
                    bg={activeColor}
                    borderRadius="full"
                    minW="1rem"
                    textAlign="center"
                  >
                    {item.badge}
                  </Box>
                )}
              </Box>
            </Tooltip>
          );
        })}
      </HStack>
    </Box>
  );
};

export default Sidebar;
