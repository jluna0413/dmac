import 'package:flutter/material.dart';

/// Button for voice input in the chat interface
class VoiceInputButton extends StatefulWidget {
  final Function(String) onVoiceInput;

  const VoiceInputButton({
    Key? key,
    required this.onVoiceInput,
  }) : super(key: key);

  @override
  State<VoiceInputButton> createState() => _VoiceInputButtonState();
}

class _VoiceInputButtonState extends State<VoiceInputButton> with SingleTickerProviderStateMixin {
  bool _isRecording = false;
  late AnimationController _animationController;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1000),
    )..repeat(reverse: true);
    _animation = Tween<double>(begin: 1.0, end: 1.5).animate(_animationController);
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  void _toggleRecording() {
    setState(() {
      _isRecording = !_isRecording;
    });

    if (_isRecording) {
      // Start recording
      _startRecording();
    } else {
      // Stop recording
      _stopRecording();
    }
  }

  void _startRecording() {
    // In a real implementation, this would start the voice recording
    // For now, we'll just animate the button
    _animationController.repeat(reverse: true);

    // Show a snackbar to indicate recording has started
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Voice recording started. Speak now...'),
        duration: Duration(seconds: 2),
      ),
    );
  }

  void _stopRecording() {
    // In a real implementation, this would stop the recording and process the audio
    _animationController.stop();

    // Simulate processing delay
    Future.delayed(const Duration(milliseconds: 500), () {
      // Simulate voice recognition result
      widget.onVoiceInput('This is a simulated voice input result.');

      // Show a snackbar to indicate recording has stopped
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Voice recording processed'),
            duration: Duration(seconds: 1),
          ),
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _animation,
      builder: (context, child) {
        return Transform.scale(
          scale: _isRecording ? _animation.value : 1.0,
          child: IconButton(
            icon: Icon(
              _isRecording ? Icons.mic : Icons.mic_none,
              color: _isRecording ? Colors.red : Theme.of(context).colorScheme.primary,
            ),
            onPressed: _toggleRecording,
            tooltip: _isRecording ? 'Stop recording' : 'Voice input',
          ),
        );
      },
    );
  }
}
