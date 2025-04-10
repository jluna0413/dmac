import * as vscode from 'vscode';
import { DMacConfigManager } from './config';
import { logger } from '../core/logger';

/**
 * Agent message
 */
export interface AgentMessage {
  id: string;
  from: string;
  to: string;
  content: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

/**
 * Agent communication
 */
export class AgentCommunication {
  private configManager: DMacConfigManager;
  private messageQueue: AgentMessage[] = [];
  private messageHandlers: ((message: AgentMessage) => Promise<void>)[] = [];
  
  constructor(configManager: DMacConfigManager) {
    this.configManager = configManager;
    logger.info('Agent communication initialized');
  }
  
  /**
   * Sends a message to another agent
   */
  public async sendMessage(
    to: string,
    content: string,
    metadata: Record<string, any> = {}
  ): Promise<string> {
    try {
      const config = this.configManager.getConfig();
      
      if (!config.enabled || !config.agentCommunicationEnabled) {
        throw new Error('Agent communication is not enabled');
      }
      
      const message: AgentMessage = {
        id: `msg_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`,
        from: 'macoder',
        to,
        content,
        timestamp: new Date().toISOString(),
        metadata
      };
      
      // In a real implementation, this would send the message to the DMac message bus
      // For now, just log it
      logger.info(`Sending message to ${to}: ${content}`);
      
      return message.id;
    } catch (error) {
      logger.error('Error sending message:', error);
      throw error;
    }
  }
  
  /**
   * Receives messages from other agents
   */
  public async receiveMessages(): Promise<AgentMessage[]> {
    try {
      const config = this.configManager.getConfig();
      
      if (!config.enabled || !config.agentCommunicationEnabled) {
        return [];
      }
      
      // In a real implementation, this would poll the DMac message bus
      // For now, just return the message queue
      const messages = [...this.messageQueue];
      this.messageQueue = [];
      
      return messages;
    } catch (error) {
      logger.error('Error receiving messages:', error);
      return [];
    }
  }
  
  /**
   * Registers a message handler
   */
  public registerMessageHandler(
    handler: (message: AgentMessage) => Promise<void>
  ): void {
    this.messageHandlers.push(handler);
    logger.info('Message handler registered');
  }
  
  /**
   * Processes incoming messages
   */
  public async processMessages(): Promise<void> {
    try {
      const messages = await this.receiveMessages();
      
      for (const message of messages) {
        for (const handler of this.messageHandlers) {
          try {
            await handler(message);
          } catch (error) {
            logger.error('Error processing message:', error);
          }
        }
      }
    } catch (error) {
      logger.error('Error processing messages:', error);
    }
  }
  
  /**
   * Starts the message processing loop
   */
  public startMessageProcessing(): vscode.Disposable {
    const interval = setInterval(() => {
      this.processMessages().catch(error => {
        logger.error('Error in message processing loop:', error);
      });
    }, 5000); // Check for messages every 5 seconds
    
    return {
      dispose: () => {
        clearInterval(interval);
      }
    };
  }
}
