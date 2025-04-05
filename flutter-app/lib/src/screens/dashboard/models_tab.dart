import 'package:flutter/material.dart';
import 'package:dmac_app/src/models/model_model.dart';
import 'package:dmac_app/src/widgets/loading_indicator.dart';

/// Tab for displaying and managing AI models
class ModelsTab extends StatefulWidget {
  const ModelsTab({Key? key}) : super(key: key);

  @override
  State<ModelsTab> createState() => _ModelsTabState();
}

class _ModelsTabState extends State<ModelsTab> {
  bool _isLoading = true;
  List<AIModel> _models = [];
  String? _error;
  ModelProvider? _selectedProvider;

  @override
  void initState() {
    super.initState();
    _loadModels();
  }

  Future<void> _loadModels() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      // Simulate API call delay
      await Future.delayed(const Duration(seconds: 1));

      // Mock data for models
      setState(() {
        _models = [
          AIModel(
            id: 'gemma3:12b',
            name: 'Gemma 3 (12B)',
            description: 'Google\'s Gemma 3 model with 12 billion parameters',
            provider: ModelProvider.ollama,
            type: ModelType.text,
            status: ModelStatus.available,
            parameterCount: 12,
            version: '3.0',
            benchmarks: {
              'mmlu': 78.5,
              'hellaswag': 85.2,
              'truthfulqa': 62.3,
            },
            metadata: {
              'context_length': 8192,
              'disk_size_gb': 24.5,
            },
          ),
          AIModel(
            id: 'llama3:8b',
            name: 'Llama 3 (8B)',
            description: 'Meta\'s Llama 3 model with 8 billion parameters',
            provider: ModelProvider.ollama,
            type: ModelType.text,
            status: ModelStatus.available,
            parameterCount: 8,
            version: '3.0',
            benchmarks: {
              'mmlu': 70.2,
              'hellaswag': 82.7,
              'truthfulqa': 58.1,
            },
            metadata: {
              'context_length': 4096,
              'disk_size_gb': 16.2,
            },
          ),
          AIModel(
            id: 'mistral:7b',
            name: 'Mistral (7B)',
            description: 'Mistral AI\'s 7 billion parameter model',
            provider: ModelProvider.ollama,
            type: ModelType.text,
            status: ModelStatus.available,
            parameterCount: 7,
            version: '1.0',
            benchmarks: {
              'mmlu': 68.9,
              'hellaswag': 81.3,
              'truthfulqa': 55.8,
            },
            metadata: {
              'context_length': 4096,
              'disk_size_gb': 14.8,
            },
          ),
          AIModel(
            id: 'gpt-4o',
            name: 'GPT-4o',
            description: 'OpenAI\'s GPT-4o multimodal model',
            provider: ModelProvider.openAI,
            type: ModelType.multimodal,
            status: ModelStatus.available,
            parameterCount: null, // Unknown
            version: '1.0',
            benchmarks: {
              'mmlu': 89.5,
              'hellaswag': 95.3,
              'truthfulqa': 72.6,
            },
            metadata: {
              'context_length': 128000,
              'api_required': true,
            },
          ),
          AIModel(
            id: 'claude-3-opus',
            name: 'Claude 3 Opus',
            description: 'Anthropic\'s Claude 3 Opus model',
            provider: ModelProvider.anthropic,
            type: ModelType.multimodal,
            status: ModelStatus.available,
            parameterCount: null, // Unknown
            version: '3.0',
            benchmarks: {
              'mmlu': 88.7,
              'hellaswag': 94.2,
              'truthfulqa': 71.8,
            },
            metadata: {
              'context_length': 200000,
              'api_required': true,
            },
          ),
          AIModel(
            id: 'gemini-1.5-pro',
            name: 'Gemini 1.5 Pro',
            description: 'Google\'s Gemini 1.5 Pro multimodal model',
            provider: ModelProvider.google,
            type: ModelType.multimodal,
            status: ModelStatus.available,
            parameterCount: null, // Unknown
            version: '1.5',
            benchmarks: {
              'mmlu': 87.9,
              'hellaswag': 93.1,
              'truthfulqa': 70.5,
            },
            metadata: {
              'context_length': 1000000,
              'api_required': true,
            },
          ),
          AIModel(
            id: 'deepseek-coder',
            name: 'DeepSeek Coder',
            description: 'Specialized coding model for development tasks',
            provider: ModelProvider.ollama,
            type: ModelType.text,
            status: ModelStatus.downloading,
            parameterCount: 7,
            version: '1.0',
            benchmarks: {
              'humaneval': 72.5,
              'mbpp': 68.3,
            },
            metadata: {
              'context_length': 16384,
              'disk_size_gb': 15.3,
              'download_progress': 65,
            },
          ),
          AIModel(
            id: 'macoder-custom',
            name: 'MaCoder Custom',
            description: 'Custom-trained model for the MaCoder agent',
            provider: ModelProvider.custom,
            type: ModelType.text,
            status: ModelStatus.training,
            parameterCount: 12,
            version: '1.0',
            benchmarks: null,
            metadata: {
              'base_model': 'gemma3:12b',
              'training_progress': 45,
              'estimated_completion': '2 hours',
            },
          ),
        ];
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = 'Failed to load models: ${e.toString()}';
        _isLoading = false;
      });
    }
  }

  List<AIModel> _getFilteredModels() {
    if (_selectedProvider == null) {
      return _models;
    }
    return _models.where((model) => model.provider == _selectedProvider).toList();
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const LoadingIndicator(message: 'Loading models...');
    }

    if (_error != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.error_outline,
              size: 48,
              color: Colors.red,
            ),
            const SizedBox(height: 16),
            Text(
              'Error',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            Text(_error!),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _loadModels,
              child: const Text('Retry'),
            ),
          ],
        ),
      );
    }

    if (_models.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.model_training,
              size: 48,
              color: Colors.grey,
            ),
            const SizedBox(height: 16),
            Text(
              'No Models Found',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            const Text('Add your first model to get started'),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () {
                // Show dialog to add a new model
              },
              child: const Text('Add Model'),
            ),
          ],
        ),
      );
    }

    final filteredModels = _getFilteredModels();

    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'AI Models',
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              _buildProviderFilter(),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            'Manage and monitor your AI models',
            style: Theme.of(context).textTheme.bodyMedium,
          ),
          const SizedBox(height: 16),
          _buildModelStats(),
          const SizedBox(height: 16),
          Expanded(
            child: filteredModels.isEmpty
                ? Center(
                    child: Text(
                      'No models found for the selected provider',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                  )
                : GridView.builder(
                    gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                      crossAxisCount: 2,
                      crossAxisSpacing: 16,
                      mainAxisSpacing: 16,
                      childAspectRatio: 0.8,
                    ),
                    itemCount: filteredModels.length,
                    itemBuilder: (context, index) {
                      final model = filteredModels[index];
                      return _buildModelCard(model);
                    },
                  ),
          ),
        ],
      ),
    );
  }

  Widget _buildProviderFilter() {
    return DropdownButton<ModelProvider?>(
      value: _selectedProvider,
      hint: const Text('All Providers'),
      onChanged: (value) {
        setState(() {
          _selectedProvider = value;
        });
      },
      items: [
        const DropdownMenuItem<ModelProvider?>(
          value: null,
          child: Text('All Providers'),
        ),
        ...ModelProvider.values.map((provider) {
          return DropdownMenuItem<ModelProvider?>(
            value: provider,
            child: Text(_getProviderText(provider)),
          );
        }).toList(),
      ],
    );
  }

  Widget _buildModelStats() {
    final ollamaCount = _models.where((model) => model.provider == ModelProvider.ollama).length;
    final apiCount = _models.where((model) => model.provider != ModelProvider.ollama && model.provider != ModelProvider.local && model.provider != ModelProvider.custom).length;
    final customCount = _models.where((model) => model.provider == ModelProvider.custom).length;
    final trainingCount = _models.where((model) => model.status == ModelStatus.training || model.status == ModelStatus.downloading).length;

    return Row(
      children: [
        Expanded(
          child: _buildStatCard(
            label: 'Ollama',
            value: ollamaCount.toString(),
            color: Colors.blue,
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: _buildStatCard(
            label: 'API',
            value: apiCount.toString(),
            color: Colors.purple,
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: _buildStatCard(
            label: 'Custom',
            value: customCount.toString(),
            color: Colors.green,
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: _buildStatCard(
            label: 'Training',
            value: trainingCount.toString(),
            color: Colors.orange,
          ),
        ),
      ],
    );
  }

  Widget _buildStatCard({
    required String label,
    required String value,
    required Color color,
  }) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        children: [
          Text(
            value,
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            label,
            style: TextStyle(
              fontSize: 12,
              color: color,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildModelCard(AIModel model) {
    final providerColor = _getProviderColor(model.provider);
    final statusColor = _getStatusColor(model.status);
    final typeIcon = _getTypeIcon(model.type);

    return Card(
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: () {
          _showModelDetails(model);
        },
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header with provider color
            Container(
              color: providerColor.withOpacity(0.2),
              padding: const EdgeInsets.all(12),
              child: Row(
                children: [
                  Icon(
                    _getProviderIcon(model.provider),
                    color: providerColor,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      _getProviderText(model.provider),
                      style: TextStyle(
                        color: providerColor,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(
                      color: statusColor,
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(
                      _getStatusText(model.status),
                      style: TextStyle(
                        color: statusColor == Colors.white ? Colors.black : Colors.white,
                        fontSize: 10,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            // Model info
            Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(typeIcon, size: 16),
                      const SizedBox(width: 4),
                      Expanded(
                        child: Text(
                          model.name,
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 16,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    model.description,
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey[700],
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 8),
                  if (model.parameterCount != null) ...[
                    Text(
                      '${model.parameterCount}B parameters',
                      style: const TextStyle(fontSize: 12),
                    ),
                  ],
                  if (model.version != null) ...[
                    Text(
                      'Version: ${model.version}',
                      style: const TextStyle(fontSize: 12),
                    ),
                  ],
                ],
              ),
            ),
            const Spacer(),
            // Progress indicator for downloading/training models
            if (model.status == ModelStatus.downloading &&
                model.metadata != null &&
                model.metadata!.containsKey('download_progress')) ...[
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Downloading: ${model.metadata!['download_progress']}%',
                      style: const TextStyle(fontSize: 12),
                    ),
                    const SizedBox(height: 4),
                    LinearProgressIndicator(
                      value: model.metadata!['download_progress'] / 100,
                      backgroundColor: Colors.grey[200],
                      valueColor: AlwaysStoppedAnimation<Color>(Colors.blue),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 12),
            ] else if (model.status == ModelStatus.training &&
                model.metadata != null &&
                model.metadata!.containsKey('training_progress')) ...[
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Training: ${model.metadata!['training_progress']}%',
                      style: const TextStyle(fontSize: 12),
                    ),
                    const SizedBox(height: 4),
                    LinearProgressIndicator(
                      value: model.metadata!['training_progress'] / 100,
                      backgroundColor: Colors.grey[200],
                      valueColor: AlwaysStoppedAnimation<Color>(Colors.orange),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 12),
            ],
            // Actions
            Padding(
              padding: const EdgeInsets.all(12),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  if (model.status == ModelStatus.available) ...[
                    IconButton(
                      icon: const Icon(Icons.play_arrow),
                      tooltip: 'Use Model',
                      onPressed: () {
                        // Use model
                      },
                    ),
                  ],
                  IconButton(
                    icon: const Icon(Icons.info_outline),
                    tooltip: 'Details',
                    onPressed: () {
                      _showModelDetails(model);
                    },
                  ),
                  IconButton(
                    icon: const Icon(Icons.more_vert),
                    tooltip: 'More',
                    onPressed: () {
                      _showModelActions(model);
                    },
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showModelDetails(AIModel model) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(model.name),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text('ID: ${model.id}'),
              const SizedBox(height: 8),
              Text('Provider: ${_getProviderText(model.provider)}'),
              const SizedBox(height: 8),
              Text('Type: ${_getTypeText(model.type)}'),
              const SizedBox(height: 8),
              Text('Status: ${_getStatusText(model.status)}'),
              const SizedBox(height: 16),
              const Text('Description:'),
              Text(model.description),
              if (model.parameterCount != null) ...[
                const SizedBox(height: 16),
                Text('Parameters: ${model.parameterCount} billion'),
              ],
              if (model.version != null) ...[
                const SizedBox(height: 8),
                Text('Version: ${model.version}'),
              ],
              if (model.benchmarks != null && model.benchmarks!.isNotEmpty) ...[
                const SizedBox(height: 16),
                const Text('Benchmarks:'),
                ...model.benchmarks!.entries.map(
                  (entry) => Text('• ${entry.key.toUpperCase()}: ${entry.value}'),
                ),
              ],
              if (model.metadata != null && model.metadata!.isNotEmpty) ...[
                const SizedBox(height: 16),
                const Text('Metadata:'),
                ...model.metadata!.entries.map(
                  (entry) => Text('• ${entry.key}: ${entry.value}'),
                ),
              ],
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  void _showModelActions(AIModel model) {
    showModalBottomSheet(
      context: context,
      builder: (context) => Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          ListTile(
            leading: const Icon(Icons.info),
            title: const Text('View Details'),
            onTap: () {
              Navigator.pop(context);
              _showModelDetails(model);
            },
          ),
          if (model.status == ModelStatus.available) ...[
            ListTile(
              leading: const Icon(Icons.play_arrow),
              title: const Text('Use Model'),
              onTap: () {
                Navigator.pop(context);
                // Use model
              },
            ),
            ListTile(
              leading: const Icon(Icons.assessment),
              title: const Text('Run Benchmark'),
              onTap: () {
                Navigator.pop(context);
                // Run benchmark
              },
            ),
          ],
          if (model.provider == ModelProvider.ollama) ...[
            ListTile(
              leading: const Icon(Icons.update),
              title: const Text('Update Model'),
              onTap: () {
                Navigator.pop(context);
                // Update model
              },
            ),
          ],
          ListTile(
            leading: const Icon(Icons.delete),
            title: const Text('Delete Model'),
            onTap: () {
              Navigator.pop(context);
              _showDeleteModelDialog(model);
            },
          ),
        ],
      ),
    );
  }

  void _showDeleteModelDialog(AIModel model) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Model'),
        content: Text('Are you sure you want to delete ${model.name}?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              // Delete model
              setState(() {
                _models.removeWhere((m) => m.id == model.id);
              });
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text('${model.name} deleted'),
                  action: SnackBarAction(
                    label: 'Undo',
                    onPressed: () {
                      setState(() {
                        _models.add(model);
                        _models.sort((a, b) => a.id.compareTo(b.id));
                      });
                    },
                  ),
                ),
              );
            },
            child: const Text('Delete'),
          ),
        ],
      ),
    );
  }

  Color _getProviderColor(ModelProvider provider) {
    switch (provider) {
      case ModelProvider.ollama:
        return Colors.blue;
      case ModelProvider.openAI:
        return Colors.green;
      case ModelProvider.anthropic:
        return Colors.purple;
      case ModelProvider.google:
        return Colors.red;
      case ModelProvider.local:
        return Colors.teal;
      case ModelProvider.custom:
        return Colors.orange;
    }
  }

  IconData _getProviderIcon(ModelProvider provider) {
    switch (provider) {
      case ModelProvider.ollama:
        return Icons.smart_toy;
      case ModelProvider.openAI:
        return Icons.auto_awesome;
      case ModelProvider.anthropic:
        return Icons.psychology;
      case ModelProvider.google:
        return Icons.g_mobiledata;
      case ModelProvider.local:
        return Icons.computer;
      case ModelProvider.custom:
        return Icons.build;
    }
  }

  String _getProviderText(ModelProvider provider) {
    switch (provider) {
      case ModelProvider.ollama:
        return 'Ollama';
      case ModelProvider.openAI:
        return 'OpenAI';
      case ModelProvider.anthropic:
        return 'Anthropic';
      case ModelProvider.google:
        return 'Google';
      case ModelProvider.local:
        return 'Local';
      case ModelProvider.custom:
        return 'Custom';
    }
  }

  Color _getStatusColor(ModelStatus status) {
    switch (status) {
      case ModelStatus.available:
        return Colors.green;
      case ModelStatus.downloading:
        return Colors.blue;
      case ModelStatus.training:
        return Colors.orange;
      case ModelStatus.error:
        return Colors.red;
    }
  }

  String _getStatusText(ModelStatus status) {
    switch (status) {
      case ModelStatus.available:
        return 'Available';
      case ModelStatus.downloading:
        return 'Downloading';
      case ModelStatus.training:
        return 'Training';
      case ModelStatus.error:
        return 'Error';
    }
  }

  IconData _getTypeIcon(ModelType type) {
    switch (type) {
      case ModelType.text:
        return Icons.text_fields;
      case ModelType.image:
        return Icons.image;
      case ModelType.audio:
        return Icons.audiotrack;
      case ModelType.multimodal:
        return Icons.layers;
    }
  }

  String _getTypeText(ModelType type) {
    switch (type) {
      case ModelType.text:
        return 'Text';
      case ModelType.image:
        return 'Image';
      case ModelType.audio:
        return 'Audio';
      case ModelType.multimodal:
        return 'Multimodal';
    }
  }
}
