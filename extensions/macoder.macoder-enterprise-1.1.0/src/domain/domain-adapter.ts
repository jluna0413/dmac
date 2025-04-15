import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import { logger } from '../core/logger';

/**
 * Domain type
 */
export enum DomainType {
  WEB_FRONTEND = 'web-frontend',
  WEB_BACKEND = 'web-backend',
  MOBILE = 'mobile',
  DESKTOP = 'desktop',
  DATA_SCIENCE = 'data-science',
  MACHINE_LEARNING = 'machine-learning',
  DEVOPS = 'devops',
  GAME_DEVELOPMENT = 'game-development',
  EMBEDDED = 'embedded',
  BLOCKCHAIN = 'blockchain',
  UNKNOWN = 'unknown'
}

/**
 * Framework info
 */
export interface FrameworkInfo {
  name: string;
  type: string;
  language: string;
  patterns: string[];
  bestPractices: string[];
}

/**
 * Domain info
 */
export interface DomainInfo {
  type: DomainType;
  frameworks: FrameworkInfo[];
  languages: string[];
  patterns: string[];
  knowledgeBase: string[];
}

/**
 * Domain Adapter
 */
export class DomainAdapter {
  private context: vscode.ExtensionContext;
  private domainInfo: DomainInfo | undefined;
  private frameworksData: Record<string, FrameworkInfo> = {};
  
  constructor(context: vscode.ExtensionContext) {
    this.context = context;
    
    // Load frameworks data
    this.loadFrameworksData();
    
    logger.info('Domain Adapter initialized');
  }
  
  /**
   * Loads frameworks data
   */
  private loadFrameworksData(): void {
    try {
      // In a real implementation, this would load from a JSON file or database
      // For now, use hardcoded data
      
      this.frameworksData = {
        'react': {
          name: 'React',
          type: 'frontend',
          language: 'javascript',
          patterns: ['components', 'hooks', 'jsx', 'virtual dom'],
          bestPractices: [
            'Use functional components with hooks',
            'Keep components small and focused',
            'Use prop types or TypeScript for type checking',
            'Use React.memo for performance optimization'
          ]
        },
        'angular': {
          name: 'Angular',
          type: 'frontend',
          language: 'typescript',
          patterns: ['components', 'services', 'modules', 'dependency injection'],
          bestPractices: [
            'Follow Angular style guide',
            'Use lazy loading for modules',
            'Implement OnPush change detection',
            'Use Angular CLI for project management'
          ]
        },
        'vue': {
          name: 'Vue.js',
          type: 'frontend',
          language: 'javascript',
          patterns: ['components', 'directives', 'vue files', 'reactivity'],
          bestPractices: [
            'Use Vue CLI for project setup',
            'Use single-file components',
            'Use Vuex for state management',
            'Follow Vue style guide'
          ]
        },
        'express': {
          name: 'Express',
          type: 'backend',
          language: 'javascript',
          patterns: ['middleware', 'routes', 'controllers', 'rest api'],
          bestPractices: [
            'Use middleware for cross-cutting concerns',
            'Implement proper error handling',
            'Use environment variables for configuration',
            'Implement input validation'
          ]
        },
        'django': {
          name: 'Django',
          type: 'backend',
          language: 'python',
          patterns: ['models', 'views', 'templates', 'orm'],
          bestPractices: [
            'Follow Django project structure',
            'Use Django ORM for database operations',
            'Implement proper authentication and authorization',
            'Write tests for views and models'
          ]
        },
        'spring': {
          name: 'Spring',
          type: 'backend',
          language: 'java',
          patterns: ['beans', 'controllers', 'services', 'dependency injection'],
          bestPractices: [
            'Use Spring Boot for application setup',
            'Implement proper exception handling',
            'Use Spring Security for authentication',
            'Follow Spring project structure'
          ]
        },
        'flutter': {
          name: 'Flutter',
          type: 'mobile',
          language: 'dart',
          patterns: ['widgets', 'stateful', 'stateless', 'material design'],
          bestPractices: [
            'Use stateless widgets when possible',
            'Implement proper state management',
            'Follow Flutter style guide',
            'Use Flutter DevTools for debugging'
          ]
        },
        'react-native': {
          name: 'React Native',
          type: 'mobile',
          language: 'javascript',
          patterns: ['components', 'native modules', 'jsx', 'bridge'],
          bestPractices: [
            'Use functional components with hooks',
            'Implement proper navigation',
            'Use native modules when necessary',
            'Follow React Native style guide'
          ]
        },
        'tensorflow': {
          name: 'TensorFlow',
          type: 'machine-learning',
          language: 'python',
          patterns: ['models', 'layers', 'tensors', 'graphs'],
          bestPractices: [
            'Use TensorFlow 2.x API',
            'Implement proper data preprocessing',
            'Use TensorBoard for visualization',
            'Implement model checkpointing'
          ]
        },
        'pytorch': {
          name: 'PyTorch',
          type: 'machine-learning',
          language: 'python',
          patterns: ['tensors', 'autograd', 'neural networks', 'optimizers'],
          bestPractices: [
            'Use PyTorch Lightning for high-level abstractions',
            'Implement proper data loading',
            'Use GPU acceleration when available',
            'Implement model checkpointing'
          ]
        }
      };
      
      logger.info(`Loaded ${Object.keys(this.frameworksData).length} frameworks`);
    } catch (error) {
      logger.error('Error loading frameworks data:', error);
      this.frameworksData = {};
    }
  }
  
