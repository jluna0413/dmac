import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import { logger } from '../core/logger';

/**
 * Feedback type
 */
export enum FeedbackType {
  POSITIVE = 'positive',
  NEGATIVE = 'negative',
  NEUTRAL = 'neutral'
}

/**
 * Feedback item
 */
export interface FeedbackItem {
  id: string;
  timestamp: string;
  prompt: string;
  result: string;
  type: FeedbackType;
  comments?: string;
  modifications?: string;
  language?: string;
  strategy?: string;
}

/**
 * Learning statistics
 */
export interface LearningStats {
  totalFeedback: number;
  positiveFeedback: number;
  negativeFeedback: number;
  neutralFeedback: number;
  feedbackByLanguage: Record<string, number>;
  feedbackByStrategy: Record<string, number>;
  recentFeedback: FeedbackItem[];
}

/**
 * Incremental Learner
 */
export class IncrementalLearner {
  private context: vscode.ExtensionContext;
  private feedbackItems: FeedbackItem[] = [];
  private storageFile: string;

  constructor(context: vscode.ExtensionContext) {
    this.context = context;

    // Set storage file path
    this.storageFile = path.join(context.globalStorageUri.fsPath, 'feedback.json');

    // Create storage directory if it doesn't exist
    const storageDir = path.dirname(this.storageFile);
    if (!fs.existsSync(storageDir)) {
      fs.mkdirSync(storageDir, { recursive: true });
    }

    // Load feedback items
    this.loadFeedbackItems();

    logger.info('Incremental Learner initialized');
  }

  /**
   * Loads feedback items from storage
   */
  private loadFeedbackItems(): void {
    try {
      if (fs.existsSync(this.storageFile)) {
        const data = fs.readFileSync(this.storageFile, 'utf8');
        this.feedbackItems = JSON.parse(data);
        logger.info(`Loaded ${this.feedbackItems.length} feedback items`);
      } else {
        logger.info('No feedback items found');
      }
    } catch (error) {
      logger.error('Error loading feedback items:', error);
      this.feedbackItems = [];
    }
  }

  /**
   * Saves feedback items to storage
   */
  private saveFeedbackItems(): void {
    try {
      const data = JSON.stringify(this.feedbackItems, null, 2);
      fs.writeFileSync(this.storageFile, data, 'utf8');
      logger.info(`Saved ${this.feedbackItems.length} feedback items`);
    } catch (error) {
      logger.error('Error saving feedback items:', error);
    }
  }

  /**
   * Adds a feedback item
   */
  public addFeedback(
    prompt: string,
    result: string,
    type: FeedbackType,
    options?: {
      comments?: string;
      modifications?: string;
      language?: string;
      strategy?: string;
    }
  ): string {
    try {
      // Create feedback item
      const feedbackItem: FeedbackItem = {
        id: `feedback_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`,
        timestamp: new Date().toISOString(),
        prompt,
        result,
        type,
        comments: options?.comments,
        modifications: options?.modifications,
        language: options?.language,
        strategy: options?.strategy
      };

      // Add to feedback items
      this.feedbackItems.push(feedbackItem);

      // Save feedback items
      this.saveFeedbackItems();

      logger.info(`Added feedback item: ${feedbackItem.id}`);

      return feedbackItem.id;
    } catch (error) {
      logger.error('Error adding feedback:', error);
      throw error;
    }
  }

  /**
   * Gets a feedback item by ID
   */
  public getFeedback(id: string): FeedbackItem | undefined {
    return this.feedbackItems.find(item => item.id === id);
  }

  /**
   * Gets all feedback items
   */
  public getAllFeedback(): FeedbackItem[] {
    return [...this.feedbackItems];
  }

  /**
   * Gets feedback items by type
   */
  public getFeedbackByType(type: FeedbackType): FeedbackItem[] {
    return this.feedbackItems.filter(item => item.type === type);
  }

  /**
   * Gets feedback items by language
   */
  public getFeedbackByLanguage(language: string): FeedbackItem[] {
    return this.feedbackItems.filter(item => item.language === language);
  }

  /**
   * Gets feedback items by strategy
   */
  public getFeedbackByStrategy(strategy: string): FeedbackItem[] {
    return this.feedbackItems.filter(item => item.strategy === strategy);
  }

  /**
   * Gets learning statistics
   */
  public getStats(): LearningStats {
    try {
      // Calculate statistics
      const totalFeedback = this.feedbackItems.length;
      const positiveFeedback = this.getFeedbackByType(FeedbackType.POSITIVE).length;
      const negativeFeedback = this.getFeedbackByType(FeedbackType.NEGATIVE).length;
      const neutralFeedback = this.getFeedbackByType(FeedbackType.NEUTRAL).length;

      // Calculate feedback by language
      const feedbackByLanguage: Record<string, number> = {};

      for (const item of this.feedbackItems) {
        if (item.language) {
          feedbackByLanguage[item.language] = (feedbackByLanguage[item.language] || 0) + 1;
        }
      }

      // Calculate feedback by strategy
      const feedbackByStrategy: Record<string, number> = {};

      for (const item of this.feedbackItems) {
        if (item.strategy) {
          feedbackByStrategy[item.strategy] = (feedbackByStrategy[item.strategy] || 0) + 1;
        }
      }

      // Get recent feedback
      const recentFeedback = [...this.feedbackItems]
        .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
        .slice(0, 10);

      return {
        totalFeedback,
        positiveFeedback,
        negativeFeedback,
        neutralFeedback,
        feedbackByLanguage,
        feedbackByStrategy,
        recentFeedback
      };
    } catch (error) {
      logger.error('Error getting learning stats:', error);

      return {
        totalFeedback: 0,
        positiveFeedback: 0,
        negativeFeedback: 0,
        neutralFeedback: 0,
        feedbackByLanguage: {},
        feedbackByStrategy: {},
        recentFeedback: []
      };
    }
  }

  /**
   * Clears all feedback items
   */
  public clearFeedback(): void {
    try {
      this.feedbackItems = [];
      this.saveFeedbackItems();
      logger.info('Cleared all feedback items');
    } catch (error) {
      logger.error('Error clearing feedback:', error);
      throw error;
    }
  }

  /**
   * Gets recommendations based on feedback
   */
  public getRecommendations(
    _prompt: string,
    language: string
  ): { strategy: string; confidence: number } {
    try {
      // In a real implementation, this would analyze feedback and make recommendations
      // For now, return a placeholder

      // Get feedback for the language
      const languageFeedback = this.getFeedbackByLanguage(language);

      if (languageFeedback.length === 0) {
        return { strategy: 'direct', confidence: 0.5 };
      }

      // Count positive feedback by strategy
      const strategyScores: Record<string, { positive: number; total: number }> = {};

      for (const item of languageFeedback) {
        if (item.strategy) {
          if (!strategyScores[item.strategy]) {
            strategyScores[item.strategy] = { positive: 0, total: 0 };
          }

          strategyScores[item.strategy].total++;

          if (item.type === FeedbackType.POSITIVE) {
            strategyScores[item.strategy].positive++;
          }
        }
      }

      // Find the strategy with the highest score
      let bestStrategy = 'direct';
      let bestScore = 0;

      for (const [strategy, scores] of Object.entries(strategyScores)) {
        const score = scores.total > 0 ? scores.positive / scores.total : 0;

        if (score > bestScore) {
          bestStrategy = strategy;
          bestScore = score;
        }
      }

      return { strategy: bestStrategy, confidence: bestScore };
    } catch (error) {
      logger.error('Error getting recommendations:', error);
      return { strategy: 'direct', confidence: 0.5 };
    }
  }
}
