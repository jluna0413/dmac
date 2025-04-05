import 'package:flutter/material.dart';
import 'package:dmac_app/src/widgets/loading_indicator.dart';

/// Tab for displaying analytics and metrics
class AnalyticsTab extends StatefulWidget {
  const AnalyticsTab({Key? key}) : super(key: key);

  @override
  State<AnalyticsTab> createState() => _AnalyticsTabState();
}

class _AnalyticsTabState extends State<AnalyticsTab> {
  bool _isLoading = true;
  Map<String, dynamic> _analyticsData = {};
  String? _error;
  String _timeRange = 'week'; // 'day', 'week', 'month', 'year'

  @override
  void initState() {
    super.initState();
    _loadAnalytics();
  }

  Future<void> _loadAnalytics() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      // Simulate API call delay
      await Future.delayed(const Duration(seconds: 1));

      // Mock data for analytics
      setState(() {
        _analyticsData = {
          'task_completion': {
            'total': 156,
            'completed': 124,
            'completion_rate': 0.79,
            'average_time': '2.3 days',
            'by_agent': {
              'MaCoder': 42,
              'ResearchBot': 35,
              'TaskMaster': 28,
              'DataAnalyst': 12,
              'ContentCreator': 7,
            },
          },
          'agent_performance': {
            'average_score': 86,
            'top_performer': 'MaCoder',
            'top_score': 92,
            'by_agent': {
              'MaCoder': 92,
              'ResearchBot': 87,
              'TaskMaster': 90,
              'DataAnalyst': 78,
              'ContentCreator': 85,
            },
          },
          'model_usage': {
            'total_tokens': 15782345,
            'total_cost': '\$12.45',
            'by_model': {
              'gemma3:12b': 8234567,
              'llama3:8b': 4567890,
              'mistral:7b': 2345678,
              'gpt-4o': 634210,
            },
          },
          'system_metrics': {
            'uptime': '14 days',
            'cpu_usage': 0.45,
            'memory_usage': 0.62,
            'disk_usage': 0.38,
            'api_calls': 12453,
          },
          'learning_progress': {
            'reinforcement_learning': {
              'OpenManus-RL': {
                'episodes': 1245,
                'reward': 0.72,
                'progress': 0.65,
              },
              'DeepSeek-RL': {
                'episodes': 987,
                'reward': 0.68,
                'progress': 0.58,
              },
            },
          },
        };
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = 'Failed to load analytics: ${e.toString()}';
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const LoadingIndicator(message: 'Loading analytics...');
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
              onPressed: _loadAnalytics,
              child: const Text('Retry'),
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
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Analytics & Metrics',
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              _buildTimeRangeSelector(),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            'Performance metrics and system analytics',
            style: Theme.of(context).textTheme.bodyMedium,
          ),
          const SizedBox(height: 16),
          Expanded(
            child: SingleChildScrollView(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildTaskCompletionSection(),
                  const SizedBox(height: 24),
                  _buildAgentPerformanceSection(),
                  const SizedBox(height: 24),
                  _buildModelUsageSection(),
                  const SizedBox(height: 24),
                  _buildSystemMetricsSection(),
                  const SizedBox(height: 24),
                  _buildLearningProgressSection(),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTimeRangeSelector() {
    return SegmentedButton<String>(
      segments: const [
        ButtonSegment<String>(
          value: 'day',
          label: Text('Day'),
        ),
        ButtonSegment<String>(
          value: 'week',
          label: Text('Week'),
        ),
        ButtonSegment<String>(
          value: 'month',
          label: Text('Month'),
        ),
        ButtonSegment<String>(
          value: 'year',
          label: Text('Year'),
        ),
      ],
      selected: {_timeRange},
      onSelectionChanged: (Set<String> selection) {
        setState(() {
          _timeRange = selection.first;
        });
        _loadAnalytics();
      },
    );
  }

  Widget _buildTaskCompletionSection() {
    final taskData = _analyticsData['task_completion'];
    final completionRate = (taskData['completion_rate'] * 100).toInt();
    final agentData = taskData['by_agent'] as Map<String, dynamic>;

    return _buildSectionCard(
      title: 'Task Completion',
      icon: Icons.task_alt,
      color: Colors.blue,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: _buildMetricTile(
                  label: 'Total Tasks',
                  value: taskData['total'].toString(),
                  icon: Icons.list,
                ),
              ),
              Expanded(
                child: _buildMetricTile(
                  label: 'Completed',
                  value: taskData['completed'].toString(),
                  icon: Icons.check_circle,
                ),
              ),
              Expanded(
                child: _buildMetricTile(
                  label: 'Completion Rate',
                  value: '$completionRate%',
                  icon: Icons.percent,
                ),
              ),
              Expanded(
                child: _buildMetricTile(
                  label: 'Avg. Time',
                  value: taskData['average_time'],
                  icon: Icons.timer,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          const Text(
            'Tasks Completed by Agent',
            style: TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 16,
            ),
          ),
          const SizedBox(height: 8),
          SizedBox(
            height: 200,
            child: _buildBarChart(
              data: agentData,
              color: Colors.blue,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAgentPerformanceSection() {
    final performanceData = _analyticsData['agent_performance'];
    final agentData = performanceData['by_agent'] as Map<String, dynamic>;

    return _buildSectionCard(
      title: 'Agent Performance',
      icon: Icons.trending_up,
      color: Colors.green,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: _buildMetricTile(
                  label: 'Average Score',
                  value: '${performanceData['average_score']}%',
                  icon: Icons.score,
                ),
              ),
              Expanded(
                child: _buildMetricTile(
                  label: 'Top Performer',
                  value: performanceData['top_performer'],
                  icon: Icons.emoji_events,
                ),
              ),
              Expanded(
                child: _buildMetricTile(
                  label: 'Top Score',
                  value: '${performanceData['top_score']}%',
                  icon: Icons.star,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          const Text(
            'Performance by Agent',
            style: TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 16,
            ),
          ),
          const SizedBox(height: 8),
          SizedBox(
            height: 200,
            child: _buildBarChart(
              data: agentData,
              color: Colors.green,
              maxValue: 100,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildModelUsageSection() {
    final usageData = _analyticsData['model_usage'];
    final modelData = usageData['by_model'] as Map<String, dynamic>;

    return _buildSectionCard(
      title: 'Model Usage',
      icon: Icons.model_training,
      color: Colors.purple,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: _buildMetricTile(
                  label: 'Total Tokens',
                  value: _formatNumber(usageData['total_tokens']),
                  icon: Icons.token,
                ),
              ),
              Expanded(
                child: _buildMetricTile(
                  label: 'Total Cost',
                  value: usageData['total_cost'],
                  icon: Icons.attach_money,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          const Text(
            'Token Usage by Model',
            style: TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 16,
            ),
          ),
          const SizedBox(height: 8),
          SizedBox(
            height: 200,
            child: _buildPieChart(
              data: modelData,
              colors: const [
                Colors.blue,
                Colors.green,
                Colors.orange,
                Colors.red,
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSystemMetricsSection() {
    final metricsData = _analyticsData['system_metrics'];

    return _buildSectionCard(
      title: 'System Metrics',
      icon: Icons.memory,
      color: Colors.orange,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: _buildMetricTile(
                  label: 'Uptime',
                  value: metricsData['uptime'],
                  icon: Icons.access_time,
                ),
              ),
              Expanded(
                child: _buildMetricTile(
                  label: 'API Calls',
                  value: _formatNumber(metricsData['api_calls']),
                  icon: Icons.api,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          const Text(
            'Resource Usage',
            style: TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 16,
            ),
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              Expanded(
                child: _buildProgressBar(
                  label: 'CPU',
                  value: metricsData['cpu_usage'],
                  color: Colors.red,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: _buildProgressBar(
                  label: 'Memory',
                  value: metricsData['memory_usage'],
                  color: Colors.blue,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: _buildProgressBar(
                  label: 'Disk',
                  value: metricsData['disk_usage'],
                  color: Colors.green,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildLearningProgressSection() {
    final learningData = _analyticsData['learning_progress'];
    final rlData = learningData['reinforcement_learning'] as Map<String, dynamic>;
    final openManusData = rlData['OpenManus-RL'] as Map<String, dynamic>;
    final deepSeekData = rlData['DeepSeek-RL'] as Map<String, dynamic>;

    return _buildSectionCard(
      title: 'Learning Progress',
      icon: Icons.psychology,
      color: Colors.teal,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Reinforcement Learning',
            style: TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 16,
            ),
          ),
          const SizedBox(height: 16),
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: _buildLearningCard(
                  title: 'OpenManus-RL',
                  episodes: openManusData['episodes'],
                  reward: openManusData['reward'],
                  progress: openManusData['progress'],
                  color: Colors.blue,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: _buildLearningCard(
                  title: 'DeepSeek-RL',
                  episodes: deepSeekData['episodes'],
                  reward: deepSeekData['reward'],
                  progress: deepSeekData['progress'],
                  color: Colors.purple,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSectionCard({
    required String title,
    required IconData icon,
    required Color color,
    required Widget child,
  }) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  icon,
                  color: color,
                ),
                const SizedBox(width: 8),
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const Divider(),
            child,
          ],
        ),
      ),
    );
  }

  Widget _buildMetricTile({
    required String label,
    required String value,
    required IconData icon,
  }) {
    return Column(
      children: [
        Icon(
          icon,
          color: Colors.grey[700],
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 16,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: TextStyle(
            color: Colors.grey[600],
            fontSize: 12,
          ),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }

  Widget _buildBarChart({
    required Map<String, dynamic> data,
    required Color color,
    double? maxValue,
  }) {
    final entries = data.entries.toList();
    final max = maxValue ?? entries.map((e) => e.value as num).reduce((a, b) => a > b ? a : b).toDouble();

    return ListView.builder(
      itemCount: entries.length,
      itemBuilder: (context, index) {
        final entry = entries[index];
        final value = entry.value as num;
        final percentage = value / max;

        return Padding(
          padding: const EdgeInsets.only(bottom: 8),
          child: Row(
            children: [
              SizedBox(
                width: 100,
                child: Text(
                  entry.key,
                  style: const TextStyle(fontSize: 12),
                ),
              ),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(
                      height: 16,
                      width: double.infinity,
                      decoration: BoxDecoration(
                        color: Colors.grey[200],
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: FractionallySizedBox(
                        alignment: Alignment.centerLeft,
                        widthFactor: percentage,
                        child: Container(
                          decoration: BoxDecoration(
                            color: color,
                            borderRadius: BorderRadius.circular(8),
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              SizedBox(
                width: 50,
                child: Text(
                  value.toString(),
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
                  ),
                  textAlign: TextAlign.right,
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildPieChart({
    required Map<String, dynamic> data,
    required List<Color> colors,
  }) {
    final entries = data.entries.toList();
    final total = entries.map((e) => e.value as num).reduce((a, b) => a + b);

    return Column(
      children: [
        SizedBox(
          height: 150,
          child: Center(
            child: Stack(
              alignment: Alignment.center,
              children: [
                SizedBox(
                  width: 150,
                  height: 150,
                  child: CustomPaint(
                    painter: _PieChartPainter(
                      data: entries.map((e) => e.value as num).toList(),
                      colors: colors,
                    ),
                  ),
                ),
                Text(
                  _formatNumber(total),
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                  ),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 16),
        Wrap(
          spacing: 16,
          runSpacing: 8,
          children: List.generate(
            entries.length,
            (index) {
              final entry = entries[index];
              final percentage = (entry.value as num) / total * 100;

              return Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Container(
                    width: 12,
                    height: 12,
                    color: colors[index % colors.length],
                  ),
                  const SizedBox(width: 4),
                  Text(
                    '${entry.key}: ${percentage.toStringAsFixed(1)}%',
                    style: const TextStyle(fontSize: 12),
                  ),
                ],
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _buildProgressBar({
    required String label,
    required double value,
    required Color color,
  }) {
    final percentage = (value * 100).toInt();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '$label: $percentage%',
          style: const TextStyle(fontSize: 12),
        ),
        const SizedBox(height: 4),
        LinearProgressIndicator(
          value: value,
          backgroundColor: Colors.grey[200],
          valueColor: AlwaysStoppedAnimation<Color>(color),
        ),
      ],
    );
  }

  Widget _buildLearningCard({
    required String title,
    required int episodes,
    required double reward,
    required double progress,
    required Color color,
  }) {
    return Card(
      color: color.withOpacity(0.1),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
            const SizedBox(height: 8),
            Text('Episodes: $episodes'),
            const SizedBox(height: 4),
            Text('Reward: ${(reward * 100).toInt()}%'),
            const SizedBox(height: 8),
            Text('Progress: ${(progress * 100).toInt()}%'),
            const SizedBox(height: 4),
            LinearProgressIndicator(
              value: progress,
              backgroundColor: Colors.grey[200],
              valueColor: AlwaysStoppedAnimation<Color>(color),
            ),
          ],
        ),
      ),
    );
  }

  String _formatNumber(dynamic number) {
    if (number is int && number >= 1000000) {
      return '${(number / 1000000).toStringAsFixed(1)}M';
    } else if (number is int && number >= 1000) {
      return '${(number / 1000).toStringAsFixed(1)}K';
    } else {
      return number.toString();
    }
  }
}

class _PieChartPainter extends CustomPainter {
  final List<num> data;
  final List<Color> colors;

  _PieChartPainter({
    required this.data,
    required this.colors,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final total = data.reduce((a, b) => a + b);
    final radius = size.width / 2;
    final center = Offset(size.width / 2, size.height / 2);
    
    double startAngle = -90 * (3.14159 / 180); // Start from the top (in radians)
    
    for (int i = 0; i < data.length; i++) {
      final sweepAngle = (data[i] / total) * 2 * 3.14159;
      final paint = Paint()
        ..color = colors[i % colors.length]
        ..style = PaintingStyle.fill;
      
      canvas.drawArc(
        Rect.fromCircle(center: center, radius: radius),
        startAngle,
        sweepAngle,
        true,
        paint,
      );
      
      startAngle += sweepAngle;
    }
    
    // Draw a white circle in the center for a donut chart effect
    canvas.drawCircle(
      center,
      radius * 0.6,
      Paint()..color = Colors.white,
    );
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}
