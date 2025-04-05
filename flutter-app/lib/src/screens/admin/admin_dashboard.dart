import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:dmac_app/src/models/user_model.dart';
import 'package:dmac_app/src/services/mock_auth_service.dart';
import 'package:dmac_app/src/widgets/dmac_app_bar.dart';
import 'package:dmac_app/src/widgets/loading_indicator.dart';

/// Admin dashboard for user management
class AdminDashboard extends StatefulWidget {
  const AdminDashboard({Key? key}) : super(key: key);

  @override
  State<AdminDashboard> createState() => _AdminDashboardState();
}

class _AdminDashboardState extends State<AdminDashboard> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  
  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
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
        title: 'Admin Dashboard',
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              setState(() {});
            },
            tooltip: 'Refresh',
          ),
        ],
      ),
      body: Column(
        children: [
          TabBar(
            controller: _tabController,
            tabs: const [
              Tab(text: 'Users'),
              Tab(text: 'System'),
              Tab(text: 'Analytics'),
            ],
          ),
          Expanded(
            child: TabBarView(
              controller: _tabController,
              children: const [
                UserManagementTab(),
                SystemManagementTab(),
                AnalyticsTab(),
              ],
            ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          _showAddUserDialog(context);
        },
        tooltip: 'Add User',
        child: const Icon(Icons.add),
      ),
    );
  }
  
  void _showAddUserDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => const AddUserDialog(),
    );
  }
}

/// Tab for user management
class UserManagementTab extends StatelessWidget {
  const UserManagementTab({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final authService = Provider.of<MockAuthService>(context);
    final users = authService.users;
    
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'User Management',
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: 16),
          Expanded(
            child: users.isEmpty
                ? const Center(
                    child: Text('No users found'),
                  )
                : ListView.builder(
                    itemCount: users.length,
                    itemBuilder: (context, index) {
                      final user = users[index];
                      return UserListItem(user: user);
                    },
                  ),
          ),
        ],
      ),
    );
  }
}

