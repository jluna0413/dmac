import 'package:flutter/material.dart';
import 'package:dmac_app/src/widgets/dmac_app_bar.dart';
import 'package:dmac_app/src/widgets/dmac_drawer.dart';
import 'package:dmac_app/src/screens/dashboard/agents_tab.dart';
import 'package:dmac_app/src/screens/dashboard/tasks_tab.dart';
import 'package:dmac_app/src/screens/dashboard/models_tab.dart';
import 'package:dmac_app/src/screens/dashboard/analytics_tab.dart';

/// Dashboard screen with tabs for Agents, Tasks, Models, and Analytics
class DashboardScreen extends StatefulWidget {
  const DashboardScreen({Key? key}) : super(key: key);

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  int _selectedIndex = 0;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
    _tabController.addListener(() {
      if (!_tabController.indexIsChanging) {
        setState(() {
          _selectedIndex = _tabController.index;
        });
      }
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: DMacAppBar(
        title: 'Dashboard',
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              // Refresh dashboard data
              setState(() {});
            },
            tooltip: 'Refresh',
          ),
          IconButton(
            icon: const Icon(Icons.admin_panel_settings),
            onPressed: () {
              // Navigate to admin dashboard
              Navigator.of(context).pushNamed('/admin');
            },
            tooltip: 'Admin Panel',
          ),
        ],
      ),
      drawer: DMacDrawer(
        selectedIndex: 0, // Dashboard is selected
        onItemSelected: (index) {
          // Handle drawer item selection
          if (index == 0) {
            // Already on dashboard
            Navigator.pop(context);
          } else if (index == 1) {
            // Navigate to Agents
            _tabController.animateTo(0);
            Navigator.pop(context);
          } else if (index == 2) {
            // Navigate to Chat
            Navigator.of(context).pushReplacementNamed('/chat');
          } else if (index == 3) {
            // Navigate to WebArena
            Navigator.of(context).pushReplacementNamed('/webarena');
          } else if (index == 4) {
            // Navigate to Models
            _tabController.animateTo(2);
            Navigator.pop(context);
          } else if (index == 5) {
            // Navigate to Tasks
            _tabController.animateTo(1);
            Navigator.pop(context);
          } else if (index == 6) {
            // Navigate to Analytics
            _tabController.animateTo(3);
            Navigator.pop(context);
          } else if (index == 7) {
            // Navigate to Settings
            Navigator.of(context).pushReplacementNamed('/settings');
          }
        },
      ),
      body: Column(
        children: [
          TabBar(
            controller: _tabController,
            tabs: const [
              Tab(text: 'Agents'),
              Tab(text: 'Tasks'),
              Tab(text: 'Models'),
              Tab(text: 'Analytics'),
            ],
          ),
          Expanded(
            child: TabBarView(
              controller: _tabController,
              children: const [
                AgentsTab(),
                TasksTab(),
                ModelsTab(),
                AnalyticsTab(),
              ],
            ),
          ),
        ],
      ),
      floatingActionButton: _buildFloatingActionButton(),
    );
  }

  Widget? _buildFloatingActionButton() {
    switch (_selectedIndex) {
      case 0: // Agents tab
        return FloatingActionButton(
          onPressed: () {
            // Show dialog to create a new agent
            _showCreateAgentDialog();
          },
          tooltip: 'Create Agent',
          child: const Icon(Icons.add),
        );
      case 1: // Tasks tab
        return FloatingActionButton(
          onPressed: () {
            // Show dialog to create a new task
            _showCreateTaskDialog();
          },
          tooltip: 'Create Task',
          child: const Icon(Icons.add),
        );
      case 2: // Models tab
        return FloatingActionButton(
          onPressed: () {
            // Show dialog to add a new model
            _showAddModelDialog();
          },
          tooltip: 'Add Model',
          child: const Icon(Icons.add),
        );
      default:
        return null;
    }
  }

  void _showCreateAgentDialog() {
    // Show dialog to create a new agent
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Create Agent'),
        content: const Text('This feature is coming soon!'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  void _showCreateTaskDialog() {
    // Show dialog to create a new task
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Create Task'),
        content: const Text('This feature is coming soon!'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  void _showAddModelDialog() {
    // Show dialog to add a new model
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Add Model'),
        content: const Text('This feature is coming soon!'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }
}
