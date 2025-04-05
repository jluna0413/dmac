import 'package:flutter/material.dart';
import 'package:dmac_app/src/widgets/device_preview.dart';
import 'package:dmac_app/src/widgets/dmac_app_bar.dart';
import 'package:dmac_app/src/utils/app_theme.dart';

/// Screen for previewing the app on different devices
class DevicePreviewScreen extends StatefulWidget {
  final Widget child;

  const DevicePreviewScreen({
    Key? key,
    required this.child,
  }) : super(key: key);

  @override
  State<DevicePreviewScreen> createState() => _DevicePreviewScreenState();
}

class _DevicePreviewScreenState extends State<DevicePreviewScreen> {
  DeviceType _deviceType = DeviceType.phone;
  DeviceOrientation _orientation = DeviceOrientation.portrait;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: DMacAppBar(
        title: 'Device Preview',
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              setState(() {
                // Reset to default
                _deviceType = DeviceType.phone;
                _orientation = DeviceOrientation.portrait;
              });
            },
            tooltip: 'Reset',
          ),
        ],
      ),
      body: Column(
        children: [
          _buildControls(),
          Expanded(
            child: DevicePreview(
              child: widget.child,
              deviceType: _deviceType,
              orientation: _orientation,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildControls() {
    return Card(
      margin: const EdgeInsets.all(16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Device Settings',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Device Type',
                        style: Theme.of(context).textTheme.titleSmall,
                      ),
                      const SizedBox(height: 8),
                      SegmentedButton<DeviceType>(
                        segments: const [
                          ButtonSegment<DeviceType>(
                            value: DeviceType.phone,
                            label: Text('Phone'),
                            icon: Icon(Icons.smartphone),
                          ),
                          ButtonSegment<DeviceType>(
                            value: DeviceType.tablet,
                            label: Text('Tablet'),
                            icon: Icon(Icons.tablet),
                          ),
                          ButtonSegment<DeviceType>(
                            value: DeviceType.desktop,
                            label: Text('Desktop'),
                            icon: Icon(Icons.desktop_windows),
                          ),
                        ],
                        selected: {_deviceType},
                        onSelectionChanged: (Set<DeviceType> selection) {
                          setState(() {
                            _deviceType = selection.first;
                          });
                        },
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Orientation',
                        style: Theme.of(context).textTheme.titleSmall,
                      ),
                      const SizedBox(height: 8),
                      SegmentedButton<DeviceOrientation>(
                        segments: const [
                          ButtonSegment<DeviceOrientation>(
                            value: DeviceOrientation.portrait,
                            label: Text('Portrait'),
                            icon: Icon(Icons.stay_current_portrait),
                          ),
                          ButtonSegment<DeviceOrientation>(
                            value: DeviceOrientation.landscape,
                            label: Text('Landscape'),
                            icon: Icon(Icons.stay_current_landscape),
                          ),
                        ],
                        selected: {_orientation},
                        onSelectionChanged: (Set<DeviceOrientation> selection) {
                          setState(() {
                            _orientation = selection.first;
                          });
                        },
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                OutlinedButton.icon(
                  onPressed: () {
                    Navigator.pop(context);
                  },
                  icon: const Icon(Icons.close),
                  label: const Text('Close Preview'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
