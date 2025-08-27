/**
 * Receipts Viewer Page (Simplified)
 * 
 * Displays transparency receipts for all system operations.
 * Simplified version using only available components.
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { 
  Shield,
  Download,
  Search,
  Clock,
  AlertCircle,
  CheckCircle,
  Info,
  Eye
} from 'lucide-react';
import { useAuth } from '@/contexts/AuthContextSimple';
import { client as api } from '@/api';

interface Receipt {
  id: string;
  user_id: string;
  receipt_type: string;
  timestamp: string;
  action: string;
  entity_type?: string;
  entity_id?: string;
  context?: Record<string, any>;
  persona_mode?: string;
  worldview_profile?: Record<string, any>;
  decisions_made?: string[];
  confidence_score?: number;
  explanation?: string;
  privacy_impact?: string;
  user_visible: boolean;
}

interface ReceiptStats {
  total_receipts: number;
  by_type: Record<string, number>;
  by_entity: Record<string, number>;
  by_privacy_impact: Record<string, number>;
  by_persona_mode: Record<string, number>;
}

const receiptTypeColors: Record<string, string> = {
  'auth_login': 'bg-green-100 text-green-800',
  'auth_logout': 'bg-gray-100 text-gray-800',
  'memory_created': 'bg-blue-100 text-blue-800',
  'memory_updated': 'bg-yellow-100 text-yellow-800',
  'memory_deleted': 'bg-red-100 text-red-800',
  'task_created': 'bg-purple-100 text-purple-800',
  'task_completed': 'bg-green-100 text-green-800',
  'chat_message': 'bg-indigo-100 text-indigo-800',
  'trust_event': 'bg-orange-100 text-orange-800',
  'pattern_observation': 'bg-cyan-100 text-cyan-800',
};

const privacyImpactIcons = {
  'none': <CheckCircle className="w-4 h-4 text-green-600" />,
  'minimal': <Info className="w-4 h-4 text-blue-600" />,
  'moderate': <AlertCircle className="w-4 h-4 text-yellow-600" />,
  'significant': <AlertCircle className="w-4 h-4 text-orange-600" />,
  'critical': <AlertCircle className="w-4 h-4 text-red-600" />,
};

export default function ReceiptsSimple() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [receipts, setReceipts] = useState<Receipt[]>([]);
  const [stats, setStats] = useState<ReceiptStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedReceipt, setSelectedReceipt] = useState<Receipt | null>(null);
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const LIMIT = 20;

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
    } else {
      fetchReceipts();
      fetchStats();
    }
  }, [isAuthenticated, navigate]);

  const fetchReceipts = async (loadMore = false) => {
    try {
      if (loadMore) {
        setLoadingMore(true);
      } else {
        setLoading(true);
        setSearchTerm('');
      }
      const response = await api.get(`/receipts/?limit=${LIMIT}&offset=${loadMore ? offset : 0}`);
      if (loadMore) {
        setReceipts(prev => [...prev, ...response.data]);
        setOffset(prev => prev + LIMIT);
      } else {
        setReceipts(response.data);
        setOffset(LIMIT);
      }
      setHasMore(response.data.length === LIMIT);
    } catch (error) {
      console.error('Failed to fetch receipts:', error);
      if (!loadMore) {
        setReceipts([]);
      }
      setHasMore(false);
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await api.get('/receipts/stats');
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const filteredReceipts = receipts.filter(receipt => {
    if (searchTerm && !receipt.action.toLowerCase().includes(searchTerm.toLowerCase())) {
      return false;
    }
    return true;
  });

  const exportReceipts = () => {
    const dataStr = JSON.stringify(filteredReceipts, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `receipts_${new Date().toISOString()}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  const formatDate = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'just now';
    if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="h-full overflow-auto bg-background">
      <div className="container mx-auto px-4 py-8">
        <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Shield className="w-8 h-8 text-primary" />
          <div>
            <h1 className="text-3xl font-bold">Transparency Receipts</h1>
            <p className="text-muted-foreground mt-1">
              Complete record of all system operations and decisions
            </p>
          </div>
        </div>
        <Button onClick={exportReceipts} variant="outline">
          <Download className="w-4 h-4 mr-2" />
          Export
        </Button>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Total Receipts</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.total_receipts}</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Most Common</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {Object.entries(stats.by_type)
                    .sort(([, a], [, b]) => b - a)[0]?.[0]
                    ?.replace(/_/g, ' ') || 'None'}
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Privacy Impact</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2">
                  {stats.by_privacy_impact?.none > (stats.total_receipts * 0.8) ? (
                    <CheckCircle className="w-5 h-5 text-green-600" />
                  ) : (
                    <AlertCircle className="w-5 h-5 text-yellow-600" />
                  )}
                  <span className="text-2xl font-bold">
                    {stats.by_privacy_impact?.none > (stats.total_receipts * 0.8) ? 'Low' : 'Moderate'}
                  </span>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Active Persona</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {Object.entries(stats.by_persona_mode || {})
                    .sort(([, a], [, b]) => b - a)[0]?.[0] || 'Confidant'}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

      {/* Search */}
      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search receipts..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && setSearchTerm(e.currentTarget.value)}
            className="pl-10"
          />
        </div>
        <Button 
          variant="secondary"
          onClick={() => setSearchTerm(searchTerm)}
          disabled={false}
        >
          Search
        </Button>
      </div>

      {/* Receipts List */}
      <div className="space-y-4">
        <div>
          <h3 className="text-xl font-semibold">Recent Activity</h3>
          <p className="text-sm text-muted-foreground">
            {filteredReceipts.length} operations recorded
          </p>
        </div>
        
        {loading ? (
          <Card>
            <CardContent className="py-8 text-center">
              <p className="text-muted-foreground">Loading receipts...</p>
            </CardContent>
          </Card>
        ) : filteredReceipts.length === 0 ? (
          <Card>
            <CardContent className="py-8 text-center">
              <p className="text-muted-foreground">No receipts found</p>
            </CardContent>
          </Card>
        ) : (
          <>
            <div className="space-y-3">
              {filteredReceipts.map((receipt) => (
                <Card key={receipt.id} className="hover:shadow-md transition-shadow">
                <CardContent className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <Badge 
                          className={receiptTypeColors[receipt.receipt_type] || 'bg-gray-100 text-gray-800'}
                        >
                          {receipt.receipt_type.replace(/_/g, ' ')}
                        </Badge>
                        {receipt.persona_mode && (
                          <Badge variant="outline">
                            {receipt.persona_mode}
                          </Badge>
                        )}
                        {receipt.privacy_impact && (
                          <div className="flex items-center gap-1">
                            {privacyImpactIcons[receipt.privacy_impact] || privacyImpactIcons.minimal}
                          </div>
                        )}
                      </div>
                      
                      <p className="font-medium mb-1">{receipt.action}</p>
                      
                      {receipt.explanation && (
                        <p className="text-sm text-muted-foreground mb-2">
                          {receipt.explanation}
                        </p>
                      )}
                      
                      <div className="flex items-center gap-4 text-sm text-muted-foreground">
                        <div className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {formatDate(receipt.timestamp)}
                        </div>
                        {receipt.entity_type && (
                          <span>
                            {receipt.entity_type}
                          </span>
                        )}
                        {receipt.confidence_score && (
                          <span>
                            Confidence: {Math.round(receipt.confidence_score * 100)}%
                          </span>
                        )}
                      </div>
                      
                      {/* Inline details for selected receipt */}
                      {selectedReceipt?.id === receipt.id && (
                        <div className="mt-4 pt-4 border-t space-y-3">
                          <div>
                            <p className="text-sm font-medium text-muted-foreground">Receipt ID</p>
                            <p className="font-mono text-xs">{receipt.id}</p>
                          </div>
                          
                          {receipt.decisions_made && receipt.decisions_made.length > 0 && (
                            <div>
                              <p className="text-sm font-medium text-muted-foreground mb-1">Decisions Made</p>
                              <ul className="list-disc list-inside text-sm space-y-1">
                                {receipt.decisions_made.map((decision, idx) => (
                                  <li key={idx}>{decision}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                          
                          {receipt.context && Object.keys(receipt.context).length > 0 && (
                            <div>
                              <p className="text-sm font-medium text-muted-foreground mb-1">Context</p>
                              <pre className="bg-gray-50 p-2 rounded text-xs overflow-auto max-h-32">
                                {JSON.stringify(receipt.context, null, 2)}
                              </pre>
                            </div>
                          )}
                          
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => {
                              const dataStr = JSON.stringify(receipt, null, 2);
                              const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
                              const exportFileDefaultName = `receipt_${receipt.id}.json`;
                              
                              const linkElement = document.createElement('a');
                              linkElement.setAttribute('href', dataUri);
                              linkElement.setAttribute('download', exportFileDefaultName);
                              linkElement.click();
                            }}
                          >
                            <Download className="w-3 h-3 mr-1" />
                            Export Receipt
                          </Button>
                        </div>
                      )}
                    </div>
                    
                    <Button 
                      variant="ghost" 
                      size="sm"
                      onClick={() => setSelectedReceipt(
                        selectedReceipt?.id === receipt.id ? null : receipt
                      )}
                    >
                      <Eye className="w-4 h-4 mr-1" />
                      {selectedReceipt?.id === receipt.id ? 'Hide' : 'View'}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
            </div>
            {hasMore && !searchTerm && (
              <div className="flex justify-center mt-4">
                <Button 
                  variant="outline" 
                  onClick={() => fetchReceipts(true)}
                  disabled={loadingMore}
                >
                  {loadingMore ? 'Loading...' : 'Load More'}
                </Button>
              </div>
            )}
          </>
        )}
      </div>
        </div>
      </div>
    </div>
  );
}