  /**
   * Detects the domain of the current project
   */
  public async detectDomain(): Promise<DomainInfo> {
    try {
      // If domain info is already detected, return it
      if (this.domainInfo) {
        return this.domainInfo;
      }
      
      logger.info('Detecting domain...');
      
      // Get workspace folders
      const workspaceFolders = vscode.workspace.workspaceFolders;
      
      if (!workspaceFolders || workspaceFolders.length === 0) {
        logger.warn('No workspace folders found');
        return this.createUnknownDomain();
      }
      
      // Get the first workspace folder
      const workspaceFolder = workspaceFolders[0];
      const workspacePath = workspaceFolder.uri.fsPath;
      
      // Detect frameworks
      const detectedFrameworks = await this.detectFrameworks(workspacePath);
      
      // Detect languages
      const detectedLanguages = await this.detectLanguages(workspacePath);
      
      // Determine domain type
      const domainType = this.determineDomainType(detectedFrameworks, detectedLanguages);
      
      // Create domain info
      this.domainInfo = {
        type: domainType,
        frameworks: detectedFrameworks,
        languages: detectedLanguages,
        patterns: this.extractPatterns(detectedFrameworks),
        knowledgeBase: this.createKnowledgeBase(domainType, detectedFrameworks, detectedLanguages)
      };
      
      logger.info(`Detected domain: ${domainType}`);
      
      return this.domainInfo;
    } catch (error) {
      logger.error('Error detecting domain:', error);
      return this.createUnknownDomain();
    }
  }
  
  /**
   * Creates an unknown domain
   */
  private createUnknownDomain(): DomainInfo {
    return {
      type: DomainType.UNKNOWN,
      frameworks: [],
      languages: [],
      patterns: [],
      knowledgeBase: []
    };
  }
  