/// Tab for system management
class SystemManagementTab extends StatelessWidget {
  const SystemManagementTab({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'System Management',
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: 16),
          Expanded(
            child: ListView(
              children: [
                _buildSystemCard(
                  context,
                  title: 'Database',
                  icon: Icons.storage,
                  status: 'Online',
                  statusColor: Colors.green,
                  details: 'SQLite Database',
                  onTap: () {
                    // Show database management screen
                  },
                ),
                _buildSystemCard(
                  context,
                  title: 'Ollama Integration',
                  icon: Icons.smart_toy,
                  status: 'Connected',
                  statusColor: Colors.green,
                  details: 'Running version 0.1.14',
                  onTap: () {
                    // Show Ollama management screen
                  },
                ),
                _buildSystemCard(
                  context,
                  title: 'WebArena',
                  icon: Icons.web,
                  status: 'Active',
                  statusColor: Colors.green,
                  details: '2 active experiments',
                  onTap: () {
                    // Show WebArena management screen
                  },
                ),
                _buildSystemCard(
                  context,
                  title: 'OpenManus-RL',
                  icon: Icons.psychology,
                  status: 'Training',
                  statusColor: Colors.orange,
                  details: 'Epoch 42/100',
                  onTap: () {
                    // Show OpenManus-RL management screen
                  },
                ),
                _buildSystemCard(
                  context,
                  title: 'DeepSeek-RL',
                  icon: Icons.search,
                  status: 'Idle',
                  statusColor: Colors.blue,
                  details: 'Ready for training',
                  onTap: () {
                    // Show DeepSeek-RL management screen
                  },
                ),
                _buildSystemCard(
                  context,
                  title: 'Langchain',
                  icon: Icons.link,
                  status: 'Connected',
                  statusColor: Colors.green,
                  details: 'Using 3 chains',
                  onTap: () {
                    // Show Langchain management screen
                  },
                ),
                _buildSystemCard(
                  context,
                  title: 'Open Deep Research',
                  icon: Icons.search,
                  status: 'Connected',
                  statusColor: Colors.green,
                  details: 'Ready for research tasks',
                  onTap: () {
                    // Show Open Deep Research management screen
                  },
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildSystemCard(
    BuildContext context, {
    required String title,
    required IconData icon,
    required String status,
    required Color statusColor,
    required String details,
    required VoidCallback onTap,
  }) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: ListTile(
        leading: Icon(icon, size: 32),
        title: Text(title),
        subtitle: Text(details),
        trailing: Chip(
          label: Text(
            status,
            style: TextStyle(
              color: statusColor == Colors.green ? Colors.white : Colors.black87,
            ),
          ),
          backgroundColor: statusColor.withOpacity(0.2),
        ),
        onTap: onTap,
      ),
    );
  }
}

/// Tab for analytics
class AnalyticsTab extends StatelessWidget {
  const AnalyticsTab({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Analytics',
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: 16),
          Expanded(
            child: GridView.count(
              crossAxisCount: 2,
              crossAxisSpacing: 16,
              mainAxisSpacing: 16,
              children: [
                _buildAnalyticsCard(
                  context,
                  title: 'Active Users',
                  value: '12',
                  icon: Icons.people,
                  color: Colors.blue,
                ),
                _buildAnalyticsCard(
                  context,
                  title: 'Active Agents',
                  value: '8',
                  icon: Icons.smart_toy,
                  color: Colors.green,
                ),
                _buildAnalyticsCard(
                  context,
                  title: 'Tasks Completed',
                  value: '156',
                  icon: Icons.task_alt,
                  color: Colors.purple,
                ),
                _buildAnalyticsCard(
                  context,
                  title: 'Models Trained',
                  value: '5',
                  icon: Icons.model_training,
                  color: Colors.orange,
                ),
                _buildAnalyticsCard(
                  context,
                  title: 'API Calls',
                  value: '1,243',
                  icon: Icons.api,
                  color: Colors.red,
                ),
                _buildAnalyticsCard(
                  context,
                  title: 'Storage Used',
                  value: '2.4 GB',
                  icon: Icons.storage,
                  color: Colors.teal,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildAnalyticsCard(
    BuildContext context, {
    required String title,
    required String value,
    required IconData icon,
    required Color color,
  }) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              icon,
              size: 48,
              color: color,
            ),
            const SizedBox(height: 16),
            Text(
              value,
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: color,
                  ),
            ),
            const SizedBox(height: 8),
            Text(
              title,
              style: Theme.of(context).textTheme.titleMedium,
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}

/// Widget for displaying a user in a list
class UserListItem extends StatelessWidget {
  final User user;
  
  const UserListItem({
    Key? key,
    required this.user,
  }) : super(key: key);
  
  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: _getRoleColor(user.role),
          child: Text(
            user.name.isNotEmpty ? user.name[0].toUpperCase() : '?',
            style: const TextStyle(color: Colors.white),
          ),
        ),
        title: Text(user.name),
        subtitle: Text(user.email),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Chip(
              label: Text(
                _getRoleName(user.role),
                style: const TextStyle(color: Colors.white),
              ),
              backgroundColor: _getRoleColor(user.role),
            ),
            IconButton(
              icon: const Icon(Icons.edit),
              onPressed: () {
                _showEditUserDialog(context, user);
              },
            ),
            IconButton(
              icon: const Icon(Icons.delete),
              onPressed: () {
                _showDeleteUserDialog(context, user);
              },
            ),
          ],
        ),
        onTap: () {
          _showUserDetailsDialog(context, user);
        },
      ),
    );
  }
  
  Color _getRoleColor(UserRole role) {
    switch (role) {
      case UserRole.admin:
        return Colors.red;
      case UserRole.developer:
        return Colors.purple;
      case UserRole.user:
        return Colors.blue;
    }
  }
  
  String _getRoleName(UserRole role) {
    switch (role) {
      case UserRole.admin:
        return 'Admin';
      case UserRole.developer:
        return 'Developer';
      case UserRole.user:
        return 'User';
    }
  }
  
  void _showEditUserDialog(BuildContext context, User user) {
    showDialog(
      context: context,
      builder: (context) => EditUserDialog(user: user),
    );
  }
  
  void _showDeleteUserDialog(BuildContext context, User user) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete User'),
        content: Text('Are you sure you want to delete ${user.name}?'),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
            },
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              final authService = Provider.of<MockAuthService>(context, listen: false);
              authService.deleteUser(user.id);
              Navigator.of(context).pop();
            },
            child: const Text('Delete'),
          ),
        ],
      ),
    );
  }
  
  void _showUserDetailsDialog(BuildContext context, User user) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(user.name),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildDetailRow('ID', user.id),
            _buildDetailRow('Email', user.email),
            _buildDetailRow('Role', _getRoleName(user.role)),
            if (user.metadata != null) ...[
              const SizedBox(height: 16),
              const Text('Metadata:'),
              const SizedBox(height: 8),
              Text(user.metadata.toString()),
            ],
          ],
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
            },
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }
  
  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '$label: ',
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
          Expanded(child: Text(value)),
        ],
      ),
    );
  }
}

/// Dialog for adding a new user
class AddUserDialog extends StatefulWidget {
  const AddUserDialog({Key? key}) : super(key: key);
  
  @override
  State<AddUserDialog> createState() => _AddUserDialogState();
}

