/**
 * Footer Component
 * 
 * This component provides the application footer with copyright information,
 * links, and other footer content.
 */
import React from 'react';
import {
  Box,
  Container,
  Stack,
  Text,
  Link,
  useColorModeValue,
  Flex,
} from '@chakra-ui/react';
import { Link as RouterLink } from 'react-router-dom';

/**
 * Application footer component
 */
const Footer: React.FC = () => {
  return (
    <Box
      as="footer"
      bg={useColorModeValue('gray.50', 'gray.900')}
      color={useColorModeValue('gray.700', 'gray.200')}
      mt={10}
      py={4}
    >
      <Container
        as={Stack}
        maxW={'container.xl'}
        py={4}
        direction={{ base: 'column', md: 'row' }}
        spacing={4}
        justify={{ base: 'center', md: 'space-between' }}
        align={{ base: 'center', md: 'center' }}
      >
        <Text>© {new Date().getFullYear()} Mnemosyne. All rights reserved</Text>
        <Stack direction={'row'} spacing={6}>
          <Link as={RouterLink} to={'/'}>Home</Link>
          <Link as={RouterLink} to={'/about'}>About</Link>
          <Link as={RouterLink} to={'/privacy'}>Privacy</Link>
          <Link as={RouterLink} to={'/terms'}>Terms</Link>
          <Link as={RouterLink} to={'/contact'}>Contact</Link>
        </Stack>
      </Container>
    </Box>
  );
};

export default Footer;