  /**
   * Detects frameworks in a project
   */
  private async detectFrameworks(projectPath: string): Promise<FrameworkInfo[]> {
    try {
      const detectedFrameworks: FrameworkInfo[] = [];
      
      // Check for package.json
      const packageJsonPath = path.join(projectPath, 'package.json');
      
      if (fs.existsSync(packageJsonPath)) {
        try {
          const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
          
          // Check dependencies
          const dependencies = {
            ...(packageJson.dependencies || {}),
            ...(packageJson.devDependencies || {})
          };
          
          // Check for frameworks
          for (const [name, info] of Object.entries(this.frameworksData)) {
            if (dependencies[name]) {
              detectedFrameworks.push(info);
            }
          }
        } catch (error) {
          logger.warn(`Error parsing package.json at ${packageJsonPath}:`, error);
        }
      }
      
      // Check for requirements.txt
      const requirementsPath = path.join(projectPath, 'requirements.txt');
      
      if (fs.existsSync(requirementsPath)) {
        try {
          const requirements = fs.readFileSync(requirementsPath, 'utf8');
          
          // Check for frameworks
          for (const [name, info] of Object.entries(this.frameworksData)) {
            if (info.language === 'python' && requirements.includes(name)) {
              detectedFrameworks.push(info);
            }
          }
        } catch (error) {
          logger.warn(`Error parsing requirements.txt at ${requirementsPath}:`, error);
        }
      }
      
      // Check for pom.xml
      const pomPath = path.join(projectPath, 'pom.xml');
      
      if (fs.existsSync(pomPath)) {
        try {
          const pom = fs.readFileSync(pomPath, 'utf8');
          
          // Check for frameworks
          for (const [name, info] of Object.entries(this.frameworksData)) {
            if (info.language === 'java' && pom.includes(name)) {
              detectedFrameworks.push(info);
            }
          }
        } catch (error) {
          logger.warn(`Error parsing pom.xml at ${pomPath}:`, error);
        }
      }
      
      // Check for pubspec.yaml
      const pubspecPath = path.join(projectPath, 'pubspec.yaml');
      
      if (fs.existsSync(pubspecPath)) {
        try {
          const pubspec = fs.readFileSync(pubspecPath, 'utf8');
          
          // Check for frameworks
          for (const [name, info] of Object.entries(this.frameworksData)) {
            if (info.language === 'dart' && pubspec.includes(name)) {
              detectedFrameworks.push(info);
            }
          }
        } catch (error) {
          logger.warn(`Error parsing pubspec.yaml at ${pubspecPath}:`, error);
        }
      }
      
      return detectedFrameworks;
    } catch (error) {
      logger.error(`Error detecting frameworks in ${projectPath}:`, error);
      return [];
    }
  }
  
  /**
   * Detects languages in a project
   */
  private async detectLanguages(projectPath: string): Promise<string[]> {
    try {
      const languages = new Set<string>();
      
      // Find files in the project
      const uris = await vscode.workspace.findFiles(
        new vscode.RelativePattern(projectPath, '**/*.{js,ts,jsx,tsx,py,java,c,cpp,cs,go,rb,php,html,css,dart}'),
        new vscode.RelativePattern(projectPath, '**/node_modules/**')
      );
      
      // Count files by extension
      const extensionCounts: Record<string, number> = {};
      
      for (const uri of uris) {
        const extension = path.extname(uri.fsPath).toLowerCase();
        extensionCounts[extension] = (extensionCounts[extension] || 0) + 1;
      }
      
      // Map extensions to languages
      const extensionToLanguage: Record<string, string> = {
        '.js': 'javascript',
        '.ts': 'typescript',
        '.jsx': 'javascript',
        '.tsx': 'typescript',
        '.py': 'python',
        '.java': 'java',
        '.c': 'c',
        '.cpp': 'c++',
        '.cs': 'c#',
        '.go': 'go',
        '.rb': 'ruby',
        '.php': 'php',
        '.html': 'html',
        '.css': 'css',
        '.dart': 'dart'
      };
      
      // Add languages with more than 5 files
      for (const [extension, count] of Object.entries(extensionCounts)) {
        if (count >= 5 && extensionToLanguage[extension]) {
          languages.add(extensionToLanguage[extension]);
        }
      }
      
      return Array.from(languages);
    } catch (error) {
      logger.error(`Error detecting languages in ${projectPath}:`, error);
      return [];
    }
  }
  
