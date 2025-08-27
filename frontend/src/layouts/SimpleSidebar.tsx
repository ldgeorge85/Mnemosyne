import React, { useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { useAuth } from '../contexts/AuthContextSimple';
import { useNavigate } from 'react-router-dom';
import { cn } from '@/lib/utils';
import {
  Home,
  MessageSquare,
  CheckSquare,
  Brain,
  Shield,
  Settings,
  LogOut,
  ChevronLeft,
  ChevronRight,
  X,
  Plus,
  Clock,
} from 'lucide-react';

interface SimpleSidebarProps {
  isOpen: boolean;
  onToggle: () => void;
  onClose: () => void;
}

interface NavItem {
  name: string;
  icon: React.ComponentType<{ className?: string }>;
  path: string;
  badge?: number;
}

const navItems: NavItem[] = [
  { name: 'Chat', icon: MessageSquare, path: '/chat' },
  { name: 'Dashboard', icon: Home, path: '/dashboard' },
  { name: 'Tasks', icon: CheckSquare, path: '/tasks' },
  { name: 'Memories', icon: Brain, path: '/memories' },
  { name: 'Receipts', icon: Shield, path: '/receipts' },
  { name: 'Settings', icon: Settings, path: '/settings' },
];

const SimpleSidebar: React.FC<SimpleSidebarProps> = ({ isOpen, onToggle, onClose }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  
  // Local state for conversations from localStorage
  const [localConversations, setLocalConversations] = React.useState<any[]>([]);
  const [selectedConversationId, setSelectedConversationId] = React.useState<string | null>(null);
  
  // Load conversations from localStorage
  const loadConversations = () => {
    const stored = localStorage.getItem('mnemosyne_conversations');
    if (!stored) return [];
    try {
      const parsed = JSON.parse(stored);
      return parsed.map((conv: any) => ({
        id: conv.id,
        title: conv.title,
        updatedAt: conv.updatedAt,
        persona_mode: conv.persona_mode
      }));
    } catch {
      return [];
    }
  };
  
  // Listen for conversation updates from chat page
  useEffect(() => {
    const handleConversationUpdate = (event: CustomEvent) => {
      const conversations = event.detail;
      setLocalConversations(conversations.map((conv: any) => ({
        id: conv.id,
        title: conv.title,
        updatedAt: conv.updatedAt,
        persona_mode: conv.persona_mode
      })));
    };
    
    window.addEventListener('conversationsUpdated', handleConversationUpdate as EventListener);
    
    // Initial load
    if (location.pathname === '/chat') {
      setLocalConversations(loadConversations());
    }
    
    return () => {
      window.removeEventListener('conversationsUpdated', handleConversationUpdate as EventListener);
    };
  }, [location.pathname]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (path: string) => {
    if (path === '/chat' && location.pathname === '/') return true;
    return location.pathname === path;
  };

  return (
    <div className="h-full bg-card border-r flex flex-col">
      {/* Header */}
      <div className="p-4 border-b flex items-center justify-between">
        {isOpen ? (
          <>
            <h2 className="text-xl font-bold">Mnemosyne</h2>
            <div className="flex gap-1">
              <Button
                variant="ghost"
                size="icon"
                className="hidden md:flex"
                onClick={onToggle}
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="md:hidden"
                onClick={onClose}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          </>
        ) : (
          <Button
            variant="ghost"
            size="icon"
            onClick={onToggle}
            className="mx-auto"
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto p-2">
        {/* Main Navigation */}
        <div className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={cn(
                  'flex items-center gap-3 px-3 py-2 rounded-lg transition-colors',
                  'hover:bg-accent hover:text-accent-foreground',
                  isActive(item.path) && 'bg-accent text-accent-foreground font-medium'
                )}
              >
                <Icon className="h-5 w-5 flex-shrink-0" />
                {isOpen && (
                  <>
                    <span className="flex-1">{item.name}</span>
                    {item.badge && (
                      <span className="bg-primary text-primary-foreground text-xs px-2 py-0.5 rounded-full">
                        {item.badge}
                      </span>
                    )}
                  </>
                )}
              </Link>
            );
          })}
        </div>

        {/* Chat History Section - Only show in Chat view when sidebar is open */}
        {isOpen && location.pathname === '/chat' && (
          <div className="mt-6">
            <div className="px-3 mb-2 flex items-center justify-between">
              <h3 className="text-sm font-semibold text-muted-foreground">Recent Chats</h3>
              <Button 
                variant="ghost" 
                size="icon" 
                className="h-6 w-6"
                onClick={() => {
                  // Dispatch event to create new conversation
                  window.dispatchEvent(new CustomEvent('createNewConversation'));
                }}
              >
                <Plus className="h-3 w-3" />
              </Button>
            </div>
            <div className="space-y-1">
              {localConversations.length > 0 ? (
                localConversations.slice(0, 10).map((conversation) => {
                  const isActive = selectedConversationId === conversation.id;
                  const lastMessageTime = conversation.updatedAt 
                    ? new Date(conversation.updatedAt).toLocaleString('en-US', { 
                        hour: 'numeric',
                        minute: '2-digit',
                        month: 'short',
                        day: 'numeric'
                      })
                    : 'No messages';
                  
                  return (
                    <button
                      key={conversation.id}
                      className={cn(
                        "w-full text-left px-3 py-2 rounded-lg transition-colors",
                        isActive ? "bg-accent" : "hover:bg-accent"
                      )}
                      onClick={() => {
                        setSelectedConversationId(conversation.id);
                        // Dispatch event to load conversation
                        window.dispatchEvent(new CustomEvent('loadConversation', { 
                          detail: conversation.id 
                        }));
                      }}
                    >
                      <div className="text-sm font-medium truncate">
                        {conversation.title || 'Untitled Chat'}
                      </div>
                      <div className="text-xs text-muted-foreground flex items-center gap-1 mt-0.5">
                        <Clock className="h-3 w-3" />
                        {lastMessageTime}
                      </div>
                    </button>
                  );
                })
              ) : (
                <div className="px-3 py-2 text-sm text-muted-foreground">
                  No conversations yet
                </div>
              )}
            </div>
          </div>
        )}
      </nav>

      {/* Footer */}
      <div className="border-t p-2">
        {isOpen ? (
          <div className="space-y-2">
            <div className="px-3 py-2 text-sm">
              <div className="font-medium">{user?.username || 'User'}</div>
              <div className="text-xs text-muted-foreground">{user?.email}</div>
            </div>
            <Button
              variant="ghost"
              className="w-full justify-start"
              onClick={handleLogout}
            >
              <LogOut className="h-4 w-4 mr-3" />
              Logout
            </Button>
          </div>
        ) : (
          <Button
            variant="ghost"
            size="icon"
            onClick={handleLogout}
            className="w-full"
          >
            <LogOut className="h-4 w-4" />
          </Button>
        )}
      </div>
    </div>
  );
};

export default SimpleSidebar;