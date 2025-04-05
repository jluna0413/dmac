import 'package:flutter/material.dart';

/// A widget that displays a Material icon as a placeholder
class MaterialIconPlaceholder extends StatelessWidget {
  final IconData icon;
  final double size;
  final Color backgroundColor;
  final Color iconColor;
  final String? label;
  final TextStyle? labelStyle;

  const MaterialIconPlaceholder({
    Key? key,
    required this.icon,
    this.size = 100,
    this.backgroundColor = Colors.blue,
    this.iconColor = Colors.white,
    this.label,
    this.labelStyle,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: size,
          height: size,
          decoration: BoxDecoration(
            color: backgroundColor,
            shape: BoxShape.circle,
          ),
          child: Center(
            child: Icon(
              icon,
              size: size * 0.6,
              color: iconColor,
            ),
          ),
        ),
        if (label != null) ...[
          const SizedBox(height: 8),
          Text(
            label!,
            style: labelStyle ?? TextStyle(
              fontSize: size * 0.16,
              fontWeight: FontWeight.bold,
              color: backgroundColor,
            ),
          ),
        ],
      ],
    );
  }
}

/// A widget that displays a Material icon with a gradient background as a placeholder
class GradientIconPlaceholder extends StatelessWidget {
  final IconData icon;
  final double size;
  final List<Color> gradientColors;
  final Color iconColor;
  final String? label;
  final TextStyle? labelStyle;

  const GradientIconPlaceholder({
    Key? key,
    required this.icon,
    this.size = 100,
    this.gradientColors = const [Colors.blue, Colors.purple],
    this.iconColor = Colors.white,
    this.label,
    this.labelStyle,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: size,
          height: size,
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: gradientColors,
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            shape: BoxShape.circle,
          ),
          child: Center(
            child: Icon(
              icon,
              size: size * 0.6,
              color: iconColor,
            ),
          ),
        ),
        if (label != null) ...[
          const SizedBox(height: 8),
          Text(
            label!,
            style: labelStyle ?? TextStyle(
              fontSize: size * 0.16,
              fontWeight: FontWeight.bold,
              color: gradientColors[0],
            ),
          ),
        ],
      ],
    );
  }
}

/// A widget that displays multiple Material icons as a placeholder for agent capabilities
class AgentCapabilitiesPlaceholder extends StatelessWidget {
  final List<IconData> icons;
  final double size;
  final Color backgroundColor;
  final Color iconColor;
  final String? label;
  final TextStyle? labelStyle;

  const AgentCapabilitiesPlaceholder({
    Key? key,
    required this.icons,
    this.size = 100,
    this.backgroundColor = Colors.blue,
    this.iconColor = Colors.white,
    this.label,
    this.labelStyle,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: size,
          height: size,
          decoration: BoxDecoration(
            color: backgroundColor,
            shape: BoxShape.circle,
          ),
          child: Stack(
            children: [
              // Center icon
              Center(
                child: Icon(
                  icons.first,
                  size: size * 0.4,
                  color: iconColor,
                ),
              ),
              // Surrounding icons
              if (icons.length > 1)
                for (int i = 1; i < icons.length && i < 5; i++)
                  Positioned(
                    top: i == 1 ? size * 0.15 : (i == 2 ? size * 0.65 : (i == 3 ? size * 0.15 : size * 0.65)),
                    left: i == 1 ? size * 0.15 : (i == 2 ? size * 0.15 : (i == 3 ? size * 0.65 : size * 0.65)),
                    child: Icon(
                      icons[i],
                      size: size * 0.25,
                      color: iconColor.withOpacity(0.8),
                    ),
                  ),
            ],
          ),
        ),
        if (label != null) ...[
          const SizedBox(height: 8),
          Text(
            label!,
            style: labelStyle ?? TextStyle(
              fontSize: size * 0.16,
              fontWeight: FontWeight.bold,
              color: backgroundColor,
            ),
          ),
        ],
      ],
    );
  }
}
