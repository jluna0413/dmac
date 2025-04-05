import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:dmac_app/src/services/api_service.dart';
import 'package:dmac_app/src/services/webarena_service.dart';
import 'package:dmac_app/src/models/webarena_models.dart';
import 'package:dmac_app/src/widgets/dmac_app_bar.dart';
import 'package:dmac_app/src/widgets/loading_indicator.dart';
import 'package:dmac_app/src/utils/app_theme.dart';

/// Screen for running WebArena experiments
class WebArenaExperimentScreen extends StatefulWidget {
  const WebArenaExperimentScreen({Key? key}) : super(key: key);

  @override
  State<WebArenaExperimentScreen> createState() => _WebArenaExperimentScreenState();
}

class _WebArenaExperimentScreenState extends State<WebArenaExperimentScreen> {
  late WebArenaService _webArenaService;
  bool _isLoading = true;
  bool _isRunning = false;
  List<WebArenaTask> _tasks = [];
  List<WebArenaModel> _models = [];
  String? _error;

  // Form values
  WebArenaTask? _selectedTask;
  WebArenaModel? _selectedModel;
  int _numEpisodes = 1;
  int _timeout = 3600; // 1 hour default

  final _formKey = GlobalKey<FormState>();

  @override
  void initState() {
    super.initState();
    _webArenaService = WebArenaService(Provider.of<ApiService>(context, listen: false));
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      // Load tasks and models in parallel
      final results = await Future.wait([
        _webArenaService.getTasks(),
        _webArenaService.getModels(),
      ]);

      setState(() {
        _tasks = results[0] as List<WebArenaTask>;
        _models = results[1] as List<WebArenaModel>;
        
        // Set default selections if available
        if (_tasks.isNotEmpty) {
          _selectedTask = _tasks.first;
        }
        if (_models.isNotEmpty) {
          _selectedModel = _models.first;
        }
        
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = 'Failed to load WebArena data: ${e.toString()}';
        _isLoading = false;
      });
    }
  }

  Future<void> _runExperiment() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() {
      _isRunning = true;
    });

    try {
      final run = await _webArenaService.runExperiment(
        taskName: _selectedTask!.name,
        modelName: _selectedModel!.name,
        numEpisodes: _numEpisodes,
        timeout: _timeout,
      );

      // Show success message
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Experiment started successfully! Run ID: ${run.id}'),
            backgroundColor: Colors.green,
          ),
        );

        // Navigate back or to results
        Navigator.pop(context, run);
      }
    } catch (e) {
      // Show error message
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to start experiment: ${e.toString()}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isRunning = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: const DMacAppBar(
        title: 'New WebArena Experiment',
      ),
      body: _isLoading
          ? const LoadingIndicator(message: 'Loading WebArena data...')
          : _error != null
              ? _buildErrorView()
              : _buildContent(),
    );
  }

  Widget _buildErrorView() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(
            Icons.error_outline,
            size: 64,
            color: Colors.red,
          ),
          const SizedBox(height: 16),
          Text(
            'Error',
            style: Theme.of(context).textTheme.headlineMedium,
          ),
          const SizedBox(height: 8),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 32),
            child: Text(
              _error!,
              textAlign: TextAlign.center,
            ),
          ),
          const SizedBox(height: 24),
          ElevatedButton(
            onPressed: _loadData,
            child: const Text('Retry'),
          ),
        ],
      ),
    );
  }

  Widget _buildContent() {
    return LoadingContainer(
      isLoading: _isRunning,
      loadingMessage: 'Starting experiment...',
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Card(
                elevation: 2,
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'New WebArena Experiment',
                        style: Theme.of(context).textTheme.titleLarge,
                      ),
                      const SizedBox(height: 8),
                      const Text(
                        'Configure and run a new WebArena experiment to evaluate AI models on web-based tasks.',
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 24),
              Text(
                'Task Selection',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              const SizedBox(height: 8),
              _buildTaskSelector(),
              const SizedBox(height: 24),
              Text(
                'Model Selection',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              const SizedBox(height: 8),
              _buildModelSelector(),
              const SizedBox(height: 24),
              Text(
                'Experiment Configuration',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              const SizedBox(height: 8),
              _buildExperimentConfig(),
              const SizedBox(height: 32),
              Center(
                child: ElevatedButton.icon(
                  onPressed: _isRunning ? null : _runExperiment,
                  icon: const Icon(Icons.play_arrow),
                  label: const Text('Run Experiment'),
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildTaskSelector() {
    if (_tasks.isEmpty) {
      return const Card(
        elevation: 1,
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Center(
            child: Text('No tasks available. Please check your WebArena configuration.'),
          ),
        ),
      );
    }

    return Card(
      elevation: 1,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            DropdownButtonFormField<WebArenaTask>(
              value: _selectedTask,
              decoration: const InputDecoration(
                labelText: 'Select Task',
                border: OutlineInputBorder(),
              ),
              items: _tasks.map((task) {
                return DropdownMenuItem<WebArenaTask>(
                  value: task,
                  child: Text(task.name),
                );
              }).toList(),
              onChanged: (value) {
                setState(() {
                  _selectedTask = value;
                });
              },
              validator: (value) {
                if (value == null) {
                  return 'Please select a task';
                }
                return null;
              },
            ),
            if (_selectedTask != null) ...[
              const SizedBox(height: 16),
              Text(
                'Task Description:',
                style: Theme.of(context).textTheme.titleSmall,
              ),
              const SizedBox(height: 4),
              Text(_selectedTask!.description),
              const SizedBox(height: 8),
              Text(
                'Category: ${_selectedTask!.category}',
                style: const TextStyle(fontStyle: FontStyle.italic),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildModelSelector() {
    if (_models.isEmpty) {
      return const Card(
        elevation: 1,
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Center(
            child: Text('No models available. Please check your WebArena configuration.'),
          ),
        ),
      );
    }

    return Card(
      elevation: 1,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            DropdownButtonFormField<WebArenaModel>(
              value: _selectedModel,
              decoration: const InputDecoration(
                labelText: 'Select Model',
                border: OutlineInputBorder(),
              ),
              items: _models.map((model) {
                return DropdownMenuItem<WebArenaModel>(
                  value: model,
                  child: Text(model.name),
                );
              }).toList(),
              onChanged: (value) {
                setState(() {
                  _selectedModel = value;
                });
              },
              validator: (value) {
                if (value == null) {
                  return 'Please select a model';
                }
                return null;
              },
            ),
            if (_selectedModel != null) ...[
              const SizedBox(height: 16),
              Text(
                'Model Description:',
                style: Theme.of(context).textTheme.titleSmall,
              ),
              const SizedBox(height: 4),
              Text(_selectedModel!.description),
              const SizedBox(height: 8),
              Text(
                'Provider: ${_selectedModel!.provider}',
                style: const TextStyle(fontStyle: FontStyle.italic),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildExperimentConfig() {
    return Card(
      elevation: 1,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            TextFormField(
              initialValue: _numEpisodes.toString(),
              decoration: const InputDecoration(
                labelText: 'Number of Episodes',
                border: OutlineInputBorder(),
                helperText: 'Number of times to run the experiment',
              ),
              keyboardType: TextInputType.number,
              validator: (value) {
                if (value == null || value.isEmpty) {
                  return 'Please enter the number of episodes';
                }
                final episodes = int.tryParse(value);
                if (episodes == null || episodes < 1) {
                  return 'Please enter a valid number (minimum 1)';
                }
                return null;
              },
              onChanged: (value) {
                final episodes = int.tryParse(value);
                if (episodes != null && episodes > 0) {
                  setState(() {
                    _numEpisodes = episodes;
                  });
                }
              },
            ),
            const SizedBox(height: 16),
            TextFormField(
              initialValue: _timeout.toString(),
              decoration: const InputDecoration(
                labelText: 'Timeout (seconds)',
                border: OutlineInputBorder(),
                helperText: 'Maximum time to run the experiment',
              ),
              keyboardType: TextInputType.number,
              validator: (value) {
                if (value == null || value.isEmpty) {
                  return 'Please enter the timeout';
                }
                final timeout = int.tryParse(value);
                if (timeout == null || timeout < 60) {
                  return 'Please enter a valid timeout (minimum 60 seconds)';
                }
                return null;
              },
              onChanged: (value) {
                final timeout = int.tryParse(value);
                if (timeout != null && timeout >= 60) {
                  setState(() {
                    _timeout = timeout;
                  });
                }
              },
            ),
          ],
        ),
      ),
    );
  }
}
