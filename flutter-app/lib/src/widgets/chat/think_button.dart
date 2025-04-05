import 'package:flutter/material.dart';

/// Button for deep thinking mode in the chat interface
class ThinkButton extends StatelessWidget {
  final VoidCallback onThinkRequested;

  const ThinkButton({
    Key? key,
    required this.onThinkRequested,
  }) : super(key: key);

  void _showThinkingOptions(BuildContext context) {
    showModalBottomSheet(
      context: context,
      builder: (context) => Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Text(
              'Deep Thinking Options',
              style: Theme.of(context).textTheme.titleLarge,
            ),
          ),
          ListTile(
            leading: const Icon(Icons.psychology),
            title: const Text('Standard Thinking'),
            subtitle: const Text('Think deeply about the problem'),
            onTap: () {
              Navigator.pop(context);
              _startThinking(context, 'Standard');
            },
          ),
          ListTile(
            leading: const Icon(Icons.lightbulb),
            title: const Text('Creative Thinking'),
            subtitle: const Text('Generate creative solutions'),
            onTap: () {
              Navigator.pop(context);
              _startThinking(context, 'Creative');
            },
          ),
          ListTile(
            leading: const Icon(Icons.science),
            title: const Text('Analytical Thinking'),
            subtitle: const Text('Analyze the problem systematically'),
            onTap: () {
              Navigator.pop(context);
              _startThinking(context, 'Analytical');
            },
          ),
          ListTile(
            leading: const Icon(Icons.architecture),
            title: const Text('Strategic Thinking'),
            subtitle: const Text('Develop a strategic approach'),
            onTap: () {
              Navigator.pop(context);
              _startThinking(context, 'Strategic');
            },
          ),
        ],
      ),
    );
  }

  void _startThinking(BuildContext context, String thinkingMode) {
    // Show a thinking dialog with animation
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => _ThinkingDialog(
        thinkingMode: thinkingMode,
        onComplete: () {
          Navigator.pop(context);
          onThinkRequested();
        },
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return IconButton(
      icon: const Icon(Icons.psychology),
      onPressed: () => _showThinkingOptions(context),
      tooltip: 'Deep thinking mode',
    );
  }
}

/// Dialog that shows an animated thinking process
class _ThinkingDialog extends StatefulWidget {
  final String thinkingMode;
  final VoidCallback onComplete;

  const _ThinkingDialog({
    Key? key,
    required this.thinkingMode,
    required this.onComplete,
  }) : super(key: key);

  @override
  State<_ThinkingDialog> createState() => _ThinkingDialogState();
}

class _ThinkingDialogState extends State<_ThinkingDialog> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _progressAnimation;
  late Animation<double> _opacityAnimation;
  int _currentStep = 0;
  final List<String> _thinkingSteps = [
    'Analyzing problem...',
    'Gathering relevant information...',
    'Considering approaches...',
    'Evaluating solutions...',
    'Refining ideas...',
    'Finalizing response...',
  ];

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 6),
    );

    _progressAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(_controller)
      ..addListener(() {
        setState(() {
          // Update the current step based on progress
          _currentStep = (_progressAnimation.value * _thinkingSteps.length).floor();
          if (_currentStep >= _thinkingSteps.length) {
            _currentStep = _thinkingSteps.length - 1;
          }
        });
      });

    _opacityAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _controller,
        curve: const Interval(0.8, 1.0),
      ),
    );

    _controller.forward().then((_) {
      Future.delayed(const Duration(milliseconds: 500), () {
        widget.onComplete();
      });
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text('${widget.thinkingMode} Thinking Mode'),
      content: SizedBox(
        height: 150,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            LinearProgressIndicator(
              value: _progressAnimation.value,
            ),
            const SizedBox(height: 16),
            Text(
              _thinkingSteps[_currentStep],
              style: Theme.of(context).textTheme.bodyLarge,
            ),
            const SizedBox(height: 24),
            Expanded(
              child: Center(
                child: AnimatedBuilder(
                  animation: _opacityAnimation,
                  builder: (context, child) {
                    return Opacity(
                      opacity: _opacityAnimation.value,
                      child: const Icon(
                        Icons.check_circle,
                        color: Colors.green,
                        size: 48,
                      ),
                    );
                  },
                ),
              ),
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () {
            _controller.stop();
            widget.onComplete();
          },
          child: const Text('Skip'),
        ),
      ],
    );
  }
}