  /**
   * Determines the domain type based on frameworks and languages
   */
  private determineDomainType(
    frameworks: FrameworkInfo[],
    languages: string[]
  ): DomainType {
    try {
      // Count frameworks by type
      const typeCounts: Record<string, number> = {};
      
      for (const framework of frameworks) {
        typeCounts[framework.type] = (typeCounts[framework.type] || 0) + 1;
      }
      
      // Determine domain type based on framework types
      if (typeCounts['frontend'] && typeCounts['backend']) {
        return DomainType.WEB_FRONTEND;
      } else if (typeCounts['frontend']) {
        return DomainType.WEB_FRONTEND;
      } else if (typeCounts['backend']) {
        return DomainType.WEB_BACKEND;
      } else if (typeCounts['mobile']) {
        return DomainType.MOBILE;
      } else if (typeCounts['machine-learning']) {
        return DomainType.MACHINE_LEARNING;
      }
      
      // Determine domain type based on languages
      if (languages.includes('python') && (
        languages.includes('jupyter') ||
        languages.includes('r')
      )) {
        return DomainType.DATA_SCIENCE;
      } else if (languages.includes('c') || languages.includes('c++')) {
        return DomainType.EMBEDDED;
      } else if (languages.includes('javascript') || languages.includes('typescript')) {
        return DomainType.WEB_FRONTEND;
      } else if (languages.includes('java') || languages.includes('c#')) {
        return DomainType.DESKTOP;
      }
      
      return DomainType.UNKNOWN;
    } catch (error) {
      logger.error('Error determining domain type:', error);
      return DomainType.UNKNOWN;
    }
  }
  
  /**
   * Extracts patterns from frameworks
   */
  private extractPatterns(frameworks: FrameworkInfo[]): string[] {
    try {
      const patterns = new Set<string>();
      
      for (const framework of frameworks) {
        for (const pattern of framework.patterns) {
          patterns.add(pattern);
        }
      }
      
      return Array.from(patterns);
    } catch (error) {
      logger.error('Error extracting patterns:', error);
      return [];
    }
  }
  
  /**
   * Creates a knowledge base for the domain
   */
  private createKnowledgeBase(
    domainType: DomainType,
    frameworks: FrameworkInfo[],
    languages: string[]
  ): string[] {
    try {
      const knowledgeBase: string[] = [];
      
      // Add domain-specific knowledge
      switch (domainType) {
        case DomainType.WEB_FRONTEND:
          knowledgeBase.push(
            'Web frontend development focuses on creating user interfaces for web applications',
            'Key concerns include responsiveness, accessibility, and browser compatibility',
            'Common patterns include component-based architecture and state management'
          );
          break;
        case DomainType.WEB_BACKEND:
          knowledgeBase.push(
            'Web backend development focuses on server-side logic and data management',
            'Key concerns include security, performance, and scalability',
            'Common patterns include RESTful APIs, middleware, and database abstraction'
          );
          break;
        case DomainType.MOBILE:
          knowledgeBase.push(
            'Mobile development focuses on creating applications for mobile devices',
            'Key concerns include performance, battery usage, and device compatibility',
            'Common patterns include responsive layouts and offline-first design'
          );
          break;
        case DomainType.DESKTOP:
          knowledgeBase.push(
            'Desktop development focuses on creating applications for desktop operating systems',
            'Key concerns include performance, native integration, and cross-platform compatibility',
            'Common patterns include MVC architecture and native API integration'
          );
          break;
        case DomainType.DATA_SCIENCE:
          knowledgeBase.push(
            'Data science focuses on extracting insights from data',
            'Key concerns include data cleaning, analysis, and visualization',
            'Common patterns include data pipelines and statistical analysis'
          );
          break;
        case DomainType.MACHINE_LEARNING:
          knowledgeBase.push(
            'Machine learning focuses on creating models that learn from data',
            'Key concerns include model accuracy, training efficiency, and inference performance',
            'Common patterns include supervised learning, unsupervised learning, and reinforcement learning'
          );
          break;
      }
      
      // Add framework-specific knowledge
      for (const framework of frameworks) {
        knowledgeBase.push(`${framework.name} is a ${framework.type} framework for ${framework.language}`);
        
        for (const practice of framework.bestPractices) {
          knowledgeBase.push(`${framework.name} best practice: ${practice}`);
        }
      }
      
      // Add language-specific knowledge
      for (const language of languages) {
        switch (language) {
          case 'javascript':
            knowledgeBase.push(
              'JavaScript is a dynamic language commonly used for web development',
              'Key features include first-class functions, prototypal inheritance, and asynchronous programming'
            );
            break;
          case 'typescript':
            knowledgeBase.push(
              'TypeScript is a statically typed superset of JavaScript',
              'Key features include interfaces, generics, and type inference'
            );
            break;
          case 'python':
            knowledgeBase.push(
              'Python is a high-level language known for its readability and simplicity',
              'Key features include dynamic typing, list comprehensions, and extensive standard library'
            );
            break;
          case 'java':
            knowledgeBase.push(
              'Java is a statically typed, object-oriented language',
              'Key features include platform independence, strong typing, and garbage collection'
            );
            break;
        }
      }
      
      return knowledgeBase;
    } catch (error) {
      logger.error('Error creating knowledge base:', error);
      return [];
    }
  }
  
