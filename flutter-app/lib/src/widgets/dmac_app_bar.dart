import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:dmac_app/src/services/auth_service.dart';
import 'package:dmac_app/src/utils/app_theme.dart';

/// A consistent app bar for the DMac app
class DMacAppBar extends StatelessWidget implements PreferredSizeWidget {
  final String title;
  final List<Widget>? actions;
  final bool showDrawerButton;
  final VoidCallback? onDrawerButtonPressed;
  final Widget? leading;

  const DMacAppBar({
    Key? key,
    required this.title,
    this.actions,
    this.showDrawerButton = true,
    this.onDrawerButtonPressed,
    this.leading,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final authService = Provider.of<AuthService>(context);
    final user = authService.currentUser;

    return AppBar(
      title: Text(title),
      leading: leading ?? (showDrawerButton ? IconButton(
        icon: const Icon(Icons.menu),
        onPressed: onDrawerButtonPressed ?? () {
          Scaffold.of(context).openDrawer();
        },
      ) : null),
      actions: actions ?? [
        IconButton(
          icon: const Icon(Icons.notifications),
          onPressed: () {
            // Show notifications
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Notifications coming soon!'),
              ),
            );
          },
        ),
        IconButton(
          icon: const Icon(Icons.brightness_6),
          onPressed: () {
            // Toggle theme
            final themeProvider = Provider.of<ThemeProvider>(context, listen: false);
            themeProvider.toggleTheme();
          },
        ),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 8.0),
          child: GestureDetector(
            onTap: () {
              // Show profile
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Profile coming soon!'),
                ),
              );
            },
            child: CircleAvatar(
              radius: 16,
              backgroundImage: user?.avatarUrl != null
                  ? NetworkImage(user!.avatarUrl!)
                  : null,
              child: user?.avatarUrl == null
                  ? const Icon(Icons.person, size: 16)
                  : null,
            ),
          ),
        ),
      ],
    );
  }

  @override
  Size get preferredSize => const Size.fromHeight(kToolbarHeight);
}
