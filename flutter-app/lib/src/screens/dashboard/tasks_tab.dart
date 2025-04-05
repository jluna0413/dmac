import 'package:flutter/material.dart';
import 'package:dmac_app/src/models/task_model.dart';
import 'package:dmac_app/src/widgets/loading_indicator.dart';

/// Tab for displaying and managing tasks
class TasksTab extends StatefulWidget {
  const TasksTab({Key? key}) : super(key: key);

  @override
  State<TasksTab> createState() => _TasksTabState();
}

class _TasksTabState extends State<TasksTab> {
  bool _isLoading = true;
  List<Task> _tasks = [];
  String? _error;
  TaskFilter _currentFilter = TaskFilter.all;

  @override
  void initState() {
    super.initState();
    _loadTasks();
  }

  Future<void> _loadTasks() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      // Simulate API call delay
      await Future.delayed(const Duration(seconds: 1));

      // Mock data for tasks
      setState(() {
        _tasks = [
          Task(
            id: '1',
            title: 'Implement login screen',
            description: 'Create a login screen with email and password fields',
            status: TaskStatus.completed,
            priority: TaskPriority.high,
            assignedAgentId: '1', // MaCoder
            createdAt: DateTime.now().subtract(const Duration(days: 5)),
            dueDate: DateTime.now().subtract(const Duration(days: 2)),
            completedAt: DateTime.now().subtract(const Duration(days: 3)),
            tags: ['UI', 'Authentication'],
            metadata: {
              'completion_time': '2 days',
              'code_lines': 120,
            },
          ),
          Task(
            id: '2',
            title: 'Research machine learning algorithms',
            description: 'Find the best algorithms for image classification',
            status: TaskStatus.inProgress,
            priority: TaskPriority.medium,
            assignedAgentId: '2', // ResearchBot
            createdAt: DateTime.now().subtract(const Duration(days: 3)),
            dueDate: DateTime.now().add(const Duration(days: 2)),
            completedAt: null,
            tags: ['Research', 'ML'],
            metadata: {
              'progress': 60,
              'sources_found': 15,
            },
          ),
          Task(
            id: '3',
            title: 'Create project timeline',
            description: 'Develop a timeline for the project with milestones',
            status: TaskStatus.todo,
            priority: TaskPriority.high,
            assignedAgentId: '3', // TaskMaster
            createdAt: DateTime.now().subtract(const Duration(days: 1)),
            dueDate: DateTime.now().add(const Duration(days: 3)),
            completedAt: null,
            tags: ['Planning', 'Project Management'],
            metadata: null,
          ),
          Task(
            id: '4',
            title: 'Analyze user feedback data',
            description: 'Process and analyze user feedback from the survey',
            status: TaskStatus.todo,
            priority: TaskPriority.low,
            assignedAgentId: '4', // DataAnalyst
            createdAt: DateTime.now().subtract(const Duration(days: 1)),
            dueDate: DateTime.now().add(const Duration(days: 5)),
            completedAt: null,
            tags: ['Data', 'Analysis'],
            metadata: null,
          ),
          Task(
            id: '5',
            title: 'Write blog post about new features',
            description: 'Create a blog post highlighting the new features',
            status: TaskStatus.blocked,
            priority: TaskPriority.medium,
            assignedAgentId: '5', // ContentCreator
            createdAt: DateTime.now().subtract(const Duration(days: 4)),
            dueDate: DateTime.now().add(const Duration(days: 1)),
            completedAt: null,
            tags: ['Content', 'Marketing'],
            metadata: {
              'blocked_reason': 'Waiting for feature screenshots',
            },
          ),
        ];
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = 'Failed to load tasks: ${e.toString()}';
        _isLoading = false;
      });
    }
  }

  List<Task> _getFilteredTasks() {
    switch (_currentFilter) {
      case TaskFilter.all:
        return _tasks;
      case TaskFilter.todo:
        return _tasks.where((task) => task.status == TaskStatus.todo).toList();
      case TaskFilter.inProgress:
        return _tasks.where((task) => task.status == TaskStatus.inProgress).toList();
      case TaskFilter.completed:
        return _tasks.where((task) => task.status == TaskStatus.completed).toList();
      case TaskFilter.blocked:
        return _tasks.where((task) => task.status == TaskStatus.blocked).toList();
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const LoadingIndicator(message: 'Loading tasks...');
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
              onPressed: _loadTasks,
              child: const Text('Retry'),
            ),
          ],
        ),
      );
    }

    if (_tasks.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.task,
              size: 48,
              color: Colors.grey,
            ),
            const SizedBox(height: 16),
            Text(
              'No Tasks Found',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            const Text('Create your first task to get started'),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () {
                // Show dialog to create a new task
              },
              child: const Text('Create Task'),
            ),
          ],
        ),
      );
    }

    final filteredTasks = _getFilteredTasks();

    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Your Tasks',
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              _buildFilterDropdown(),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            'Manage and track your tasks',
            style: Theme.of(context).textTheme.bodyMedium,
          ),
          const SizedBox(height: 16),
          _buildTaskStats(),
          const SizedBox(height: 16),
          Expanded(
            child: filteredTasks.isEmpty
                ? Center(
                    child: Text(
                      'No ${_currentFilter.toString().split('.').last} tasks found',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                  )
                : ListView.builder(
                    itemCount: filteredTasks.length,
                    itemBuilder: (context, index) {
                      final task = filteredTasks[index];
                      return _buildTaskCard(task);
                    },
                  ),
          ),
        ],
      ),
    );
  }

  Widget _buildFilterDropdown() {
    return DropdownButton<TaskFilter>(
      value: _currentFilter,
      onChanged: (value) {
        if (value != null) {
          setState(() {
            _currentFilter = value;
          });
        }
      },
      items: TaskFilter.values.map((filter) {
        return DropdownMenuItem<TaskFilter>(
          value: filter,
          child: Text(_getFilterText(filter)),
        );
      }).toList(),
    );
  }

  Widget _buildTaskStats() {
    final todoCount = _tasks.where((task) => task.status == TaskStatus.todo).length;
    final inProgressCount = _tasks.where((task) => task.status == TaskStatus.inProgress).length;
    final completedCount = _tasks.where((task) => task.status == TaskStatus.completed).length;
    final blockedCount = _tasks.where((task) => task.status == TaskStatus.blocked).length;

    return Row(
      children: [
        Expanded(
          child: _buildStatCard(
            label: 'To Do',
            value: todoCount.toString(),
            color: Colors.blue,
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: _buildStatCard(
            label: 'In Progress',
            value: inProgressCount.toString(),
            color: Colors.orange,
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: _buildStatCard(
            label: 'Completed',
            value: completedCount.toString(),
            color: Colors.green,
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: _buildStatCard(
            label: 'Blocked',
            value: blockedCount.toString(),
            color: Colors.red,
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

  Widget _buildTaskCard(Task task) {
    final statusColor = _getStatusColor(task.status);
    final priorityColor = _getPriorityColor(task.priority);
    final isOverdue = task.dueDate.isBefore(DateTime.now()) && task.status != TaskStatus.completed;

    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                // Priority indicator
                Container(
                  width: 4,
                  height: 24,
                  decoration: BoxDecoration(
                    color: priorityColor,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
                const SizedBox(width: 8),
                // Task title
                Expanded(
                  child: Text(
                    task.title,
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          decoration: task.status == TaskStatus.completed
                              ? TextDecoration.lineThrough
                              : null,
                        ),
                  ),
                ),
                // Status chip
                Chip(
                  label: Text(
                    _getStatusText(task.status),
                    style: TextStyle(
                      color: statusColor == Colors.white ? Colors.black : Colors.white,
                      fontSize: 12,
                    ),
                  ),
                  backgroundColor: statusColor,
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 0),
                  materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                ),
              ],
            ),
            const SizedBox(height: 8),
            // Description
            Text(
              task.description,
              style: TextStyle(
                color: Colors.grey[700],
              ),
            ),
            const SizedBox(height: 16),
            // Tags
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: task.tags.map((tag) {
                return Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.grey[200],
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    tag,
                    style: const TextStyle(fontSize: 12),
                  ),
                );
              }).toList(),
            ),
            const SizedBox(height: 16),
            // Due date and assigned agent
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    const Icon(Icons.person, size: 16),
                    const SizedBox(width: 4),
                    Text('Agent: ${_getAgentName(task.assignedAgentId)}'),
                  ],
                ),
                Row(
                  children: [
                    Icon(
                      Icons.calendar_today,
                      size: 16,
                      color: isOverdue ? Colors.red : null,
                    ),
                    const SizedBox(width: 4),
                    Text(
                      'Due: ${_formatDate(task.dueDate)}',
                      style: TextStyle(
                        color: isOverdue ? Colors.red : null,
                        fontWeight: isOverdue ? FontWeight.bold : null,
                      ),
                    ),
                  ],
                ),
              ],
            ),
            // Progress indicator for in-progress tasks
            if (task.status == TaskStatus.inProgress &&
                task.metadata != null &&
                task.metadata!.containsKey('progress')) ...[
              const SizedBox(height: 8),
              LinearProgressIndicator(
                value: task.metadata!['progress'] / 100,
                backgroundColor: Colors.grey[200],
                valueColor: AlwaysStoppedAnimation<Color>(Colors.orange),
              ),
              const SizedBox(height: 4),
              Text(
                '${task.metadata!['progress']}% complete',
                style: const TextStyle(fontSize: 12),
              ),
            ],
            // Blocked reason
            if (task.status == TaskStatus.blocked &&
                task.metadata != null &&
                task.metadata!.containsKey('blocked_reason')) ...[
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.red[50],
                  borderRadius: BorderRadius.circular(4),
                  border: Border.all(color: Colors.red[200]!),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.warning, color: Colors.red, size: 16),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'Blocked: ${task.metadata!['blocked_reason']}',
                        style: const TextStyle(color: Colors.red),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Color _getStatusColor(TaskStatus status) {
    switch (status) {
      case TaskStatus.todo:
        return Colors.blue;
      case TaskStatus.inProgress:
        return Colors.orange;
      case TaskStatus.completed:
        return Colors.green;
      case TaskStatus.blocked:
        return Colors.red;
    }
  }

  String _getStatusText(TaskStatus status) {
    switch (status) {
      case TaskStatus.todo:
        return 'To Do';
      case TaskStatus.inProgress:
        return 'In Progress';
      case TaskStatus.completed:
        return 'Completed';
      case TaskStatus.blocked:
        return 'Blocked';
    }
  }

  Color _getPriorityColor(TaskPriority priority) {
    switch (priority) {
      case TaskPriority.low:
        return Colors.green;
      case TaskPriority.medium:
        return Colors.orange;
      case TaskPriority.high:
        return Colors.red;
    }
  }

  String _getFilterText(TaskFilter filter) {
    switch (filter) {
      case TaskFilter.all:
        return 'All Tasks';
      case TaskFilter.todo:
        return 'To Do';
      case TaskFilter.inProgress:
        return 'In Progress';
      case TaskFilter.completed:
        return 'Completed';
      case TaskFilter.blocked:
        return 'Blocked';
    }
  }

  String _formatDate(DateTime date) {
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    final dateToCheck = DateTime(date.year, date.month, date.day);
    final difference = dateToCheck.difference(today).inDays;

    if (difference == 0) {
      return 'Today';
    } else if (difference == 1) {
      return 'Tomorrow';
    } else if (difference == -1) {
      return 'Yesterday';
    } else {
      return '${date.month}/${date.day}/${date.year}';
    }
  }

  String _getAgentName(String agentId) {
    switch (agentId) {
      case '1':
        return 'MaCoder';
      case '2':
        return 'ResearchBot';
      case '3':
        return 'TaskMaster';
      case '4':
        return 'DataAnalyst';
      case '5':
        return 'ContentCreator';
      default:
        return 'Unknown';
    }
  }
}