  /**
   * Gets domain-specific code snippets
   */
  public getDomainSnippets(language: string): Record<string, string> {
    try {
      // Detect domain if not already detected
      if (!this.domainInfo) {
        this.detectDomain().catch(error => {
          logger.error('Error detecting domain:', error);
        });
        
        return {};
      }
      
      // Get snippets based on domain and language
      const snippets: Record<string, string> = {};
      
      // Add language-specific snippets
      switch (language) {
        case 'javascript':
        case 'typescript':
          snippets['function'] = 'function functionName(param1, param2) {\n  // Function body\n  return result;\n}';
          snippets['arrow-function'] = 'const functionName = (param1, param2) => {\n  // Function body\n  return result;\n}';
          snippets['class'] = 'class ClassName {\n  constructor(param1, param2) {\n    this.param1 = param1;\n    this.param2 = param2;\n  }\n  \n  methodName() {\n    // Method body\n  }\n}';
          break;
        case 'python':
          snippets['function'] = 'def function_name(param1, param2):\n    # Function body\n    return result';
          snippets['class'] = 'class ClassName:\n    def __init__(self, param1, param2):\n        self.param1 = param1\n        self.param2 = param2\n    \n    def method_name(self):\n        # Method body\n        pass';
          break;
        case 'java':
          snippets['class'] = 'public class ClassName {\n    private String param1;\n    private int param2;\n    \n    public ClassName(String param1, int param2) {\n        this.param1 = param1;\n        this.param2 = param2;\n    }\n    \n    public void methodName() {\n        // Method body\n    }\n}';
          snippets['method'] = 'public ReturnType methodName(ParamType param1, ParamType param2) {\n    // Method body\n    return result;\n}';
          break;
      }
      
      // Add domain-specific snippets
      switch (this.domainInfo.type) {
        case DomainType.WEB_FRONTEND:
          if (language === 'javascript' || language === 'typescript') {
            snippets['react-component'] = 'import React from \'react\';\n\nfunction ComponentName({ prop1, prop2 }) {\n  return (\n    <div>\n      {/* Component content */}\n    </div>\n  );\n}\n\nexport default ComponentName;';
            snippets['react-hook'] = 'import { useState, useEffect } from \'react\';\n\nfunction useHookName(param) {\n  const [state, setState] = useState(initialState);\n  \n  useEffect(() => {\n    // Effect logic\n    return () => {\n      // Cleanup logic\n    };\n  }, [param]);\n  \n  return state;\n}';
          }
          break;
        case DomainType.WEB_BACKEND:
          if (language === 'javascript' || language === 'typescript') {
            snippets['express-route'] = 'app.get(\'/path\', (req, res) => {\n  // Route handler\n  res.json({ message: \'Response\' });\n});';
            snippets['express-middleware'] = 'function middlewareName(req, res, next) {\n  // Middleware logic\n  next();\n}';
          } else if (language === 'python') {
            snippets['flask-route'] = '@app.route(\'/path\', methods=[\'GET\'])\ndef route_handler():\n    # Route handler\n    return jsonify({\'message\': \'Response\'})';
            snippets['django-view'] = 'from django.http import JsonResponse\n\ndef view_name(request):\n    # View logic\n    return JsonResponse({\'message\': \'Response\'})';
          }
          break;
        case DomainType.MACHINE_LEARNING:
          if (language === 'python') {
            snippets['tensorflow-model'] = 'import tensorflow as tf\n\ndef create_model():\n    model = tf.keras.Sequential([\n        tf.keras.layers.Dense(128, activation=\'relu\', input_shape=(input_dim,)),\n        tf.keras.layers.Dense(64, activation=\'relu\'),\n        tf.keras.layers.Dense(output_dim, activation=\'softmax\')\n    ])\n    \n    model.compile(\n        optimizer=\'adam\',\n        loss=\'sparse_categorical_crossentropy\',\n        metrics=[\'accuracy\']\n    )\n    \n    return model';
            snippets['pytorch-model'] = 'import torch\nimport torch.nn as nn\n\nclass ModelName(nn.Module):\n    def __init__(self, input_dim, output_dim):\n        super(ModelName, self).__init__()\n        self.layer1 = nn.Linear(input_dim, 128)\n        self.layer2 = nn.Linear(128, 64)\n        self.layer3 = nn.Linear(64, output_dim)\n        self.relu = nn.ReLU()\n    \n    def forward(self, x):\n        x = self.relu(self.layer1(x))\n        x = self.relu(self.layer2(x))\n        x = self.layer3(x)\n        return x';
          }
          break;
      }
      
      return snippets;
    } catch (error) {
      logger.error('Error getting domain snippets:', error);
      return {};
    }
  }
  
