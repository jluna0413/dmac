import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:dmac_app/src/services/auth_service.dart';
import 'package:dmac_app/src/utils/placeholder_assets.dart';

/// A sliding side menu for navigation
class DMacDrawer extends StatelessWidget {
  final int selectedIndex;
  final Function(int) onItemSelected;

  const DMacDrawer({
    Key? key,
    required this.selectedIndex,
    required this.onItemSelected,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final authService = Provider.of<AuthService>(context);
    final user = authService.currentUser;
    final theme = Theme.of(context);

    return Drawer(
      child: Column(
        children: [
          UserAccountsDrawerHeader(
            accountName: Text(user?.name ?? 'Guest'),
            accountEmail: Text(user?.email ?? ''),
            currentAccountPicture: user?.avatarUrl != null
                ? CircleAvatar(
                    backgroundImage: NetworkImage(user!.avatarUrl!),
                  )
                : PlaceholderAssets.getPlaceholderAvatar(
                    initials: user?.name != null && user!.name.isNotEmpty
                        ? user.name.substring(0, 1).toUpperCase()
                        : 'G',
                    radius: 30,
                  ),
            decoration: BoxDecoration(
              color: theme.colorScheme.primary,
            ),
          ),
          Expanded(
            child: ListView(
              padding: EdgeInsets.zero,
              children: [
                _buildNavItem(
                  context,
                  index: 0,
                  icon: Icons.dashboard,
                  title: 'Dashboard',
                ),
                _buildNavItem(
                  context,
                  index: 1,
                  icon: Icons.smart_toy,
                  title: 'Agents',
                ),
                _buildNavItem(
                  context,
                  index: 2,
                  icon: Icons.chat,
                  title: 'Chat',
                ),
                _buildNavItem(
                  context,
                  index: 3,
                  icon: Icons.web,
                  title: 'WebArena',
                ),
                const Divider(),
                _buildNavItem(
                  context,
                  index: 4,
                  icon: Icons.model_training,
                  title: 'Models',
                ),
                _buildNavItem(
                  context,
                  index: 5,
                  icon: Icons.task,
                  title: 'Tasks',
                ),
                _buildNavItem(
                  context,
                  index: 6,
                  icon: Icons.analytics,
                  title: 'Analytics',
                ),
                const Divider(),
                _buildNavItem(
                  context,
                  index: 7,
                  icon: Icons.settings,
                  title: 'Settings',
                ),
                _buildNavItem(
                  context,
                  index: 8,
                  icon: Icons.help,
                  title: 'Help',
                ),
              ],
            ),
          ),
          const Divider(),
          ListTile(
            leading: const Icon(Icons.logout),
            title: const Text('Logout'),
            onTap: () {
              // Show confirmation dialog
              showDialog(
                context: context,
                builder: (context) => AlertDialog(
                  title: const Text('Logout'),
                  content: const Text('Are you sure you want to logout?'),
                  actions: [
                    TextButton(
                      onPressed: () => Navigator.pop(context),
                      child: const Text('Cancel'),
                    ),
                    TextButton(
                      onPressed: () {
                        Navigator.pop(context);
                        authService.logout();
                      },
                      child: const Text('Logout'),
                    ),
                  ],
                ),
              );
            },
          ),
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Text(
              'DMac AI Agent Swarm v1.0.0',
              style: theme.textTheme.bodySmall,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildNavItem(
    BuildContext context, {
    required int index,
    required IconData icon,
    required String title,
  }) {
    final isSelected = selectedIndex == index;
    final theme = Theme.of(context);

    return ListTile(
      leading: Icon(
        icon,
        color: isSelected ? theme.colorScheme.primary : null,
      ),
      title: Text(
        title,
        style: TextStyle(
          color: isSelected ? theme.colorScheme.primary : null,
          fontWeight: isSelected ? FontWeight.bold : null,
        ),
      ),
      selected: isSelected,
      onTap: () {
        onItemSelected(index);
        Navigator.pop(context);
      },
    );
  }
}
