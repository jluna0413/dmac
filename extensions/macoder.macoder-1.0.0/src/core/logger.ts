import * as vscode from 'vscode';

/**
 * Log levels
 */
export enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARN = 2,
  ERROR = 3
}

/**
 * Logger class for MaCoder
 */
class Logger {
  private outputChannel: vscode.OutputChannel | undefined;
  private logLevel: LogLevel = LogLevel.INFO;

  /**
   * Initializes the logger
   */
  public initialize(context: vscode.ExtensionContext): void {
    // Create output channel
    this.outputChannel = vscode.window.createOutputChannel('MaCoder');
    
    // Add to context subscriptions
    context.subscriptions.push(this.outputChannel);
    
    // Get log level from configuration
    this.updateLogLevel();
    
    // Listen for configuration changes
    context.subscriptions.push(
      vscode.workspace.onDidChangeConfiguration(e => {
        if (e.affectsConfiguration('macoder.logLevel')) {
          this.updateLogLevel();
        }
      })
    );
    
    this.info('Logger initialized');
  }

  /**
   * Updates the log level from configuration
   */
  private updateLogLevel(): void {
    const config = vscode.workspace.getConfiguration('macoder');
    const logLevelString = config.get<string>('logLevel', 'info');
    
    switch (logLevelString.toLowerCase()) {
      case 'debug':
        this.logLevel = LogLevel.DEBUG;
        break;
      case 'info':
        this.logLevel = LogLevel.INFO;
        break;
      case 'warn':
        this.logLevel = LogLevel.WARN;
        break;
      case 'error':
        this.logLevel = LogLevel.ERROR;
        break;
      default:
        this.logLevel = LogLevel.INFO;
    }
    
    this.info(`Log level set to ${LogLevel[this.logLevel]}`);
  }

  /**
   * Logs a debug message
   */
  public debug(message: string, ...args: any[]): void {
    this.log(LogLevel.DEBUG, message, ...args);
  }

  /**
   * Logs an info message
   */
  public info(message: string, ...args: any[]): void {
    this.log(LogLevel.INFO, message, ...args);
  }

  /**
   * Logs a warning message
   */
  public warn(message: string, ...args: any[]): void {
    this.log(LogLevel.WARN, message, ...args);
  }

  /**
   * Logs an error message
   */
  public error(message: string, ...args: any[]): void {
    this.log(LogLevel.ERROR, message, ...args);
  }

  /**
   * Logs a message with the specified log level
   */
  private log(level: LogLevel, message: string, ...args: any[]): void {
    if (level < this.logLevel) {
      return;
    }
    
    if (!this.outputChannel) {
      console.log(`[MaCoder] [${LogLevel[level]}] ${message}`, ...args);
      return;
    }
    
    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] [${LogLevel[level]}] ${message}`;
    
    this.outputChannel.appendLine(logMessage);
    
    if (args.length > 0) {
      const argsString = args.map(arg => {
        if (arg instanceof Error) {
          return `${arg.message}\n${arg.stack}`;
        } else if (typeof arg === 'object') {
          return JSON.stringify(arg, null, 2);
        } else {
          return String(arg);
        }
      }).join('\n');
      
      this.outputChannel.appendLine(argsString);
    }
  }
}

// Export singleton instance
export const logger = new Logger();