  /**
   * Gets domain-specific recommendations
   */
  public getDomainRecommendations(code: string, language: string): string[] {
    try {
      // Detect domain if not already detected
      if (!this.domainInfo) {
        this.detectDomain().catch(error => {
          logger.error('Error detecting domain:', error);
        });
        
        return [];
      }
      
      // Get recommendations based on domain, language, and code
      const recommendations: string[] = [];
      
      // Add language-specific recommendations
      switch (language) {
        case 'javascript':
        case 'typescript':
          if (code.includes('var ')) {
            recommendations.push('Use const or let instead of var for variable declarations');
          }
          if (code.includes('function(') && !code.includes('=>')) {
            recommendations.push('Consider using arrow functions for more concise syntax');
          }
          break;
        case 'python':
          if (code.includes('print ')) {
            recommendations.push('Use print() function instead of print statement');
          }
          if (code.includes('except:')) {
            recommendations.push('Avoid bare except clauses, specify the exception type');
          }
          break;
        case 'java':
          if (code.includes('public static void main')) {
            recommendations.push('Consider using a more modular approach with separate classes for different concerns');
          }
          break;
      }
      
      // Add domain-specific recommendations
      switch (this.domainInfo.type) {
        case DomainType.WEB_FRONTEND:
          if ((language === 'javascript' || language === 'typescript') && code.includes('document.getElementById')) {
            recommendations.push('Consider using a framework like React or Vue for DOM manipulation');
          }
          break;
        case DomainType.WEB_BACKEND:
          if ((language === 'javascript' || language === 'typescript') && code.includes('app.get(') && !code.includes('try') && !code.includes('catch')) {
            recommendations.push('Implement error handling in route handlers using try-catch blocks');
          }
          break;
        case DomainType.MACHINE_LEARNING:
          if (language === 'python' && code.includes('model.fit(') && !code.includes('validation_data')) {
            recommendations.push('Include validation data when training models to monitor for overfitting');
          }
          break;
      }
      
      return recommendations;
    } catch (error) {
      logger.error('Error getting domain recommendations:', error);
      return [];
    }
  }
}
