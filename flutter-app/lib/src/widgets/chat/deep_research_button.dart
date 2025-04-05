import 'package:flutter/material.dart';

/// Button for deep research in the chat interface
class DeepResearchButton extends StatelessWidget {
  final VoidCallback onResearchRequested;

  const DeepResearchButton({
    Key? key,
    required this.onResearchRequested,
  }) : super(key: key);

  void _showResearchOptions(BuildContext context) {
    showModalBottomSheet(
      context: context,
      builder: (context) => Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Text(
              'Deep Research Options',
              style: Theme.of(context).textTheme.titleLarge,
            ),
          ),
          ListTile(
            leading: const Icon(Icons.search),
            title: const Text('Web Search'),
            subtitle: const Text('Search the web for information'),
            onTap: () {
              Navigator.pop(context);
              _showConfirmationDialog(
                context,
                'Web Search',
                'This will search the web for information related to your query. Continue?',
              );
            },
          ),
          ListTile(
            leading: const Icon(Icons.article),
            title: const Text('Academic Research'),
            subtitle: const Text('Search academic papers and journals'),
            onTap: () {
              Navigator.pop(context);
              _showConfirmationDialog(
                context,
                'Academic Research',
                'This will search academic papers and journals related to your query. Continue?',
              );
            },
          ),
          ListTile(
            leading: const Icon(Icons.analytics),
            title: const Text('Data Analysis'),
            subtitle: const Text('Analyze data related to your query'),
            onTap: () {
              Navigator.pop(context);
              _showConfirmationDialog(
                context,
                'Data Analysis',
                'This will analyze data related to your query. Continue?',
              );
            },
          ),
          ListTile(
            leading: const Icon(Icons.public),
            title: const Text('Multi-Source Research'),
            subtitle: const Text('Comprehensive research from multiple sources'),
            onTap: () {
              Navigator.pop(context);
              _showConfirmationDialog(
                context,
                'Multi-Source Research',
                'This will conduct comprehensive research from multiple sources. Continue?',
              );
            },
          ),
        ],
      ),
    );
  }

  void _showConfirmationDialog(
    BuildContext context,
    String title,
    String message,
  ) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(title),
        content: Text(message),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              
              // Show a loading indicator
              showDialog(
                context: context,
                barrierDismissible: false,
                builder: (context) => const AlertDialog(
                  content: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      CircularProgressIndicator(),
                      SizedBox(height: 16),
                      Text('Conducting research...'),
                    ],
                  ),
                ),
              );
              
              // Simulate research delay
              Future.delayed(const Duration(seconds: 2), () {
                // Dismiss the loading indicator
                Navigator.pop(context);
                
                // Call the callback
                onResearchRequested();
              });
            },
            child: const Text('Continue'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return IconButton(
      icon: const Icon(Icons.search),
      onPressed: () => _showResearchOptions(context),
      tooltip: 'Deep research',
    );
  }
}
