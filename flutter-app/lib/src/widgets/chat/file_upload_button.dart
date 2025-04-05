import 'package:flutter/material.dart';

/// Button for file uploads in the chat interface
class FileUploadButton extends StatelessWidget {
  final Function(UploadedFile) onFileSelected;

  const FileUploadButton({
    Key? key,
    required this.onFileSelected,
  }) : super(key: key);

  void _showUploadOptions(BuildContext context) {
    showModalBottomSheet(
      context: context,
      builder: (context) => Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          ListTile(
            leading: const Icon(Icons.image),
            title: const Text('Upload Image'),
            onTap: () {
              Navigator.pop(context);
              _uploadImage(context);
            },
          ),
          ListTile(
            leading: const Icon(Icons.insert_drive_file),
            title: const Text('Upload Document'),
            onTap: () {
              Navigator.pop(context);
              _uploadDocument(context);
            },
          ),
          ListTile(
            leading: const Icon(Icons.code),
            title: const Text('Upload Code'),
            onTap: () {
              Navigator.pop(context);
              _uploadCode(context);
            },
          ),
          ListTile(
            leading: const Icon(Icons.video_file),
            title: const Text('Upload Video'),
            onTap: () {
              Navigator.pop(context);
              _uploadVideo(context);
            },
          ),
          ListTile(
            leading: const Icon(Icons.audio_file),
            title: const Text('Upload Audio'),
            onTap: () {
              Navigator.pop(context);
              _uploadAudio(context);
            },
          ),
        ],
      ),
    );
  }

  void _uploadImage(BuildContext context) {
    // In a real implementation, this would open a file picker for images
    // For now, we'll simulate a file selection
    _simulateFileSelection(
      context,
      UploadedFile(
        name: 'example_image.jpg',
        type: FileType.image,
        size: (1024 * 1024 * 2.5).toInt(), // 2.5 MB
      ),
    );
  }

  void _uploadDocument(BuildContext context) {
    // In a real implementation, this would open a file picker for documents
    // For now, we'll simulate a file selection
    _simulateFileSelection(
      context,
      UploadedFile(
        name: 'example_document.pdf',
        type: FileType.document,
        size: (1024 * 1024 * 1.2).toInt(), // 1.2 MB
      ),
    );
  }

  void _uploadCode(BuildContext context) {
    // In a real implementation, this would open a file picker for code files
    // For now, we'll simulate a file selection
    _simulateFileSelection(
      context,
      UploadedFile(
        name: 'example_code.py',
        type: FileType.code,
        size: 1024 * 15, // 15 KB
      ),
    );
  }

  void _uploadVideo(BuildContext context) {
    // In a real implementation, this would open a file picker for videos
    // For now, we'll simulate a file selection
    _simulateFileSelection(
      context,
      UploadedFile(
        name: 'example_video.mp4',
        type: FileType.video,
        size: 1024 * 1024 * 15, // 15 MB
      ),
    );
  }

  void _uploadAudio(BuildContext context) {
    // In a real implementation, this would open a file picker for audio files
    // For now, we'll simulate a file selection
    _simulateFileSelection(
      context,
      UploadedFile(
        name: 'example_audio.mp3',
        type: FileType.audio,
        size: (1024 * 1024 * 3.5).toInt(), // 3.5 MB
      ),
    );
  }

  void _simulateFileSelection(BuildContext context, UploadedFile file) {
    // Show a loading indicator
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => const Center(
        child: CircularProgressIndicator(),
      ),
    );

    // Get a navigator key that we can use later
    final navigatorKey = Navigator.of(context);
    final scaffoldKey = ScaffoldMessenger.of(context);

    // Simulate file processing delay
    Future.delayed(const Duration(seconds: 1), () {
      // Try to dismiss the dialog if it's still showing
      try {
        navigatorKey.pop();
      } catch (e) {
        // Dialog might have been dismissed already
      }

      // Call the callback with the selected file
      onFileSelected(file);

      // Try to show a snackbar
      try {
        scaffoldKey.showSnackBar(
          SnackBar(
            content:
                Text('Uploaded ${file.name} (${_formatFileSize(file.size)})'),
            duration: const Duration(seconds: 2),
          ),
        );
      } catch (e) {
        // Context might not be valid anymore
      }
    });
  }

  String _formatFileSize(int bytes) {
    if (bytes < 1024) {
      return '$bytes B';
    } else if (bytes < 1024 * 1024) {
      return '${(bytes / 1024).toStringAsFixed(1)} KB';
    } else if (bytes < 1024 * 1024 * 1024) {
      return '${(bytes / (1024 * 1024)).toStringAsFixed(1)} MB';
    } else {
      return '${(bytes / (1024 * 1024 * 1024)).toStringAsFixed(1)} GB';
    }
  }

  @override
  Widget build(BuildContext context) {
    return IconButton(
      icon: const Icon(Icons.attach_file),
      onPressed: () => _showUploadOptions(context),
      tooltip: 'Upload file',
    );
  }
}

/// Enum for file types
enum FileType {
  image,
  document,
  code,
  video,
  audio,
}

/// Model class for uploaded files
class UploadedFile {
  final String name;
  final FileType type;
  final int size;

  UploadedFile({
    required this.name,
    required this.type,
    required this.size,
  });
}
