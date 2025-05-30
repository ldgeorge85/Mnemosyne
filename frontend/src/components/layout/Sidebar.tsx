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
} from '@chakra-ui/react';
import {
  FiHome,
  FiTrendingUp,
  FiCompass,
  FiStar,
  FiSettings,
  FiMessageSquare,
  FiCalendar,
  FiBrain,
  FiList,
  FiUsers,
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
}

interface LinkItemProps {
  name: string;
  icon: IconType;
  to: string;
}

// Navigation items with icons and routes
const LinkItems: Array<LinkItemProps> = [
  { name: 'Home', icon: FiHome, to: '/' },
  { name: 'Dashboard', icon: FiTrendingUp, to: '/dashboard' },
  { name: 'Conversations', icon: FiMessageSquare, to: '/conversations' },
  { name: 'Memories', icon: FiBrain, to: '/memories' },
  { name: 'Tasks', icon: FiList, to: '/tasks' },
  { name: 'Calendar', icon: FiCalendar, to: '/calendar' },
  { name: 'Contacts', icon: FiUsers, to: '/contacts' },
  { name: 'Settings', icon: FiSettings, to: '/settings' },
];

/**
 * Main sidebar component
 */
const Sidebar = ({ isOpen, onClose }: SidebarProps) => {
  return (
    <Box>
      {/* Desktop sidebar */}
      <SidebarContent
        display={{ base: 'none', md: 'block' }}
        onClose={() => onClose}
      />
      
      {/* Mobile sidebar */}
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
    </Box>
  );
};

/**
 * Sidebar content component used in both desktop and mobile versions
 */
const SidebarContent = ({ onClose, ...rest }: BoxProps & { onClose: () => void }) => {
  const location = useLocation();
  
  return (
    <Box
      bg={useColorModeValue('white', 'gray.900')}
      borderRight="1px"
      borderRightColor={useColorModeValue('gray.200', 'gray.700')}
      w={{ base: 'full', md: 60 }}
      pos="fixed"
      h="full"
      {...rest}>
      <Flex h="20" alignItems="center" mx="8" justifyContent="space-between">
        <Text fontSize="2xl" fontFamily="monospace" fontWeight="bold" color="brand.500">
          Mnemosyne
        </Text>
        <CloseButton display={{ base: 'flex', md: 'none' }} onClick={onClose} />
      </Flex>
      
      {/* Navigation Links */}
      {LinkItems.map((link) => (
        <NavItem 
          key={link.name} 
          icon={link.icon} 
          to={link.to}
          isActive={location.pathname === link.to}
        >
          {link.name}
        </NavItem>
      ))}
    </Box>
  );
};

/**
 * Individual navigation item in the sidebar
 */
const NavItem = ({ icon, children, to, isActive, ...rest }: NavItemProps) => {
  const activeColor = useColorModeValue('brand.500', 'brand.200');
  const activeBg = useColorModeValue('brand.50', 'gray.700');
  const hoverBg = useColorModeValue('gray.100', 'gray.700');
  
  return (
    <Box
      as={RouterLink}
      to={to}
      style={{ textDecoration: 'none' }}
      _focus={{ boxShadow: 'none' }}
    >
      <Flex
        align="center"
        p="4"
        mx="4"
        borderRadius="lg"
        role="group"
        cursor="pointer"
        bg={isActive ? activeBg : 'transparent'}
        color={isActive ? activeColor : 'inherit'}
        _hover={{
          bg: hoverBg,
        }}
        {...rest}>
        {icon && (
          <Icon
            mr="4"
            fontSize="16"
            as={icon}
            color={isActive ? activeColor : 'inherit'}
            _groupHover={{
              color: activeColor,
            }}
          />
        )}
        {children}
      </Flex>
    </Box>
  );
};

export default Sidebar;
