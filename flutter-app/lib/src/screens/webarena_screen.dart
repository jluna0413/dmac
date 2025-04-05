import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:dmac_app/src/services/api_service.dart';
import 'package:dmac_app/src/services/webarena_service.dart';
import 'package:dmac_app/src/models/webarena_models.dart';
import 'package:dmac_app/src/widgets/dmac_app_bar.dart';
import 'package:dmac_app/src/widgets/loading_indicator.dart';
import 'package:dmac_app/src/utils/app_theme.dart';

/// Main screen for WebArena integration
class WebArenaScreen extends StatefulWidget {
  const WebArenaScreen({Key? key}) : super(key: key);

  @override
  State<WebArenaScreen> createState() => _WebArenaScreenState();
}

class _WebArenaScreenState extends State<WebArenaScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  late WebArenaService _webArenaService;
  bool _isLoading = true;
  List<WebArenaTask> _tasks = [];
  List<WebArenaModel> _models = [];
  List<WebArenaRun> _runs = [];
  String? _error;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
    _webArenaService = WebArenaService(Provider.of<ApiService>(context, listen: false));
    _loadData();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadData() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      // Load tasks, models, and runs in parallel
      final results = await Future.wait([
        _webArenaService.getTasks(),
        _webArenaService.getModels(),
        _webArenaService.getRuns(),
      ]);

      setState(() {
        _tasks = results[0] as List<WebArenaTask>;
        _models = results[1] as List<WebArenaModel>;
        _runs = results[2] as List<WebArenaRun>;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = 'Failed to load WebArena data: ${e.toString()}';
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: DMacAppBar(
        title: 'WebArena',
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadData,
          ),
        ],
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
    return Column(
      children: [
        TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'Dashboard'),
            Tab(text: 'Experiments'),
            Tab(text: 'Results'),
            Tab(text: 'Visualizations'),
          ],
        ),
        Expanded(
          child: TabBarView(
            controller: _tabController,
            children: [
              _buildDashboardTab(),
              _buildExperimentsTab(),
              _buildResultsTab(),
              _buildVisualizationsTab(),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildDashboardTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildInfoCard(
            title: 'WebArena',
            content: 'WebArena is a benchmark for evaluating web agents. '
                'You can run experiments with different models and tasks, and visualize the results.',
            icon: Icons.web,
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: _buildStatsCard(
                  title: 'Available Tasks',
                  value: _tasks.length.toString(),
                  icon: Icons.task_alt,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: _buildStatsCard(
                  title: 'Available Models',
                  value: _models.length.toString(),
                  icon: Icons.model_training,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: _buildStatsCard(
                  title: 'Total Runs',
                  value: _runs.length.toString(),
                  icon: Icons.play_circle,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: _buildStatsCard(
                  title: 'Active Runs',
                  value: _runs.where((run) => run.status == 'running').length.toString(),
                  icon: Icons.pending_actions,
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),
          Text(
            'Recent Runs',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const SizedBox(height: 8),
          _buildRecentRunsList(),
          const SizedBox(height: 24),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              ElevatedButton.icon(
                onPressed: () {
                  _tabController.animateTo(1); // Switch to Experiments tab
                },
                icon: const Icon(Icons.add),
                label: const Text('New Experiment'),
              ),
              const SizedBox(width: 16),
              OutlinedButton.icon(
                onPressed: () {
                  _tabController.animateTo(3); // Switch to Visualizations tab
                },
                icon: const Icon(Icons.bar_chart),
                label: const Text('View Visualizations'),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildInfoCard({
    required String title,
    required String content,
    required IconData icon,
  }) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, size: 24),
                const SizedBox(width: 8),
                Text(
                  title,
                  style: Theme.of(context).textTheme.titleLarge,
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(content),
          ],
        ),
      ),
    );
  }

  Widget _buildStatsCard({
    required String title,
    required String value,
    required IconData icon,
  }) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Icon(icon, size: 32, color: Theme.of(context).colorScheme.primary),
            const SizedBox(height: 8),
            Text(
              value,
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                    color: Theme.of(context).colorScheme.primary,
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 4),
            Text(
              title,
              style: Theme.of(context).textTheme.bodyMedium,
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRecentRunsList() {
    if (_runs.isEmpty) {
      return const Card(
        elevation: 1,
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Center(
            child: Text('No runs available. Start a new experiment!'),
          ),
        ),
      );
    }

    // Sort runs by start time (newest first) and take the first 5
    final recentRuns = List<WebArenaRun>.from(_runs)
      ..sort((a, b) => b.startTime.compareTo(a.startTime));
    final displayRuns = recentRuns.take(5).toList();

    return Card(
      elevation: 1,
      child: ListView.separated(
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        itemCount: displayRuns.length,
        separatorBuilder: (context, index) => const Divider(height: 1),
        itemBuilder: (context, index) {
          final run = displayRuns[index];
          return ListTile(
            leading: _getStatusIcon(run.status),
            title: Text('${run.taskName} with ${run.modelName}'),
            subtitle: Text('Run ID: ${run.id}'),
            trailing: Text(
              _getFormattedStatus(run.status),
              style: TextStyle(
                color: _getStatusColor(run.status),
                fontWeight: FontWeight.bold,
              ),
            ),
            onTap: () {
              // Navigate to run details
              _tabController.animateTo(2); // Switch to Results tab
              // TODO: Show details for this specific run
            },
          );
        },
      ),
    );
  }

  Widget _getStatusIcon(String status) {
    switch (status) {
      case 'running':
        return const CircularProgressIndicator(
          strokeWidth: 2,
          valueColor: AlwaysStoppedAnimation<Color>(Colors.blue),
        );
      case 'completed':
        return const Icon(Icons.check_circle, color: Colors.green);
      case 'failed':
        return const Icon(Icons.error, color: Colors.red);
      case 'stopped':
        return const Icon(Icons.stop_circle, color: Colors.orange);
      default:
        return const Icon(Icons.help, color: Colors.grey);
    }
  }

  String _getFormattedStatus(String status) {
    switch (status) {
      case 'running':
        return 'Running';
      case 'completed':
        return 'Completed';
      case 'failed':
        return 'Failed';
      case 'stopped':
        return 'Stopped';
      default:
        return status.substring(0, 1).toUpperCase() + status.substring(1);
    }
  }

  Color _getStatusColor(String status) {
    switch (status) {
      case 'running':
        return Colors.blue;
      case 'completed':
        return Colors.green;
      case 'failed':
        return Colors.red;
      case 'stopped':
        return Colors.orange;
      default:
        return Colors.grey;
    }
  }

  Widget _buildExperimentsTab() {
    // This will be implemented in a separate file
    return const Center(
      child: Text('Experiments tab content will be implemented separately'),
    );
  }

  Widget _buildResultsTab() {
    // This will be implemented in a separate file
    return const Center(
      child: Text('Results tab content will be implemented separately'),
    );
  }

  Widget _buildVisualizationsTab() {
    // This will be implemented in a separate file
    return const Center(
      child: Text('Visualizations tab content will be implemented separately'),
    );
  }
}
