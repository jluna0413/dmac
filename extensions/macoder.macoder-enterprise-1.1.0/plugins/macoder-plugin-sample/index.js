/**
 * Sample plugin for MaCoder
 */
class Plugin {
  constructor() {
    this.id = 'macoder-plugin-sample';
    this.name = 'MaCoder Sample Plugin';
    this.description = 'A sample plugin for MaCoder';
    this.version = '1.0.0';
  }
  
  /**
   * Activates the plugin
   */
  activate(context) {
    console.log('MaCoder Sample Plugin activated');
    
    // Register a command
    const command = vscode.commands.registerCommand('macoder-plugin-sample.hello', () => {
      vscode.window.showInformationMessage('Hello from MaCoder Sample Plugin!');
    });
    
    // Add to subscriptions
    context.subscriptions.push(command);
  }
  
  /**
   * Deactivates the plugin
   */
  deactivate() {
    console.log('MaCoder Sample Plugin deactivated');
  }
}

// Export the plugin class
exports.Plugin = Plugin;
