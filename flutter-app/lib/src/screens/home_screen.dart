import 'package:flutter/material.dart';
import 'package:dmac_app/src/widgets/dmac_app_bar.dart';
import 'package:dmac_app/src/widgets/dmac_drawer.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _selectedIndex = 0;

  @override
  void initState() {
    super.initState();
    // Redirect to the dashboard screen
    Future.microtask(() {
      if (mounted) {
        Navigator.of(context).pushReplacementNamed('/dashboard');
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: const DMacAppBar(
        title: 'DMac AI Agent Swarm',
      ),
      drawer: DMacDrawer(
        selectedIndex: _selectedIndex,
        onItemSelected: (index) {
          setState(() {
            _selectedIndex = index;
          });
        },
      ),
      body: const Center(
        child: CircularProgressIndicator(),
      ),
    );
  }
}

class DashboardTab extends StatelessWidget {
  const DashboardTab({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: Text('Dashboard Tab'),
    );
  }
}

class AgentsTab extends StatelessWidget {
  const AgentsTab({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: Text('Agents Tab'),
    );
  }
}

// ChatTab has been replaced with ChatScreen

class SettingsTab extends StatelessWidget {
  const SettingsTab({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: Text('Settings Tab'),
    );
  }
}
