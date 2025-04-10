import * as vscode from 'vscode';
import { logger } from '../core/logger';
import { ProviderManager } from '../model-providers/provider-manager';
import { ModelInfo } from '../model-providers/provider-interface';

/**
 * Model browser for browsing and managing models
 */
export class ModelBrowser {
  private static instance: ModelBrowser | undefined;

  private panel: vscode.WebviewPanel | undefined;
  private context: vscode.ExtensionContext;
  private providerManager: ProviderManager;

  private constructor(
    context: vscode.ExtensionContext,
    providerManager: ProviderManager
  ) {
    this.context = context;
    this.providerManager = providerManager;

    logger.info('Model browser initialized');
  }

  /**
   * Gets the model browser instance
   */
  public static getInstance(
    context: vscode.ExtensionContext,
    providerManager: ProviderManager
  ): ModelBrowser {
    if (!ModelBrowser.instance) {
      ModelBrowser.instance = new ModelBrowser(
        context,
        providerManager
      );
    }

    return ModelBrowser.instance;
  }

  /**
   * Shows the model browser
   */
  public async show(): Promise<void> {
    if (this.panel) {
      this.panel.reveal();
      return;
    }

    // Create panel
    this.panel = vscode.window.createWebviewPanel(
      'macoderModelBrowser',
      'MaCoder Model Browser',
      vscode.ViewColumn.One,
      {
        enableScripts: true,
        retainContextWhenHidden: true,
        localResourceRoots: [
          vscode.Uri.joinPath(this.context.extensionUri, 'media')
        ]
      }
    );

    // Set HTML content
    await this.updateContent();

    // Handle messages from the webview
    this.panel.webview.onDidReceiveMessage(
      async message => {
        switch (message.command) {
          case 'setActiveProvider':
            await this.handleSetActiveProvider(message.providerId, message.modelId);
            break;

          case 'refreshModels':
            await this.updateContent();
            break;
        }
      },
      undefined,
      this.context.subscriptions
    );

    // Handle panel disposal
    this.panel.onDidDispose(
      () => {
        this.panel = undefined;
      },
      null,
      this.context.subscriptions
    );
  }

