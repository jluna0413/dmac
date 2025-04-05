import 'package:flutter/material.dart';

/// Widget for previewing the app on different devices
class DevicePreview extends StatelessWidget {
  final Widget child;
  final DeviceType deviceType;
  final DeviceOrientation orientation;

  const DevicePreview({
    Key? key,
    required this.child,
    this.deviceType = DeviceType.phone,
    this.orientation = DeviceOrientation.portrait,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    // Get device dimensions based on type and orientation
    final Size deviceSize = _getDeviceSize();
    final double deviceScale = _getDeviceScale(context);

    return Center(
      child: Transform.scale(
        scale: deviceScale,
        child: Container(
          width: deviceSize.width,
          height: deviceSize.height,
          decoration: BoxDecoration(
            color: Colors.black,
            borderRadius: BorderRadius.circular(
              deviceType == DeviceType.phone ? 32 : 16,
            ),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.3),
                blurRadius: 20,
                offset: const Offset(0, 10),
              ),
            ],
          ),
          child: Stack(
            children: [
              // Device frame
              Positioned.fill(
                child: _buildDeviceFrame(),
              ),
              
              // Screen content
              Positioned(
                left: deviceType == DeviceType.phone ? 12 : 16,
                top: deviceType == DeviceType.phone ? 12 : 16,
                right: deviceType == DeviceType.phone ? 12 : 16,
                bottom: deviceType == DeviceType.phone ? 12 : 16,
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(
                    deviceType == DeviceType.phone ? 24 : 8,
                  ),
                  child: child,
                ),
              ),
              
              // Device UI elements (notch, buttons, etc.)
              if (deviceType == DeviceType.phone) _buildPhoneElements(),
              if (deviceType == DeviceType.tablet) _buildTabletElements(),
            ],
          ),
        ),
      ),
    );
  }

  Size _getDeviceSize() {
    switch (deviceType) {
      case DeviceType.phone:
        return orientation == DeviceOrientation.portrait
            ? const Size(375, 812) // iPhone X-like
            : const Size(812, 375);
      case DeviceType.tablet:
        return orientation == DeviceOrientation.portrait
            ? const Size(768, 1024) // iPad-like
            : const Size(1024, 768);
      case DeviceType.desktop:
        return const Size(1280, 800);
    }
  }

  double _getDeviceScale(BuildContext context) {
    final Size screenSize = MediaQuery.of(context).size;
    final Size deviceSize = _getDeviceSize();
    
    // Calculate scale to fit the device on screen with some padding
    final double widthScale = (screenSize.width - 64) / deviceSize.width;
    final double heightScale = (screenSize.height - 64) / deviceSize.height;
    
    // Use the smaller scale to ensure the device fits on screen
    return widthScale < heightScale ? widthScale : heightScale;
  }

  Widget _buildDeviceFrame() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.black,
        borderRadius: BorderRadius.circular(
          deviceType == DeviceType.phone ? 32 : 16,
        ),
        border: Border.all(
          color: Colors.grey.shade800,
          width: 2,
        ),
      ),
    );
  }

  Widget _buildPhoneElements() {
    return Stack(
      children: [
        // Notch
        if (orientation == DeviceOrientation.portrait)
          Positioned(
            top: 0,
            left: 0,
            right: 0,
            child: Center(
              child: Container(
                margin: const EdgeInsets.only(top: 4),
                width: 150,
                height: 24,
                decoration: BoxDecoration(
                  color: Colors.black,
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
            ),
          ),
        
        // Home indicator
        Positioned(
          bottom: 8,
          left: 0,
          right: 0,
          child: Center(
            child: Container(
              width: 120,
              height: 4,
              decoration: BoxDecoration(
                color: Colors.grey.shade600,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),
        ),
        
        // Volume buttons
        if (orientation == DeviceOrientation.portrait)
          Positioned(
            top: 100,
            left: 0,
            child: Container(
              width: 3,
              height: 60,
              decoration: BoxDecoration(
                color: Colors.grey.shade700,
                borderRadius: BorderRadius.circular(1),
              ),
            ),
          ),
        
        // Power button
        if (orientation == DeviceOrientation.portrait)
          Positioned(
            top: 120,
            right: 0,
            child: Container(
              width: 3,
              height: 40,
              decoration: BoxDecoration(
                color: Colors.grey.shade700,
                borderRadius: BorderRadius.circular(1),
              ),
            ),
          ),
      ],
    );
  }

  Widget _buildTabletElements() {
    return Stack(
      children: [
        // Home button
        if (orientation == DeviceOrientation.portrait)
          Positioned(
            bottom: 8,
            left: 0,
            right: 0,
            child: Center(
              child: Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  border: Border.all(
                    color: Colors.grey.shade600,
                    width: 2,
                  ),
                ),
              ),
            ),
          ),
        
        // Front camera
        if (orientation == DeviceOrientation.portrait)
          Positioned(
            top: 8,
            left: 0,
            right: 0,
            child: Center(
              child: Container(
                width: 8,
                height: 8,
                decoration: BoxDecoration(
                  color: Colors.grey.shade800,
                  shape: BoxShape.circle,
                ),
              ),
            ),
          ),
      ],
    );
  }
}

/// Enum for device types
enum DeviceType {
  phone,
  tablet,
  desktop,
}

/// Enum for device orientations
enum DeviceOrientation {
  portrait,
  landscape,
}
