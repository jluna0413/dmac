import 'package:flutter/material.dart';

/// Placeholder assets for the app
class PlaceholderAssets {
  /// Get a placeholder image widget
  static Widget getPlaceholderImage({
    required String name,
    double? width,
    double? height,
    Color color = Colors.blue,
    Color textColor = Colors.white,
  }) {
    return Container(
      width: width,
      height: height,
      color: color,
      child: Center(
        child: Text(
          name,
          style: TextStyle(
            color: textColor,
            fontWeight: FontWeight.bold,
          ),
          textAlign: TextAlign.center,
        ),
      ),
    );
  }
  
  /// Get a placeholder avatar widget
  static Widget getPlaceholderAvatar({
    required String initials,
    double radius = 20,
    Color backgroundColor = Colors.blue,
    Color textColor = Colors.white,
  }) {
    return CircleAvatar(
      radius: radius,
      backgroundColor: backgroundColor,
      child: Text(
        initials,
        style: TextStyle(
          color: textColor,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }
}