class _AddUserDialogState extends State<AddUserDialog> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _emailController = TextEditingController();
  UserRole _selectedRole = UserRole.user;
  bool _isLoading = false;
  String? _errorMessage;
  
  @override
  void dispose() {
    _nameController.dispose();
    _emailController.dispose();
    super.dispose();
  }
  
  Future<void> _addUser() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }
    
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });
    
    try {
      final authService = Provider.of<MockAuthService>(context, listen: false);
      await authService.createUser(
        email: _emailController.text.trim(),
        name: _nameController.text.trim(),
        role: _selectedRole,
      );
      
      if (mounted) {
        Navigator.of(context).pop();
      }
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
      });
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Add User'),
      content: LoadingContainer(
        isLoading: _isLoading,
        loadingMessage: 'Adding user...',
        child: Form(
          key: _formKey,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              if (_errorMessage != null) ...[
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.red.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    _errorMessage!,
                    style: const TextStyle(color: Colors.red),
                  ),
                ),
                const SizedBox(height: 16),
              ],
              TextFormField(
                controller: _nameController,
                decoration: const InputDecoration(
                  labelText: 'Name',
                  border: OutlineInputBorder(),
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please enter a name';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _emailController,
                decoration: const InputDecoration(
                  labelText: 'Email',
                  border: OutlineInputBorder(),
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please enter an email';
                  }
                  if (!RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$').hasMatch(value)) {
                    return 'Please enter a valid email';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),
              DropdownButtonFormField<UserRole>(
                value: _selectedRole,
                decoration: const InputDecoration(
                  labelText: 'Role',
                  border: OutlineInputBorder(),
                ),
                items: UserRole.values.map((role) {
                  return DropdownMenuItem<UserRole>(
                    value: role,
                    child: Text(_getRoleName(role)),
                  );
                }).toList(),
                onChanged: (value) {
                  if (value != null) {
                    setState(() {
                      _selectedRole = value;
                    });
                  }
                },
              ),
            ],
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: () {
            Navigator.of(context).pop();
          },
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: _isLoading ? null : _addUser,
          child: const Text('Add'),
        ),
      ],
    );
  }
  
  String _getRoleName(UserRole role) {
    switch (role) {
      case UserRole.admin:
        return 'Admin';
      case UserRole.developer:
        return 'Developer';
      case UserRole.user:
        return 'User';
    }
  }
}

/// Dialog for editing a user
class EditUserDialog extends StatefulWidget {
  final User user;
  
  const EditUserDialog({
    Key? key,
    required this.user,
  }) : super(key: key);
  
  @override
  State<EditUserDialog> createState() => _EditUserDialogState();
}

class _EditUserDialogState extends State<EditUserDialog> {
  final _formKey = GlobalKey<FormState>();
  late TextEditingController _nameController;
  late TextEditingController _emailController;
  late UserRole _selectedRole;
  bool _isLoading = false;
  String? _errorMessage;
  
  @override
  void initState() {
    super.initState();
    _nameController = TextEditingController(text: widget.user.name);
    _emailController = TextEditingController(text: widget.user.email);
    _selectedRole = widget.user.role;
  }
  
  @override
  void dispose() {
    _nameController.dispose();
    _emailController.dispose();
    super.dispose();
  }
  
  Future<void> _updateUser() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }
    
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });
    
    try {
      final authService = Provider.of<MockAuthService>(context, listen: false);
      final updatedUser = widget.user.copyWith(
        name: _nameController.text.trim(),
        email: _emailController.text.trim(),
        role: _selectedRole,
      );
      
      await authService.updateUser(updatedUser);
      
      if (mounted) {
        Navigator.of(context).pop();
      }
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
      });
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Edit User'),
      content: LoadingContainer(
        isLoading: _isLoading,
        loadingMessage: 'Updating user...',
        child: Form(
          key: _formKey,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              if (_errorMessage != null) ...[
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.red.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    _errorMessage!,
                    style: const TextStyle(color: Colors.red),
                  ),
                ),
                const SizedBox(height: 16),
              ],
              TextFormField(
                controller: _nameController,
                decoration: const InputDecoration(
                  labelText: 'Name',
                  border: OutlineInputBorder(),
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please enter a name';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _emailController,
                decoration: const InputDecoration(
                  labelText: 'Email',
                  border: OutlineInputBorder(),
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please enter an email';
                  }
                  if (!RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$').hasMatch(value)) {
                    return 'Please enter a valid email';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),
              DropdownButtonFormField<UserRole>(
                value: _selectedRole,
                decoration: const InputDecoration(
                  labelText: 'Role',
                  border: OutlineInputBorder(),
                ),
                items: UserRole.values.map((role) {
                  return DropdownMenuItem<UserRole>(
                    value: role,
                    child: Text(_getRoleName(role)),
                  );
                }).toList(),
                onChanged: (value) {
                  if (value != null) {
                    setState(() {
                      _selectedRole = value;
                    });
                  }
                },
              ),
            ],
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: () {
            Navigator.of(context).pop();
          },
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: _isLoading ? null : _updateUser,
          child: const Text('Save'),
        ),
      ],
    );
  }
  
  String _getRoleName(UserRole role) {
    switch (role) {
      case UserRole.admin:
        return 'Admin';
      case UserRole.developer:
        return 'Developer';
      case UserRole.user:
        return 'User';
    }
  }
}
