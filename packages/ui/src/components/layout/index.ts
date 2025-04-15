/**
 * Layout Components
 */
import React from 'react';
import { Box, Container, AppBar, Toolbar, Typography, Drawer, List, ListItem, ListItemIcon, ListItemText, Divider } from '@mui/material';

export interface PageProps {
  title: string;
  children: React.ReactNode;
}

/**
 * Page component
 */
export const Page: React.FC<PageProps> = ({ title, children }) => {
  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        {title}
      </Typography>
      {children}
    </Container>
  );
};

export interface SidebarItemProps {
  icon?: React.ReactNode;
  text: string;
  onClick?: () => void;
}

/**
 * Sidebar item component
 */
export const SidebarItem: React.FC<SidebarItemProps> = ({ icon, text, onClick }) => {
  return (
    <ListItem button onClick={onClick}>
      {icon && <ListItemIcon>{icon}</ListItemIcon>}
      <ListItemText primary={text} />
    </ListItem>
  );
};

export interface SidebarProps {
  items: SidebarItemProps[];
  width?: number;
}

/**
 * Sidebar component
 */
export const Sidebar: React.FC<SidebarProps> = ({ items, width = 240 }) => {
  return (
    <Drawer
      variant="permanent"
      sx={{
        width,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width,
          boxSizing: 'border-box',
        },
      }}
    >
      <Toolbar />
      <Box sx={{ overflow: 'auto' }}>
        <List>
          {items.map((item, index) => (
            <SidebarItem key={index} {...item} />
          ))}
        </List>
      </Box>
    </Drawer>
  );
};

export interface HeaderProps {
  title: string;
  onMenuClick?: () => void;
}

/**
 * Header component
 */
export const Header: React.FC<HeaderProps> = ({ title, onMenuClick }) => {
  return (
    <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
      <Toolbar>
        <Typography variant="h6" noWrap component="div">
          {title}
        </Typography>
      </Toolbar>
    </AppBar>
  );
};
