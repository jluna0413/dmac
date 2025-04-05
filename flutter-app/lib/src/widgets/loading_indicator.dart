import 'package:flutter/material.dart';

/// A visual loading indicator with progress bar
class LoadingIndicator extends StatelessWidget {
  final String message;
  final double? progress;
  final bool isLinear;

  const LoadingIndicator({
    Key? key,
    this.message = 'Loading...',
    this.progress,
    this.isLinear = true,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (isLinear) ...[
            SizedBox(
              width: 200,
              child: progress != null
                  ? LinearProgressIndicator(value: progress)
                  : const LinearProgressIndicator(),
            ),
          ] else ...[
            SizedBox(
              width: 50,
              height: 50,
              child: progress != null
                  ? CircularProgressIndicator(value: progress)
                  : const CircularProgressIndicator(),
            ),
          ],
          const SizedBox(height: 16),
          Text(
            message,
            style: theme.textTheme.bodyLarge,
            textAlign: TextAlign.center,
          ),
          if (progress != null) ...[
            const SizedBox(height: 8),
            Text(
              '${(progress! * 100).toStringAsFixed(1)}%',
              style: theme.textTheme.bodyMedium,
            ),
          ],
        ],
      ),
    );
  }
}

/// A loading overlay that can be shown over the entire screen
class LoadingOverlay extends StatelessWidget {
  final String message;
  final double? progress;
  final bool isLinear;
  final Color? backgroundColor;

  const LoadingOverlay({
    Key? key,
    this.message = 'Loading...',
    this.progress,
    this.isLinear = true,
    this.backgroundColor,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      color: backgroundColor ?? Colors.black.withOpacity(0.5),
      child: LoadingIndicator(
        message: message,
        progress: progress,
        isLinear: isLinear,
      ),
    );
  }
}

/// A widget that shows a loading indicator while waiting for data
class LoadingContainer extends StatelessWidget {
  final bool isLoading;
  final Widget child;
  final String loadingMessage;
  final double? loadingProgress;
  final bool isLinearIndicator;

  const LoadingContainer({
    Key? key,
    required this.isLoading,
    required this.child,
    this.loadingMessage = 'Loading...',
    this.loadingProgress,
    this.isLinearIndicator = true,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        child,
        if (isLoading)
          LoadingOverlay(
            message: loadingMessage,
            progress: loadingProgress,
            isLinear: isLinearIndicator,
          ),
      ],
    );
  }
}