  /**
   * Updates the panel content
   */
  private async updateContent(): Promise<void> {
    if (!this.panel) {
      return;
    }

    try {
      // Get style URI
      const styleUri = this.panel.webview.asWebviewUri(
        vscode.Uri.joinPath(this.context.extensionUri, 'media', 'style.css')
      );

      // Get providers
      const providers = this.providerManager.getProviders();

      // Get active provider
      const activeProvider = this.providerManager.getActiveProvider();

      // Get models
      const models = await this.providerManager.listAllModels();

      // Group models by provider
      const modelsByProvider: Record<string, ModelInfo[]> = {};

      for (const model of models) {
        if (!modelsByProvider[model.provider]) {
          modelsByProvider[model.provider] = [];
        }

        modelsByProvider[model.provider].push(model);
      }

      // Set HTML content
      this.panel.webview.html = `
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>MaCoder Model Browser</title>
          <link href="${styleUri}" rel="stylesheet">
        </head>
        <body>
          <div class="container">
            <h1>MaCoder Model Browser</h1>

            <div class="tabs">
              <div class="tab active" data-tab="browse-models">Browse Models</div>
              <div class="tab" data-tab="installed-models">Installed Models</div>
            </div>

            <div class="tab-content active" id="browse-models">
              <h2>Browse Models</h2>

              <div class="form-group">
                <label for="model-search">Search</label>
                <input type="text" id="model-search" placeholder="Search models">
              </div>

              <div class="form-group">
                <label for="model-provider-filter">Provider</label>
                <select id="model-provider-filter">
                  <option value="all">All Providers</option>
                  ${providers.map(provider => `<option value="${provider.id}">${provider.name}</option>`).join('')}
                </select>
              </div>

              <div class="form-group">
                <label for="model-sort">Sort By</label>
                <select id="model-sort">
                  <option value="name">Name</option>
                  <option value="size">Size</option>
                  <option value="provider">Provider</option>
                </select>
              </div>

              <button id="refresh-models-button">Refresh Models</button>

              <div class="grid">
                ${Object.entries(modelsByProvider).map(([providerName, providerModels]) => `
                  <div class="provider-section">
                    <h3>${providerName}</h3>
                    ${providerModels.map(model => `
                      <div class="card model-card" data-provider="${model.provider}" data-model-id="${model.id}" data-name="${model.name}" data-size="${model.size}">
                        <div class="card-title">${model.name}</div>
                        <div class="card-body">
                          <p>${model.description}</p>
                          <p>Size: ${model.size}</p>
                          <div class="tags">
                            ${model.tags.map(tag => `<span class="badge">${tag}</span>`).join('')}
                          </div>
                        </div>
                        <div class="card-footer">
                          <button class="set-active-button" data-provider-id="${providers.find(p => p.name === model.provider)?.id}" data-model-id="${model.id}">
                            ${activeProvider && activeProvider.model.id === model.id ? 'Active' : 'Set Active'}
                          </button>
                        </div>
                      </div>
                    `).join('')}
                  </div>
                `).join('')}
              </div>
            </div>

            <div class="tab-content" id="installed-models">
              <h2>Installed Models</h2>

              <div class="grid">
                ${Object.entries(modelsByProvider)
          .filter(([_, providerModels]) => providerModels.some(model => model.localPath))
          .map(([providerName, providerModels]) => `
                    <div class="provider-section">
                      <h3>${providerName}</h3>
                      ${providerModels
              .filter(model => model.localPath)
              .map(model => `
                          <div class="card model-card" data-provider="${model.provider}" data-model-id="${model.id}" data-name="${model.name}" data-size="${model.size}">
                            <div class="card-title">${model.name}</div>
                            <div class="card-body">
                              <p>${model.description}</p>
                              <p>Size: ${model.size}</p>
                              <div class="tags">
                                ${model.tags.map(tag => `<span class="badge">${tag}</span>`).join('')}
                              </div>
                            </div>
                            <div class="card-footer">
                              <button class="set-active-button" data-provider-id="${providers.find(p => p.name === model.provider)?.id}" data-model-id="${model.id}">
                                ${activeProvider && activeProvider.model.id === model.id ? 'Active' : 'Set Active'}
                              </button>
                            </div>
                          </div>
                        `).join('')}
                    </div>
                  `).join('')}
              </div>
            </div>
          </div>

          <script>
            (function() {
              // Initialize tabs
              const tabs = document.querySelectorAll('.tabs .tab');
              const tabContents = document.querySelectorAll('.tab-content');

              tabs.forEach(tab => {
                tab.addEventListener('click', () => {
                  // Remove active class from all tabs and contents
                  tabs.forEach(t => t.classList.remove('active'));
                  tabContents.forEach(c => c.classList.remove('active'));

                  // Add active class to clicked tab and corresponding content
                  tab.classList.add('active');
                  const tabId = tab.getAttribute('data-tab');
                  document.getElementById(tabId).classList.add('active');
                });
              });

              // Initialize search
              const searchInput = document.getElementById('model-search');
              const providerFilter = document.getElementById('model-provider-filter');
              const sortSelect = document.getElementById('model-sort');
              const modelCards = document.querySelectorAll('.model-card');

              function filterModels() {
                const searchTerm = searchInput.value.toLowerCase();
                const providerValue = providerFilter.value;
                const sortValue = sortSelect.value;

                // Filter models
                modelCards.forEach(card => {
                  const name = card.getAttribute('data-name').toLowerCase();
                  const provider = card.getAttribute('data-provider');

                  const matchesSearch = name.includes(searchTerm);
                  const matchesProvider = providerValue === 'all' || provider === providerValue;

                  if (matchesSearch && matchesProvider) {
                    card.style.display = '';
                  } else {
                    card.style.display = 'none';
                  }
                });

                // Sort models
                const sortedCards = Array.from(modelCards).sort((a, b) => {
                  if (sortValue === 'name') {
                    return a.getAttribute('data-name').localeCompare(b.getAttribute('data-name'));
                  } else if (sortValue === 'size') {
                    return a.getAttribute('data-size').localeCompare(b.getAttribute('data-size'));
                  } else if (sortValue === 'provider') {
                    return a.getAttribute('data-provider').localeCompare(b.getAttribute('data-provider'));
                  }

                  return 0;
                });

                // Reorder models
                sortedCards.forEach(card => {
                  card.parentElement.appendChild(card);
                });
              }

              searchInput.addEventListener('input', filterModels);
              providerFilter.addEventListener('change', filterModels);
              sortSelect.addEventListener('change', filterModels);

              // Initialize set active buttons
              const setActiveButtons = document.querySelectorAll('.set-active-button');

              setActiveButtons.forEach(button => {
                button.addEventListener('click', () => {
                  const providerId = button.getAttribute('data-provider-id');
                  const modelId = button.getAttribute('data-model-id');

                  vscode.postMessage({
                    command: 'setActiveProvider',
                    providerId,
                    modelId
                  });
                });
              });

              // Initialize refresh button
              document.getElementById('refresh-models-button').addEventListener('click', () => {
                vscode.postMessage({
                  command: 'refreshModels'
                });
              });

              // Initialize vscode API
              const vscode = acquireVsCodeApi();
            })();
          </script>
        </body>
        </html>
      `;
    } catch (error: any) {
      logger.error('Error updating model browser content:', error);

      // Show error message
      if (this.panel) {
        this.panel.webview.html = `
          <!DOCTYPE html>
          <html lang="en">
          <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>MaCoder Model Browser</title>
          </head>
          <body>
            <div class="container">
              <h1>MaCoder Model Browser</h1>

              <div class="alert alert-error">
                <p>Error loading models: ${error.message}</p>
              </div>

              <button id="refresh-models-button">Refresh Models</button>
            </div>

            <script>
              (function() {
                // Initialize refresh button
                document.getElementById('refresh-models-button').addEventListener('click', () => {
                  vscode.postMessage({
                    command: 'refreshModels'
                  });
                });

                // Initialize vscode API
                const vscode = acquireVsCodeApi();
              })();
            </script>
          </body>
          </html>
        `;
      }
    }
  }

  /**
   * Handles set active provider request
   */
  private async handleSetActiveProvider(
    providerId: string,
    modelId: string
  ): Promise<void> {
    try {
      // Set active provider
      await this.providerManager.setActiveProvider(providerId, modelId);

      // Update content
      await this.updateContent();

      // Show success message
      vscode.window.showInformationMessage(`Active model set to ${modelId}`);
    } catch (error: any) {
      logger.error('Error setting active provider:', error);
      vscode.window.showErrorMessage(`Error setting active provider: ${error.message}`);
    }
  }
}
