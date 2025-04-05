import 'package:flutter/material.dart';
import 'package:dmac_app/src/models/agent_model.dart';
import 'package:dmac_app/src/widgets/loading_indicator.dart';
import 'package:dmac_app/src/utils/placeholder_assets.dart';

/// Tab for displaying and managing agents
class AgentsTab extends StatefulWidget {
  const AgentsTab({Key? key}) : super(key: key);

  @override
  State<AgentsTab> createState() => _AgentsTabState();
}

class _AgentsTabState extends State<AgentsTab> {
  bool _isLoading = true;
  List<Agent> _agents = [];
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadAgents();
  }

  Future<void> _loadAgents() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      // Simulate API call delay
      await Future.delayed(const Duration(seconds: 1));

      // Mock data for agents
      setState(() {
        _agents = [
          Agent(
            id: '1',
            name: 'MaCoder',
            description: 'Code assistant agent for development tasks',
            type: AgentType.developer,
            status: AgentStatus.active,
            avatarUrl: null,
            modelId: 'gemma3:12b',
            capabilities: ['Code completion', 'Bug fixing', 'Code review'],
            metadata: {
              'performance_score': 92,
              'training_status': 'completed',
            },
          ),
          Agent(
            id: '2',
            name: 'ResearchBot',
            description: 'Research assistant for gathering information',
            type: AgentType.researcher,
            status: AgentStatus.active,
            avatarUrl: null,
            modelId: 'llama3:8b',
            capabilities: ['Web search', 'Data analysis', 'Report generation'],
            metadata: {
              'performance_score': 87,
              'training_status': 'completed',
            },
          ),
          Agent(
            id: '3',
            name: 'TaskMaster',
            description: 'Task management and coordination agent',
            type: AgentType.coordinator,
            status: AgentStatus.active,
            avatarUrl: null,
            modelId: 'gemma3:12b',
            capabilities: ['Task assignment', 'Progress tracking', 'Resource allocation'],
            metadata: {
              'performance_score': 90,
              'training_status': 'completed',
            },
          ),
          Agent(
            id: '4',
            name: 'DataAnalyst',
            description: 'Data analysis and visualization agent',
            type: AgentType.analyst,
            status: AgentStatus.training,
            avatarUrl: null,
            modelId: 'mistral:7b',
            capabilities: ['Data processing', 'Statistical analysis', 'Chart generation'],
            metadata: {
              'performance_score': 78,
              'training_status': 'in_progress',
              'training_progress': 65,
            },
          ),
          Agent(
            id: '5',
            name: 'ContentCreator',
            description: 'Content creation and editing agent',
            type: AgentType.creator,
            status: AgentStatus.inactive,
            avatarUrl: null,
            modelId: 'llama3:8b',
            capabilities: ['Text generation', 'Content editing', 'SEO optimization'],
            metadata: {
              'performance_score': 85,
              'training_status': 'completed',
            },
          ),
        ];
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = 'Failed to load agents: ${e.toString()}';
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const LoadingIndicator(message: 'Loading agents...');
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
              onPressed: _loadAgents,
              child: const Text('Retry'),
            ),
          ],
        ),
      );
    }

    if (_agents.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.smart_toy,
              size: 48,
              color: Colors.grey,
            ),
            const SizedBox(height: 16),
            Text(
              'No Agents Found',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            const Text('Create your first agent to get started'),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () {
                // Show dialog to create a new agent
              },
              child: const Text('Create Agent'),
            ),
          ],
        ),
      );
    }

    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Your Agents',
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: 8),
          Text(
            'Manage and monitor your AI agents',
            style: Theme.of(context).textTheme.bodyMedium,
          ),
          const SizedBox(height: 16),
          Expanded(
            child: ListView.builder(
              itemCount: _agents.length,
              itemBuilder: (context, index) {
                final agent = _agents[index];
                return _buildAgentCard(agent);
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAgentCard(Agent agent) {
    final statusColor = _getStatusColor(agent.status);
    final statusText = _getStatusText(agent.status);
    final typeIcon = _getTypeIcon(agent.type);
    final typeColor = _getTypeColor(agent.type);

    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                // Agent avatar
                CircleAvatar(
                  radius: 24,
                  backgroundColor: typeColor.withOpacity(0.2),
                  child: Icon(
                    typeIcon,
                    color: typeColor,
                  ),
                ),
                const SizedBox(width: 16),
                // Agent name and status
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        agent.name,
                        style: Theme.of(context).textTheme.titleLarge,
                      ),
                      const SizedBox(height: 4),
                      Row(
                        children: [
                          Container(
                            width: 8,
                            height: 8,
                            decoration: BoxDecoration(
                              color: statusColor,
                              shape: BoxShape.circle,
                            ),
                          ),
                          const SizedBox(width: 4),
                          Text(
                            statusText,
                            style: TextStyle(color: statusColor),
                          ),
                          const SizedBox(width: 8),
                          Text(
                            'Model: ${agent.modelId}',
                            style: Theme.of(context).textTheme.bodySmall,
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                // Actions
                IconButton(
                  icon: const Icon(Icons.more_vert),
                  onPressed: () {
                    _showAgentActions(agent);
                  },
                ),
              ],
            ),
            const SizedBox(height: 16),
            // Description
            Text(agent.description),
            const SizedBox(height: 16),
            // Capabilities
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: agent.capabilities.map((capability) {
                return Chip(
                  label: Text(capability),
                  backgroundColor: typeColor.withOpacity(0.1),
                );
              }).toList(),
            ),
            const SizedBox(height: 16),
            // Performance
            if (agent.metadata != null && agent.metadata!.containsKey('performance_score')) ...[
              Row(
                children: [
                  const Text('Performance: '),
                  const SizedBox(width: 8),
                  _buildPerformanceIndicator(agent.metadata!['performance_score']),
                ],
              ),
            ],
            // Training progress
            if (agent.status == AgentStatus.training &&
                agent.metadata != null &&
                agent.metadata!.containsKey('training_progress')) ...[
              const SizedBox(height: 8),
              Row(
                children: [
                  const Text('Training: '),
                  const SizedBox(width: 8),
                  Expanded(
                    child: LinearProgressIndicator(
                      value: agent.metadata!['training_progress'] / 100,
                      backgroundColor: Colors.grey.withOpacity(0.2),
                      valueColor: AlwaysStoppedAnimation<Color>(typeColor),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Text('${agent.metadata!['training_progress']}%'),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildPerformanceIndicator(int score) {
    Color color;
    if (score >= 90) {
      color = Colors.green;
    } else if (score >= 70) {
      color = Colors.orange;
    } else {
      color = Colors.red;
    }

    return Row(
      children: [
        Container(
          width: 100,
          height: 8,
          decoration: BoxDecoration(
            color: Colors.grey.withOpacity(0.2),
            borderRadius: BorderRadius.circular(4),
          ),
          child: FractionallySizedBox(
            alignment: Alignment.centerLeft,
            widthFactor: score / 100,
            child: Container(
              decoration: BoxDecoration(
                color: color,
                borderRadius: BorderRadius.circular(4),
              ),
            ),
          ),
        ),
        const SizedBox(width: 8),
        Text(
          '$score%',
          style: TextStyle(
            color: color,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }

  void _showAgentActions(Agent agent) {
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
              _showAgentDetails(agent);
            },
          ),
          if (agent.status == AgentStatus.inactive) ...[
            ListTile(
              leading: const Icon(Icons.play_arrow),
              title: const Text('Activate'),
              onTap: () {
                Navigator.pop(context);
                // Activate agent
              },
            ),
          ],
          if (agent.status == AgentStatus.active) ...[
            ListTile(
              leading: const Icon(Icons.pause),
              title: const Text('Deactivate'),
              onTap: () {
                Navigator.pop(context);
                // Deactivate agent
              },
            ),
          ],
          ListTile(
            leading: const Icon(Icons.edit),
            title: const Text('Edit'),
            onTap: () {
              Navigator.pop(context);
              // Edit agent
            },
          ),
          ListTile(
            leading: const Icon(Icons.delete),
            title: const Text('Delete'),
            onTap: () {
              Navigator.pop(context);
              _showDeleteAgentDialog(agent);
            },
          ),
        ],
      ),
    );
  }

  void _showAgentDetails(Agent agent) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(agent.name),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text('ID: ${agent.id}'),
              const SizedBox(height: 8),
              Text('Type: ${_getTypeText(agent.type)}'),
              const SizedBox(height: 8),
              Text('Status: ${_getStatusText(agent.status)}'),
              const SizedBox(height: 8),
              Text('Model: ${agent.modelId}'),
              const SizedBox(height: 16),
              const Text('Description:'),
              Text(agent.description),
              const SizedBox(height: 16),
              const Text('Capabilities:'),
              ...agent.capabilities.map((capability) => Text('• $capability')),
              if (agent.metadata != null && agent.metadata!.isNotEmpty) ...[
                const SizedBox(height: 16),
                const Text('Metadata:'),
                ...agent.metadata!.entries.map(
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

  void _showDeleteAgentDialog(Agent agent) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Agent'),
        content: Text('Are you sure you want to delete ${agent.name}?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              // Delete agent
              setState(() {
                _agents.removeWhere((a) => a.id == agent.id);
              });
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text('${agent.name} deleted'),
                  action: SnackBarAction(
                    label: 'Undo',
                    onPressed: () {
                      setState(() {
                        _agents.add(agent);
                        _agents.sort((a, b) => a.id.compareTo(b.id));
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

  Color _getStatusColor(AgentStatus status) {
    switch (status) {
      case AgentStatus.active:
        return Colors.green;
      case AgentStatus.inactive:
        return Colors.grey;
      case AgentStatus.training:
        return Colors.orange;
      case AgentStatus.error:
        return Colors.red;
    }
  }

  String _getStatusText(AgentStatus status) {
    switch (status) {
      case AgentStatus.active:
        return 'Active';
      case AgentStatus.inactive:
        return 'Inactive';
      case AgentStatus.training:
        return 'Training';
      case AgentStatus.error:
        return 'Error';
    }
  }

  IconData _getTypeIcon(AgentType type) {
    switch (type) {
      case AgentType.developer:
        return Icons.code;
      case AgentType.researcher:
        return Icons.search;
      case AgentType.coordinator:
        return Icons.people;
      case AgentType.analyst:
        return Icons.analytics;
      case AgentType.creator:
        return Icons.create;
      case AgentType.assistant:
        return Icons.assistant;
    }
  }

  Color _getTypeColor(AgentType type) {
    switch (type) {
      case AgentType.developer:
        return Colors.blue;
      case AgentType.researcher:
        return Colors.purple;
      case AgentType.coordinator:
        return Colors.green;
      case AgentType.analyst:
        return Colors.orange;
      case AgentType.creator:
        return Colors.pink;
      case AgentType.assistant:
        return Colors.teal;
    }
  }

  String _getTypeText(AgentType type) {
    switch (type) {
      case AgentType.developer:
        return 'Developer';
      case AgentType.researcher:
        return 'Researcher';
      case AgentType.coordinator:
        return 'Coordinator';
      case AgentType.analyst:
        return 'Analyst';
      case AgentType.creator:
        return 'Creator';
      case AgentType.assistant:
        return 'Assistant';
    }
  }
}
